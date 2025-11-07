#!/usr/bin/env python3
"""
API 路由层

提供 FastAPI 路由和接口定义
"""

# 导入所有路由
from .users import router

__all__ = [
    "router",
]






