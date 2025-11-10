"""脚本执行模块"""

import asyncio
import contextvars
import importlib.util
import inspect
import sys
import threading
from pathlib import Path
from typing import List, Optional

import snailjob as sj

from .config import PlaywrightExecutorConfig
from .exceptions import ScriptExecutionError
from .logger import logger


class ScriptRunner:
    """脚本执行器（通过方法调用）"""

    def __init__(self, config: PlaywrightExecutorConfig):
        self.config = config
        self.service_path = config.get_service_path()
        self._result: any = None  # 可以是任意类型的返回值
        self._exception: Optional[Exception] = None
        self._loop: Optional[asyncio.AbstractEventLoop] = None  # 保存事件循环引用
        self._task: Optional[asyncio.Task] = None  # 保存异步任务引用

    def run_main_script(
        self, site_packages_paths: List[str], job_id: int, task_batch_id: int, extra_params: dict = None
    ) -> tuple[bool, any]:
        """
        动态导入 main.py 并调用 run() 方法

        Args:
            site_packages_paths: 虚拟环境的 site-packages 路径列表
            job_id: 任务ID（用于日志追溯）
            task_batch_id: 任务批次ID（用于中断检测）
            extra_params: 传递给 run() 方法的额外参数

        Returns:
            tuple[bool, any]: (是否成功, 返回值)
                - 成功: (True, run() 的返回值)
                - 失败: (False, 错误信息或 None)
        """
        main_py = self.service_path / "main.py"

        if not main_py.exists():
            raise ScriptExecutionError(f"main.py 不存在: {main_py}")

        logger.REMOTE.info(f"准备执行脚本: {main_py}")

        # 保存原始 sys.path
        original_sys_path = sys.path.copy()

        try:
            # 修改 sys.path，添加虚拟环境和需求文件夹路径
            self._setup_python_path(site_packages_paths)

            # 动态导入 main.py 模块
            module = self._import_main_module(main_py)

            # 验证 run 方法存在
            if not hasattr(module, "run"):
                raise ScriptExecutionError(f"main.py 中未找到 run() 方法: {main_py}")

            run_func = getattr(module, "run")

            # 在独立线程中执行 run() 方法，支持超时和中断
            success, result = self._execute_with_timeout(
                run_func=run_func, job_id=job_id, task_batch_id=task_batch_id, extra_params=extra_params or {}
            )

            if success:
                logger.REMOTE.info(f"脚本执行完成，返回结果类型: {type(result).__name__}")
            else:
                logger.REMOTE.error(f"脚本执行失败: {result}")
            
            return success, result

        finally:
            # 恢复原始 sys.path
            sys.path = original_sys_path
            logger.REMOTE.info(f"已恢复 sys.path")

    def _setup_python_path(self, site_packages_paths: List[str]) -> None:
        """
        设置 Python 路径

        优先级（从高到低）:
            1. 虚拟环境的 site-packages
            2. 业务逻辑文件夹路径
            3. Git 仓库根目录
        """
        # 1. 添加虚拟环境的 site-packages（放在前面，优先级高）
        for path in reversed(site_packages_paths):
            if path not in sys.path:
                sys.path.insert(0, path)
                logger.LOCAL.info(f"添加到 sys.path: {path}")

        # 2. 添加业务逻辑文件夹路径（让 main.py 可以导入同目录的其他模块）
        service_path_str = str(self.service_path)
        if service_path_str not in sys.path:
            sys.path.insert(0, service_path_str)
            logger.LOCAL.info(f"添加到 sys.path: {service_path_str}")

        # 3. 添加 Git 仓库根目录（让 main.py 可以导入通用工具类）
        repo_path_str = str(self.config.git_repo_dir)
        if repo_path_str not in sys.path:
            sys.path.insert(0, repo_path_str)
            logger.LOCAL.info(f"添加到 sys.path: {repo_path_str}")

    def _import_main_module(self, main_py_path: Path):
        """动态导入 main.py 模块"""
        try:
            # 使用 importlib.util 动态导入模块
            # 模块名需要唯一，避免缓存冲突
            module_name = (
                f"playwright_service_{self.config.service_folder.replace('/', '_').replace('.', '_')}"
            )

            logger.LOCAL.info(f"导入模块: {module_name} from {main_py_path}")

            spec = importlib.util.spec_from_file_location(module_name, main_py_path)
            if spec is None or spec.loader is None:
                raise ScriptExecutionError(f"无法加载模块: {main_py_path}")

            module = importlib.util.module_from_spec(spec)

            # 将模块添加到 sys.modules（避免重复导入）
            sys.modules[module_name] = module

            # 执行模块
            spec.loader.exec_module(module)

            logger.LOCAL.info(f"模块导入成功: {module_name}")
            return module

        except Exception as e:
            raise ScriptExecutionError(f"导入 main.py 失败: {str(e)}")

    def _execute_with_timeout(
        self, run_func, job_id: int, task_batch_id: int, extra_params: dict
    ) -> tuple[bool, any]:
        """
        在独立线程中执行 run() 方法，支持超时和中断
        
        自动检测并支持同步和异步函数：
        - 同步函数：直接调用
        - 异步函数：在新的事件循环中运行

        注意:
            Python 线程无法强制终止，如果脚本长时间运行，
            建议在需求方的 run() 方法中也定期检查中断信号
        
        Returns:
            tuple[bool, any]: (是否成功, 返回值/错误信息)
        """
        self._result = None
        self._exception = None
        self._loop = None
        self._task = None
        
        # 检查是否是异步函数
        is_async = inspect.iscoroutinefunction(run_func)
        if is_async:
            logger.REMOTE.info("检测到异步 run() 函数，将在新事件循环中执行")
        else:
            logger.REMOTE.info("检测到同步 run() 函数")

        # 复制当前线程的 context，用于在新线程中继承（解决 ContextVar 跨线程问题）
        ctx = contextvars.copy_context()

        def target():
            """线程执行目标"""
            try:
                if is_async:
                    # 异步函数：在新的事件循环中运行
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    self._loop = loop  # 保存循环引用，用于中断
                    try:
                        # 创建任务而不是直接 run_until_complete
                        coro = run_func(job_id=job_id, task_batch_id=task_batch_id, extra_params=extra_params)
                        task = loop.create_task(coro)
                        self._task = task  # 保存任务引用，用于中断
                        result = loop.run_until_complete(task)
                        self._result = result
                    except asyncio.CancelledError:
                        logger.REMOTE.warning("异步任务被取消")
                        self._exception = Exception("任务被中断")
                    except Exception as e:
                        raise
                    finally:
                        loop.close()
                        self._loop = None
                        self._task = None
                else:
                    # 同步函数：直接调用
                    result = run_func(job_id=job_id, task_batch_id=task_batch_id, extra_params=extra_params)
                    self._result = result
            except Exception as e:
                self._exception = e
                logger.REMOTE.error(f"脚本执行失败: {str(e)}")
                raise

        # 创建并启动线程（在复制的 context 中运行）
        thread = threading.Thread(target=lambda: ctx.run(target), daemon=True)
        thread.start()

        # 等待线程完成（带超时和中断检测）
        timeout = self.config.script_timeout
        check_interval = 1  # 每秒检查一次
        elapsed = 0

        while thread.is_alive() and elapsed < timeout:
            # 检查是否有中断信号
            if sj.ThreadPoolCache.event_is_set(task_batch_id):
                logger.REMOTE.warning("检测到任务中断信号")
                
                # 如果是异步任务，尝试取消它
                if is_async and self._loop is not None and self._task is not None:
                    logger.REMOTE.info("尝试取消异步任务...")
                    try:
                        # 使用线程安全的方式在事件循环中取消任务
                        self._loop.call_soon_threadsafe(self._task.cancel)
                        logger.REMOTE.info("已发送取消信号到异步任务")
                    except Exception as e:
                        logger.REMOTE.error(f"取消异步任务失败: {str(e)}")
                else:
                    logger.REMOTE.warning(
                        "同步任务中断需要脚本自行检查（建议在脚本中使用 sj.ThreadPoolCache.event_is_set 检查）"
                    )
                
                # 继续等待一段时间让脚本有机会响应
                thread.join(timeout=10)
                if thread.is_alive():
                    logger.REMOTE.error("脚本未响应中断信号，任务可能仍在后台运行")
                return False, "任务被中断"

            thread.join(timeout=check_interval)
            elapsed += check_interval

        # 检查超时
        if thread.is_alive():
            error_msg = f"脚本执行超时 ({timeout}秒)"
            logger.REMOTE.error(error_msg)
            raise ScriptExecutionError(error_msg)

        # 检查异常
        if self._exception is not None:
            error_msg = f"脚本执行过程中发生异常: {str(self._exception)}"
            logger.REMOTE.error(error_msg)
            raise ScriptExecutionError(error_msg)

        # 正常执行完成，返回结果（可以是任意类型，包括 None）
        logger.REMOTE.info(f"脚本正常执行完成，返回值: {self._result}")
        return True, self._result

