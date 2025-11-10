"""自定义异常类"""


class ExecutorError(Exception):
    """Playwright 执行器基础异常"""

    pass


class GitOperationError(ExecutorError):
    """Git 操作异常"""

    pass


class RequirementNotFoundError(ExecutorError):
    """需求文件夹或文件不存在异常"""

    pass


class DependencyInstallError(ExecutorError):
    """依赖安装异常"""

    pass


class ScriptExecutionError(ExecutorError):
    """脚本执行异常"""

    pass


class ConfigurationError(ExecutorError):
    """配置错误异常"""

    pass

