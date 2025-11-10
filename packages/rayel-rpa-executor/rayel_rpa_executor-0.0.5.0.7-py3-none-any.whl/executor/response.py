"""执行器响应模型"""

from typing import Any

from pydantic import BaseModel


class ExecutorResponse(BaseModel):
    """
    执行器响应类
    
    用于统一返回执行结果，包含：
    - message: 返回信息，记录成功以及异常的文字提醒
    - data: 实际脚本结果，任意类型，视脚本实际返回结果而定
    """
    
    message: str
    data: Any = None
    
    @staticmethod
    def success(message: str = "执行完成", data: Any = None) -> "ExecutorResponse":
        """
        创建成功响应
        
        Args:
            message: 成功信息
            data: 返回的数据
            
        Returns:
            ExecutorResponse: 成功响应对象
        """
        return ExecutorResponse(message=message, data=data)
    
    @staticmethod
    def failure(message: str = "执行失败", data: Any = None) -> "ExecutorResponse":
        """
        创建失败响应
        
        Args:
            message: 失败信息
            data: 错误详情或相关数据
            
        Returns:
            ExecutorResponse: 失败响应对象
        """
        return ExecutorResponse(message=message, data=data)

