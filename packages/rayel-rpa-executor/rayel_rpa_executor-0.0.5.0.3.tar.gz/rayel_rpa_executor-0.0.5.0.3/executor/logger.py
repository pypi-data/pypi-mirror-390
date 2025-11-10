"""日志管理模块 - 支持自动添加 JobID 和 TaskID 前缀"""

import contextvars
from typing import Optional, Tuple

import snailjob as sj

# 上下文变量，用于存储当前任务的 job_id 和 task_batch_id
_job_context_var: contextvars.ContextVar[Optional[Tuple[Optional[int], Optional[int]]]] = contextvars.ContextVar('job_context', default=None)


def _get_prefix() -> str:
    """
    获取日志前缀
    
    Returns:
        如果 job_id 和 task_batch_id 都存在，返回 "[JobID:xxx TaskID:xxx] "
        如果只有 job_id 存在，返回 "[JobID:xxx] "
        否则返回空字符串
    """
    context = _job_context_var.get()
    if context is None:
        return ""
    
    job_id, task_batch_id = context
    if job_id is not None and task_batch_id is not None:
        return f"[JobID:{job_id} TaskID:{task_batch_id}] "
    elif job_id is not None:
        return f"[JobID:{job_id}] "
    return ""


class _RemoteLogger:
    """远程日志记录器（自动添加 JobID 和 TaskID 前缀）"""
    
    @staticmethod
    def debug(msg: str) -> None:
        """记录 REMOTE DEBUG 级别日志"""
        prefix = _get_prefix()
        sj.SnailLog.REMOTE.debug(f"{prefix}{msg}")
    
    @staticmethod
    def info(msg: str) -> None:
        """记录 REMOTE INFO 级别日志"""
        prefix = _get_prefix()
        sj.SnailLog.REMOTE.info(f"{prefix}{msg}")
    
    @staticmethod
    def warning(msg: str) -> None:
        """记录 REMOTE WARNING 级别日志"""
        prefix = _get_prefix()
        sj.SnailLog.REMOTE.warning(f"{prefix}{msg}")
    
    @staticmethod
    def error(msg: str) -> None:
        """记录 REMOTE ERROR 级别日志"""
        prefix = _get_prefix()
        sj.SnailLog.REMOTE.error(f"{prefix}{msg}")


class _LocalLogger:
    """本地日志记录器（自动添加 JobID 和 TaskID 前缀）"""
    
    @staticmethod
    def debug(msg: str) -> None:
        """记录 LOCAL DEBUG 级别日志"""
        prefix = _get_prefix()
        sj.SnailLog.LOCAL.debug(f"{prefix}{msg}")
    
    @staticmethod
    def info(msg: str) -> None:
        """记录 LOCAL INFO 级别日志"""
        prefix = _get_prefix()
        sj.SnailLog.LOCAL.info(f"{prefix}{msg}")
    
    @staticmethod
    def warning(msg: str) -> None:
        """记录 LOCAL WARNING 级别日志"""
        prefix = _get_prefix()
        sj.SnailLog.LOCAL.warning(f"{prefix}{msg}")
    
    @staticmethod
    def error(msg: str) -> None:
        """记录 LOCAL ERROR 级别日志"""
        prefix = _get_prefix()
        sj.SnailLog.LOCAL.error(f"{prefix}{msg}")


class logger:
    """
    自定义日志类，用法与 sj.SnailLog 保持一致，自动从上下文中获取 job_id 和 task_batch_id 并添加前缀
    
    使用方式:
        # 在主流程中设置 job_id 和 task_batch_id
        logger.set_job_id(job_id, task_batch_id)
        
        # 在任何模块中使用（自动带前缀，用法与 sj.SnailLog 一致）
        logger.REMOTE.debug("debug msg")    # 输出: [JobID:123 TaskID:456] debug msg
        logger.REMOTE.info("info msg")      # 输出: [JobID:123 TaskID:456] info msg
        logger.REMOTE.warning("warn msg")   # 输出: [JobID:123 TaskID:456] warn msg
        logger.REMOTE.error("error msg")    # 输出: [JobID:123 TaskID:456] error msg
        logger.LOCAL.info("local msg")      # 输出: [JobID:123 TaskID:456] local msg
        
        # 如果只设置 job_id
        logger.set_job_id(job_id=123)
        logger.REMOTE.info("info msg")      # 输出: [JobID:123] info msg
        
        # 如果都为 None，则不添加前缀
        logger.REMOTE.info("xxx")           # 输出: xxx
        
    支持的日志级别:
        - debug: 调试信息
        - info: 普通信息
        - warning: 警告信息
        - error: 错误信息
    """
    
    # 创建日志记录器实例
    REMOTE = _RemoteLogger()
    LOCAL = _LocalLogger()
    
    @staticmethod
    def set_job_and_task_batch_id(job_id: Optional[int] = None, task_batch_id: Optional[int] = None) -> None:
        """
        设置当前上下文的 job_id 和 task_batch_id
        
        Args:
            job_id: 任务ID，如果为 None 则不添加 JobID 前缀
            task_batch_id: 任务批次ID，如果为 None 则不添加 TaskID 前缀
        """
        _job_context_var.set((job_id, task_batch_id))
    
    @staticmethod
    def get_job_id() -> Optional[int]:
        """获取当前上下文的 job_id"""
        context = _job_context_var.get()
        return context[0] if context else None
    
    @staticmethod
    def get_task_batch_id() -> Optional[int]:
        """获取当前上下文的 task_batch_id"""
        context = _job_context_var.get()
        return context[1] if context else None

