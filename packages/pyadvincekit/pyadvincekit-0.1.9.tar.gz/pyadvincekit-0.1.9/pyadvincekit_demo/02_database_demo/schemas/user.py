#!/usr/bin/env python3
"""
Generated Pydantic schemas for user
Generated at: 2025-10-11T16:43:12.283761
"""

from pydantic import BaseModel, Field
from datetime import datetime, date, time
from typing import Optional, Any, List
from decimal import Decimal


from pydantic import BaseModel, Field
from datetime import datetime, date, time
from typing import Optional, Any
from decimal import Decimal

class UserBase(BaseModel):
    """用户表"""

    username: Optional[str] = Field(default=None, description='用户名')
    email: Optional[str] = Field(default=None, description='电子邮件')
    full_name: Optional[str] = Field(default=None, description='全名')
    age: Optional[int] = Field(default=None, description='年龄')
    is_active: Optional[bool] = Field(default=None, description='是否激活')
    hashed_password: Optional[str] = Field(default=None, description='密码')

class UserCreate(UserBase):
    """创建时使用的模式"""
    pass

class UserUpdate(UserBase):
    """更新时使用的模式（所有字段都是可选的）"""
    pass

class UserResponse(UserBase):
    """API响应时使用的模式"""
    id: str  # PyAdvanceKit使用UUID作为主键
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class UserInDB(UserResponse):
    """数据库存储模式（包含所有字段）"""
    pass

class UserQuery(BaseModel):
    """查询参数模式"""
    page: Optional[int] = Field(default=1, ge=1, description='页码')
    size: Optional[int] = Field(default=10, ge=1, le=100, description='每页数量')
    search: Optional[str] = Field(default=None, description='搜索关键词')
    order_by: Optional[str] = Field(default=None, description='排序字段')
    order_desc: Optional[bool] = Field(default=False, description='是否降序')

class UserFilter(BaseModel):
    """过滤条件模式"""
    # 可以根据需要添加具体的过滤字段
    pass