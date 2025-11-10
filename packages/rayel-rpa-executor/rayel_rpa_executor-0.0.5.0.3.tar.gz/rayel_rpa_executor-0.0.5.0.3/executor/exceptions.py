"""自定义异常类"""


class PlaywrightExecutorError(Exception):
    """Playwright 执行器基础异常"""

    pass


class GitOperationError(PlaywrightExecutorError):
    """Git 操作异常"""

    pass


class RequirementNotFoundError(PlaywrightExecutorError):
    """需求文件夹或文件不存在异常"""

    pass


class DependencyInstallError(PlaywrightExecutorError):
    """依赖安装异常"""

    pass


class ScriptExecutionError(PlaywrightExecutorError):
    """脚本执行异常"""

    pass


class ConfigurationError(PlaywrightExecutorError):
    """配置错误异常"""

    pass

