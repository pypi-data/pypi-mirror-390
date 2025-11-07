"""
Pydantic模型模块

定义API请求和响应的数据结构。
"""

from .auth import *
from .user import *
from .common import *

__all__ = [
    # 认证相关
    "LoginRequest",
    "LoginResponse", 
    "TokenData",
    "UserInfo",
    "ChangePasswordRequest",
    
    # 用户相关
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "UserListResponse",
    "BatchDeleteRequest",
    
    # 通用
    "PaginationParams",
    "PaginatedResponse",
]














