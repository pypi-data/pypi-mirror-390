"""配置管理模块"""

import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from .exceptions import ConfigurationError


@dataclass
class PlaywrightExecutorConfig:
    """Playwright 执行器配置类"""

    # Git 配置（从环境变量读取）
    git_url: str = field(default="", repr=True)  # Git 仓库地址（从环境变量读取）
    git_branch: str = "main"  # Git 分支
    git_token: str = field(default="", repr=False)  # Git Token（从环境变量读取）

    # 工作目录配置
    workspace_root: Path = Path("/workspace")  # 工作根目录
    git_repo_dir: Optional[Path] = None  # Git 仓库目录
    venvs_dir: Optional[Path] = None  # 虚拟环境目录
    md5_cache_dir: Optional[Path] = None  # MD5 缓存目录

    # 执行配置
    service_folder: str = ""  # 业务逻辑文件夹名称（只需要写文件夹名，如：demo_service）
    script_timeout: int = 1800  # 脚本执行超时时间（秒），默认30分钟

    # 固定的业务逻辑父目录
    _SERVICE_PARENT_DIR: str = "app/services"

    def __post_init__(self):
        """初始化派生配置"""
        # 确保 workspace_root 是 Path 对象
        if isinstance(self.workspace_root, str):
            self.workspace_root = Path(self.workspace_root)

        # 设置派生路径
        self.git_repo_dir = self.workspace_root / "playwright_project"
        self.venvs_dir = self.workspace_root / "venvs"
        self.md5_cache_dir = self.venvs_dir / ".md5_cache"

        # 自动拼接业务逻辑文件夹完整路径
        if self.service_folder:
            # 去除前后的斜杠，避免重复
            folder_name = self.service_folder.strip("/")
            # 拼接父目录和子文件夹名称
            self.service_folder = f"{self._SERVICE_PARENT_DIR}/{folder_name}"

        # 从环境变量读取 Git URL
        if not self.git_url:
            self.git_url = os.getenv("GIT_REPO_URL", "")
            if not self.git_url:
                raise ConfigurationError(
                    "GIT_REPO_URL 环境变量未设置，请在 .env 文件或系统环境变量中配置"
                )

        # 检测是否为 SSH URL
        is_ssh_url = self.git_url.startswith(("git@", "ssh://"))

        # 从环境变量读取 Git Token（仅 HTTPS URL 需要）
        if not is_ssh_url:
            if not self.git_token:
                self.git_token = os.getenv("GIT_TOKEN", "")
                if not self.git_token:
                    raise ConfigurationError(
                        "使用 HTTPS URL 时，GIT_TOKEN 环境变量未设置，请在 .env 文件或系统环境变量中配置"
                    )
        else:
            # SSH URL 不需要 token，但允许从环境变量读取（向后兼容）
            if not self.git_token:
                self.git_token = os.getenv("GIT_TOKEN", "")

        # 验证必填参数
        if not self.service_folder:
            raise ConfigurationError("service_folder 参数为必填项")

    def get_service_path(self) -> Path:
        """
        获取RPA业务逻辑文件夹的完整路径
        
        示例：
            service_folder = "demo_service" 
            -> 完整路径 = git_repo_dir/app/services/demo_service
        """
        return self.git_repo_dir / self.service_folder

    def get_venv_name(self) -> str:
        """
        获取虚拟环境名称（基于业务逻辑文件夹路径）

        将路径中的特殊字符替换为下划线，确保文件系统兼容
        """
        safe_name = self.service_folder.replace("/", "_").replace("\\", "_")
        return f"{safe_name}_venv"

    def get_venv_path(self) -> Path:
        """获取虚拟环境路径"""
        return self.venvs_dir / self.get_venv_name()

    def get_python_version(self) -> str:
        """获取当前 Python 版本"""
        return f"python{sys.version_info.major}.{sys.version_info.minor}"

    def is_ssh_url(self) -> bool:
        """判断 Git URL 是否为 SSH 协议"""
        return self.git_url.startswith(("git@", "ssh://"))

