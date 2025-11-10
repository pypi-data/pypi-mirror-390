"""Git 操作管理模块"""

import os
import stat
import subprocess
from pathlib import Path

import snailjob as sj

from .config import PlaywrightExecutorConfig
from .exceptions import GitOperationError
from .logger import logger


class GitManager:
    """Git 操作管理器"""

    def __init__(self, config: PlaywrightExecutorConfig):
        self.config = config
        self.repo_dir = config.git_repo_dir
        
        # 如果使用 SSH URL，确保 SSH key 权限正确
        if config.is_ssh_url():
            self._ensure_ssh_key_permissions()

    def _ensure_ssh_key_permissions(self) -> None:
        """
        确保 SSH key 文件权限正确（600）
        这对于 SSH 认证是必需的
        """
        ssh_key_path = Path("/root/.ssh/id_rsa")
        
        if not ssh_key_path.exists():
            logger.REMOTE.warning(
                f"SSH key 文件不存在: {ssh_key_path}，"
                "请确保在 docker-compose.yml 中挂载了 ~/.ssh/id_rsa"
            )
            return
        
        # 检查当前权限
        try:
            current_mode = ssh_key_path.stat().st_mode
            # 检查是否为 600 (0o600 = 384 = S_IRUSR | S_IWUSR)
            expected_mode = stat.S_IRUSR | stat.S_IWUSR
            if (current_mode & 0o777) == expected_mode:
                # 权限已经是正确的，无需修改
                logger.REMOTE.debug(f"SSH key 权限已正确 (600): {ssh_key_path}")
                return
        except Exception as e:
            logger.REMOTE.debug(f"无法检查 SSH key 权限: {e}")
        
        # 尝试设置权限为 600（仅所有者可读写）
        try:
            os.chmod(ssh_key_path, stat.S_IRUSR | stat.S_IWUSR)
            logger.REMOTE.debug(f"SSH key 权限已设置为 600: {ssh_key_path}")
        except OSError as e:
            # 如果是只读文件系统（挂载为只读），这是正常的，不影响使用
            if e.errno == 30:  # Read-only file system
                logger.REMOTE.debug(
                    f"SSH key 文件为只读挂载，无法修改权限（这是正常的）: {ssh_key_path}"
                )
            else:
                logger.REMOTE.warning(f"无法设置 SSH key 权限: {e}")
        except Exception as e:
            logger.REMOTE.warning(f"无法设置 SSH key 权限: {e}")

    def ensure_repository(self) -> None:
        """
        确保 Git 仓库存在且是最新的

        - 如果仓库不存在，执行 clone
        - 如果仓库存在，执行 pull 更新
        """
        if not self.repo_dir.exists():
            logger.REMOTE.info(f"Git 仓库不存在，开始克隆: {self.config.git_url}")
            self._clone_repository()
        else:
            logger.REMOTE.info(f"Git 仓库已存在，开始更新: {self.repo_dir}")
            self._pull_repository()

    def _clone_repository(self) -> None:
        """克隆 Git 仓库（浅克隆）"""
        try:
            # 确保父目录存在
            self.repo_dir.parent.mkdir(parents=True, exist_ok=True)

            # 根据 URL 类型选择处理方式
            if self.config.is_ssh_url():
                # SSH URL：直接使用，不注入 token
                git_url = self.config.git_url
                logger.REMOTE.info("使用 SSH 协议克隆仓库")
            else:
                # HTTPS URL：注入 token
                git_url = self._inject_token_to_url(self.config.git_url)
                logger.REMOTE.info("使用 HTTPS 协议克隆仓库")

            # 执行 git clone（浅克隆，只克隆指定分支）
            cmd = [
                "git",
                "clone",
                "--branch",
                self.config.git_branch,
                "--depth",
                "1",  # 浅克隆，加快速度
                git_url,
                str(self.repo_dir),
            ]

            logger.REMOTE.info(f"执行命令: git clone --branch {self.config.git_branch} ...")

            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=300  # 5分钟超时
            )

            if result.returncode != 0:
                raise GitOperationError(f"Git clone 失败: {result.stderr}")

            logger.REMOTE.info("Git 仓库克隆成功")

        except subprocess.TimeoutExpired:
            raise GitOperationError("Git clone 超时（5分钟）")
        except Exception as e:
            raise GitOperationError(f"Git clone 异常: {str(e)}")

    def _pull_repository(self) -> None:
        """更新 Git 仓库（带重试机制和回退策略）"""
        max_retries = 3
        retry_delay = 2  # 秒
        
        for attempt in range(1, max_retries + 1):
            try:
                # 根据 URL 类型选择处理方式
                if self.config.is_ssh_url():
                    # SSH URL：直接使用
                    git_url = self.config.git_url
                    logger.REMOTE.info("使用 SSH 协议更新仓库")
                else:
                    # HTTPS URL：注入 token
                    git_url = self._inject_token_to_url(self.config.git_url)
                    logger.REMOTE.info("使用 HTTPS 协议更新仓库")
                
                # 更新 remote URL
                self._run_git_command(
                    ["remote", "set-url", "origin", git_url], hide_token=True
                )
                
                # 检出指定分支
                self._run_git_command(["checkout", self.config.git_branch])

                # 拉取最新代码（增加超时时间到 300 秒）
                logger.REMOTE.info(f"正在拉取代码（尝试 {attempt}/{max_retries}）...")
                
                # 使用 fetch + reset 强制同步到远程分支，避免分支分歧问题
                # 这样即使远程被强制推送（force push）也不会出错
                self._run_git_command(
                    ["fetch", "origin", self.config.git_branch, "--depth=1"], timeout=300
                )
                self._run_git_command(
                    ["reset", "--hard", f"origin/{self.config.git_branch}"], timeout=60
                )

                logger.REMOTE.info("Git 仓库更新成功")
                return  # 成功后直接返回

            except GitOperationError as e:
                error_msg = str(e)
                
                # 如果是网络相关错误，进行重试
                if any(keyword in error_msg.lower() for keyword in [
                    'tls', 'connection', 'timeout', 'network', 'recv error', 'could not connect'
                ]):
                    if attempt < max_retries:
                        logger.REMOTE.warning(
                            f"Git pull 失败（网络错误），{retry_delay}秒后重试... ({attempt}/{max_retries})"
                        )
                        logger.REMOTE.warning(f"错误信息: {error_msg}")
                        
                        # 尝试清理本地状态（可能有部分数据损坏）
                        try:
                            logger.REMOTE.info("尝试清理 Git 状态...")
                            self._run_git_command(["reset", "--hard"], timeout=30)
                            self._run_git_command(["clean", "-fd"], timeout=30)
                        except:
                            pass  # 清理失败不影响重试
                        
                        import time
                        time.sleep(retry_delay)
                        retry_delay *= 2  # 指数退避
                        continue
                    else:
                        # 所有重试都失败，尝试删除仓库重新克隆
                        logger.REMOTE.error(
                            f"Git pull 失败（已重试{max_retries}次），将在下次执行时重新克隆仓库"
                        )
                        raise GitOperationError(
                            f"Git pull 失败（已重试{max_retries}次）: {error_msg}"
                        )
                else:
                    # 非网络错误，直接抛出
                    raise
                    
            except Exception as e:
                raise GitOperationError(f"Git pull 异常: {str(e)}")

    def _run_git_command(
        self, args: list, timeout: int = 60, hide_token: bool = False
    ) -> subprocess.CompletedProcess:
        """执行 Git 命令"""
        cmd = ["git", "-C", str(self.repo_dir)] + args
        
        # 日志输出（避免泄露 token）
        if hide_token:
            # 隐藏带 token 的 URL
            log_cmd = " ".join(cmd).replace(self.config.git_token, "***")
            logger.REMOTE.info(f"执行命令: {log_cmd}")
        else:
            logger.REMOTE.info(f"执行命令: {' '.join(cmd)}")

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)

        if result.returncode != 0:
            # 错误信息中也要隐藏 token
            stderr = result.stderr.replace(self.config.git_token, "***") if self.config.git_token else result.stderr
            raise GitOperationError(f"Git 命令执行失败: {stderr}")

        return result

    def _inject_token_to_url(self, git_url: str) -> str:
        """
        将 token 注入到 Git URL 中（仅用于 HTTPS URL）

        支持格式:
            - GitHub: https://github.com/org/project.git
            - GitLab: https://gitlab.com/org/project.git
            - 自建 GitLab: https://gitlab.example.com/org/project.git
        
        认证格式:
            - GitHub: https://{token}@github.com/org/project.git
            - GitLab: https://oauth2:{token}@gitlab.com/org/project.git
        """
        if not git_url.startswith(("https://", "http://")):
            raise GitOperationError(
                f"不支持的 Git URL 格式: {git_url}，仅支持 HTTP(S) 协议"
            )
        
        # 判断是 GitHub 还是 GitLab
        is_github = "github.com" in git_url.lower()
        
        if is_github:
            # GitHub 使用 token 直接作为用户名
            if git_url.startswith("https://"):
                return git_url.replace("https://", f"https://{self.config.git_token}@")
            else:
                return git_url.replace("http://", f"http://{self.config.git_token}@")
        else:
            # GitLab 使用 oauth2:token 格式
            if git_url.startswith("https://"):
                return git_url.replace("https://", f"https://oauth2:{self.config.git_token}@")
            else:
                return git_url.replace("http://", f"http://oauth2:{self.config.git_token}@")

