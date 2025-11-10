"""
Playwright 通用执行器

用于执行存储在 GitLab 仓库中的 Playwright 自动化脚本项目。

Features:
    - 自动从 GitLab 拉取代码（支持增量更新）
    - 智能依赖管理（基于 MD5 校验，按需安装）
    - 环境隔离（每个需求独立的虚拟环境）
    - 实时日志上报到 SnailJob
    - 支持任务中断和超时控制

Usage:
    python main.py
"""

from .executor import playwright_executor
from .response import ExecutorResponse

__version__ = "1.0.0"
__author__ = "rayel"

__all__ = ["playwright_executor", "ExecutorResponse"]