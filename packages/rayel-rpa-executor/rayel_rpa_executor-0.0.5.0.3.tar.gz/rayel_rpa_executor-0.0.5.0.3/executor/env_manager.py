"""虚拟环境管理模块"""

import hashlib
import subprocess
import sys
from pathlib import Path
from typing import List, Optional

import snailjob as sj

from .config import PlaywrightExecutorConfig
from .exceptions import DependencyInstallError, RequirementNotFoundError
from .logger import logger


class EnvManager:
    """虚拟环境管理器"""

    def __init__(self, config: PlaywrightExecutorConfig):
        self.config = config
        self.venv_path = config.get_venv_path()
        self.service_path = config.get_service_path()

    def ensure_environment(self) -> None:
        """
        确保虚拟环境存在且依赖已安装

        流程:
            1. 验证业务逻辑文件夹和 main.py 存在
            2. 创建虚拟环境（如果不存在）
            3. 检查依赖是否需要更新（MD5 校验）
            4. 安装/更新依赖
        """
        # 1. 验证业务逻辑文件夹
        self._validate_service_folder()

        # 2. 创建虚拟环境
        if not self.venv_path.exists():
            logger.REMOTE.info(f"虚拟环境不存在，开始创建: {self.venv_path}")
            self._create_venv()
        else:
            logger.REMOTE.info(f"虚拟环境已存在: {self.venv_path}")

        # 3. 检查并安装依赖
        self._ensure_dependencies()

    def _validate_service_folder(self) -> None:
        """验证业务逻辑文件夹和 main.py 是否存在"""
        if not self.service_path.exists():
            raise RequirementNotFoundError(f"业务逻辑文件夹不存在: {self.service_path}")

        main_py = self.service_path / "main.py"
        if not main_py.exists():
            raise RequirementNotFoundError(f"main.py 不存在: {main_py}")

        logger.REMOTE.info(f"业务逻辑文件夹验证通过: {self.service_path}")

    def _create_venv(self) -> None:
        """创建虚拟环境"""
        try:
            self.venv_path.parent.mkdir(parents=True, exist_ok=True)

            cmd = ["python3", "-m", "venv", str(self.venv_path)]
            logger.REMOTE.info(f"执行命令: {' '.join(cmd)}")

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

            if result.returncode != 0:
                raise DependencyInstallError(f"创建虚拟环境失败: {result.stderr}")

            logger.REMOTE.info("虚拟环境创建成功")

            # 自动安装 rayel-rpa-executor 包到虚拟环境（所有业务都需要）
            # self._install_snailjob_package()

        except subprocess.TimeoutExpired:
            raise DependencyInstallError("创建虚拟环境超时（120秒）")
        except Exception as e:
            raise DependencyInstallError(f"创建虚拟环境异常: {str(e)}")

    def _ensure_dependencies(self) -> None:
        """确保依赖已安装且是最新的（基于 MD5 校验）"""
        requirements_files = self._get_requirements_files()

        if not requirements_files:
            logger.REMOTE.info("未找到 requirements.txt 文件，跳过依赖安装")
            return

        # 计算当前 requirements 文件的 MD5
        current_md5 = self._calculate_requirements_md5(requirements_files)

        # 获取缓存的 MD5
        cached_md5 = self._get_cached_md5()

        if current_md5 == cached_md5:
            logger.REMOTE.info("依赖文件未变化（MD5 一致），跳过安装")
            return

        # 安装依赖
        logger.REMOTE.info("依赖文件有变化，开始安装...")
        for req_file in requirements_files:
            self._install_requirements(req_file)

        # 更新 MD5 缓存
        self._save_md5_cache(current_md5)
        logger.REMOTE.info("依赖安装完成并更新 MD5 缓存")

    def _get_requirements_files(self) -> List[Path]:
        """
        获取需要安装的 requirements.txt 文件列表

        优先级:
            1. 根目录的 requirements.txt（通用依赖）
            2. 业务逻辑文件夹的 requirements.txt（业务特定依赖）
        """
        files = []

        # 1. 根目录的 requirements.txt
        root_req = self.config.git_repo_dir / "requirements.txt"
        if root_req.exists():
            files.append(root_req)
            logger.REMOTE.info(f"发现根目录依赖文件: {root_req}")

        # 2. 业务逻辑文件夹的 requirements.txt
        service_folder_req = self.service_path / "requirements.txt"
        if service_folder_req.exists():
            files.append(service_folder_req)
            logger.REMOTE.info(f"发现业务目录依赖文件: {service_folder_req}")

        return files

    def _calculate_requirements_md5(self, files: List[Path]) -> str:
        """计算多个 requirements.txt 文件的联合 MD5"""
        md5_hash = hashlib.md5()

        for file in sorted(files, key=lambda x: str(x)):  # 排序确保顺序一致
            with open(file, "rb") as f:
                md5_hash.update(f.read())

        return md5_hash.hexdigest()

    def _get_cached_md5(self) -> Optional[str]:
        """获取缓存的 MD5 值"""
        md5_file = self._get_md5_cache_file()

        if not md5_file.exists():
            return None

        try:
            return md5_file.read_text().strip()
        except Exception:
            return None

    def _save_md5_cache(self, md5: str) -> None:
        """保存 MD5 缓存"""
        md5_file = self._get_md5_cache_file()
        md5_file.parent.mkdir(parents=True, exist_ok=True)
        md5_file.write_text(md5)

    def _get_md5_cache_file(self) -> Path:
        """获取 MD5 缓存文件路径"""
        venv_name = self.config.get_venv_name()
        return self.config.md5_cache_dir / f"{venv_name}.md5"

    def _install_requirements(self, req_file: Path) -> None:
        """安装指定的 requirements.txt"""
        try:
            pip_path = self.venv_path / "bin" / "pip"

            # 使用相对路径 "requirements.txt"，并将工作目录设置为文件所在目录
            # 这样 requirements.txt 中的相对路径（如 ../../common/whl/xxx.whl）就能正确解析
            # 使用清华镜像源加速下载
            cmd = [
                str(pip_path),
                "install",
                "-i",
                "https://pypi.tuna.tsinghua.edu.cn/simple",
                "--no-input",  # 禁用交互式提示
                "-r",
                "requirements.txt",
                "--timeout",
                "300",
            ]

            logger.REMOTE.info(f"安装依赖: {req_file}")
            logger.REMOTE.info(f"执行命令: pip install -i https://pypi.tuna.tsinghua.edu.cn/simple --no-input -r requirements.txt")
            logger.REMOTE.info(f"工作目录: {req_file.parent}")
            logger.REMOTE.info(f"requirements.txt 内容:  \b: {req_file.read_text()}")

            # 使用 Popen 实时输出日志
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,  # 合并 stderr 到 stdout
                text=True,
                cwd=str(req_file.parent),
                bufsize=1,  # 行缓冲
            )

            # 实时读取并输出日志
            output_lines = []
            for line in process.stdout:
                line = line.rstrip()
                if line:  # 忽略空行
                    logger.REMOTE.info(f"[pip] {line}")
                    output_lines.append(line)

            # 等待进程结束，设置超时
            try:
                process.wait(timeout=180)  # 3分钟超时
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
                raise DependencyInstallError(f"安装依赖超时 ({req_file})，超过3分钟")

            if process.returncode != 0:
                error_msg = "\n".join(output_lines[-20:])  # 只显示最后20行
                raise DependencyInstallError(f"安装依赖失败 ({req_file}): {error_msg}")

            logger.REMOTE.info(f"依赖安装成功: {req_file}")

        except subprocess.TimeoutExpired:
            raise DependencyInstallError(f"安装依赖超时 ({req_file})，超过3分钟")
        except DependencyInstallError:
            raise
        except Exception as e:
            raise DependencyInstallError(f"安装依赖异常 ({req_file}): {str(e)}")

    def _install_snailjob_package(self) -> None:
        """
        安装 rayel-rpa-executor 包到虚拟环境

        所有业务脚本都需要使用 snailjob 来记录日志等操作，
        因此在创建虚拟环境后自动安装 snailjob 包
        """
        try:
            pip_path = self.venv_path / "bin" / "pip"

            # 从 PyPI 安装 snail-job-python 包
            cmd = [
                str(pip_path),
                "install",
                "-i",
                "https://pypi.tuna.tsinghua.edu.cn/simple",
                "--no-input",  # 禁用交互式提示
                "rayel-rpa-executor",
            ]

            logger.REMOTE.info("安装 rayel-rpa-executor 包到虚拟环境（从 PyPI）")

            # 使用 Popen 实时输出日志
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
            )

            # 实时读取并输出日志
            output_lines = []
            for line in process.stdout:
                line = line.rstrip()
                if line:
                    logger.REMOTE.info(f"[pip] {line}")
                    output_lines.append(line)

            # 等待进程结束
            try:
                process.wait(timeout=180)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
                raise DependencyInstallError("安装 snailjob 包超时（3分钟）")

            if process.returncode != 0:
                error_msg = "\n".join(output_lines[-20:])
                raise DependencyInstallError(f"安装 snailjob 包失败: {error_msg}")

            logger.REMOTE.info("snailjob 包安装成功")

        except subprocess.TimeoutExpired:
            raise DependencyInstallError("安装 snailjob 包超时（3分钟）")
        except DependencyInstallError:
            raise
        except Exception as e:
            raise DependencyInstallError(f"安装 snailjob 包异常: {str(e)}")

    def get_site_packages_paths(self) -> List[str]:
        """
        获取虚拟环境的 site-packages 路径

        用于动态导入时添加到 sys.path

        Returns:
            存在的 site-packages 路径列表
        """
        python_version = self.config.get_python_version()

        site_packages_paths = [
            str(self.venv_path / "lib" / python_version / "site-packages"),
            str(self.venv_path / "lib64" / python_version / "site-packages"),  # 兼容某些系统
        ]

        # 只返回存在的路径
        existing_paths = [p for p in site_packages_paths if Path(p).exists()]

        if not existing_paths:
            logger.REMOTE.warning(f"未找到 site-packages 目录: {site_packages_paths}")

        return existing_paths

