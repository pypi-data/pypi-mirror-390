"""Playwright 执行器主模块"""

import json
from pathlib import Path
from typing import Any

from snailjob import *

from .config import PlaywrightExecutorConfig
from .env_manager import EnvManager
from .exceptions import (
    DependencyInstallError,
    GitOperationError,
    PlaywrightExecutorError,
    RequirementNotFoundError,
    ScriptExecutionError,
)
from .git_manager import GitManager
from .logger import logger
from .response import ExecutorResponse
from .script_runner import ScriptRunner


@job("PlaywrightExecutor")
def playwright_executor(args: JobArgs) -> ExecuteResult:
    """
    Playwright 通用执行器

    参数格式（job_params）:
    {
        "service_folder": "demo_service",  // 只需写子文件夹名，自动拼接为 app/services/demo_service
        "branch": "main",  // 可选，默认 main
        "workspace_root": "/workspace",  // 可选，默认 /workspace
        "script_timeout": 1800,  // 可选，默认1800秒（30分钟）
        "extra_params": {  // 可选，传递给 run() 方法的额外参数
            "env": "test",
            "target_url": "https://example.com"
        }
    }

    环境变量配置（必需）:
    - GIT_REPO_URL: Git 仓库地址（如 https://github.com/org/project.git）
    - GIT_TOKEN: Git Token（用于仓库认证）

    注意:
    - service_folder 参数只需要写子文件夹名称（如：demo_service）
    - 系统会自动拼接父目录 app/services/，最终路径为：app/services/demo_service

    Returns:
        ExecuteResult: 执行成功或失败的结果
    """
    try:
        # ========== 1. 解析参数 ==========
        # 设置 job_id 和 task_batch_id 到上下文，后续所有日志自动带前缀
        logger.set_job_and_task_batch_id(job_id=args.job_id, task_batch_id=args.task_batch_id)

        logger.REMOTE.info("=" * 60)
        logger.REMOTE.info("🚀 Playwright 执行器启动")
        logger.REMOTE.info(f"任务详情: {vars(args)}")

        # ========== 2. 创建配置 ==========
        params = _parse_job_params(args.job_params)
        config = _create_config(params)

        logger.REMOTE.info(f"📁 业务逻辑文件夹: {config.service_folder}")
        logger.REMOTE.info(f"📂 完整路径: {config.get_service_path()}")
        logger.REMOTE.info(f"🌿 Git 分支: {config.git_branch}")
        logger.REMOTE.info(f"💼 工作目录: {config.workspace_root}")
        logger.REMOTE.info(f"⏱️ 超时时间: {config.script_timeout}秒")

        # ========== 3. Git 操作：克隆/更新仓库 ==========
        logger.REMOTE.info("-" * 60)
        logger.REMOTE.info("步骤 1/3: Git 仓库管理")
        git_manager = GitManager(config)
        git_manager.ensure_repository()

        # ========== 4. 环境管理：创建虚拟环境、安装依赖 ==========
        logger.REMOTE.info("-" * 60)
        logger.REMOTE.info("步骤 2/3: 虚拟环境管理")
        env_manager = EnvManager(config)
        env_manager.ensure_environment()

        # ========== 5. 执行脚本（方法调用） ==========
        logger.REMOTE.info("-" * 60)
        logger.REMOTE.info("步骤 3/3: 执行脚本")
        script_runner = ScriptRunner(config)
        site_packages_paths = env_manager.get_site_packages_paths()

        success, result = script_runner.run_main_script(
            site_packages_paths=site_packages_paths,
            job_id=args.job_id,
            task_batch_id=args.task_batch_id,
            extra_params=params.get("extra_params"),
        )

        # ========== 6. 判断执行结果 ==========
        logger.REMOTE.info("-" * 60)
        if success:
            logger.REMOTE.info("✅ 脚本执行成功")
            # 使用 ExecutorResponse 包装结果
            response = ExecutorResponse.success(
                message="脚本执行成功",
                data=result
            )
            logger.REMOTE.info(f"返回结果: {response}")
            return ExecuteResult.success(result=response)
        else:
            logger.REMOTE.error(f"❌ 脚本执行失败: {result}")
            # 使用 ExecutorResponse 包装失败结果
            response = ExecutorResponse.failure(
                message="脚本执行失败",
                data=result if result else "执行失败"
            )
            return ExecuteResult.failure(result=response)

    except GitOperationError as e:
        logger.REMOTE.error(f"❌ Git 操作失败: {str(e)}")
        response = ExecutorResponse.failure(message="Git操作失败", data=str(e))
        return ExecuteResult.failure(result=response)

    except RequirementNotFoundError as e:
        logger.REMOTE.error(f"❌ 业务逻辑文件夹错误: {str(e)}")
        response = ExecutorResponse.failure(message="业务逻辑文件夹错误", data=str(e))
        return ExecuteResult.failure(result=response)

    except DependencyInstallError as e:
        logger.REMOTE.error(f"❌ 依赖安装失败: {str(e)}")
        response = ExecutorResponse.failure(message="依赖安装失败", data=str(e))
        return ExecuteResult.failure(result=response)

    except ScriptExecutionError as e:
        logger.REMOTE.error(f"❌ 脚本执行失败: {str(e)}")
        response = ExecutorResponse.failure(message="脚本执行失败", data=str(e))
        return ExecuteResult.failure(result=response)

    except PlaywrightExecutorError as e:
        logger.REMOTE.error(f"❌ 执行器错误: {str(e)}")
        response = ExecutorResponse.failure(message="执行器错误", data=str(e))
        return ExecuteResult.failure(result=response)

    except Exception as e:
        logger.REMOTE.error(f"❌ 未知错误: {str(e)}")
        import traceback

        logger.REMOTE.error(traceback.format_exc())
        response = ExecutorResponse.failure(message="未知错误", data=str(e))
        return ExecuteResult.failure(result=response)

    finally:
        logger.REMOTE.info("=" * 60)


def _parse_job_params(job_params: Any) -> dict:
    """解析任务参数"""
    try:
        if isinstance(job_params, str):
            params = json.loads(job_params)
        else:
            params = job_params

        # 验证必填参数
        required_fields = ["service_folder"]
        for field in required_fields:
            if field not in params:
                raise ValueError(f"缺少必填参数: {field}")

        return params

    except json.JSONDecodeError as e:
        raise ValueError(f"任务参数 JSON 解析失败: {str(e)}")


def _create_config(params: dict) -> PlaywrightExecutorConfig:
    """根据参数创建配置对象"""
    return PlaywrightExecutorConfig(
        git_url="",  # 从环境变量读取
        git_token="",  # 从环境变量读取
        git_branch=params.get("branch", "main"),
        workspace_root=Path(params.get("workspace_root", "/workspace")),
        service_folder=params["service_folder"],
        script_timeout=params.get("script_timeout", 1800),
    )

