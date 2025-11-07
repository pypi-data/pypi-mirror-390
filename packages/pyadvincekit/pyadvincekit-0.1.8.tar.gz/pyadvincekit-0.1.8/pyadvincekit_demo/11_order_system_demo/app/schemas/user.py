"""
用户相关Pydantic模型

定义用户相关的请求和响应模型。
"""

from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr
from .common import PaginatedResponse


class UserCreate(BaseModel):
    """创建用户请求"""
    name: str = Field(min_length=2, max_length=100, description="用户姓名")
    email: EmailStr = Field(description="邮箱地址")
    password: str = Field(min_length=6, description="密码")
    phone: Optional[str] = Field(default=None, max_length=20, description="电话号码")
    department: Optional[str] = Field(default=None, max_length=100, description="部门")
    bio: Optional[str] = Field(default=None, max_length=500, description="个人简介")
    is_active: bool = Field(default=True, description="是否激活")
    is_superuser: bool = Field(default=False, description="是否超级用户")


class UserUpdate(BaseModel):
    """更新用户请求"""
    name: Optional[str] = Field(default=None, min_length=2, max_length=100, description="用户姓名")
    email: Optional[EmailStr] = Field(default=None, description="邮箱地址")
    phone: Optional[str] = Field(default=None, max_length=20, description="电话号码")
    department: Optional[str] = Field(default=None, max_length=100, description="部门")
    bio: Optional[str] = Field(default=None, max_length=500, description="个人简介")
    avatar: Optional[str] = Field(default=None, max_length=500, description="头像URL")
    is_active: Optional[bool] = Field(default=None, description="是否激活")
    is_superuser: Optional[bool] = Field(default=None, description="是否超级用户")


class UserResponse(BaseModel):
    """用户响应"""
    id: str = Field(description="用户ID")
    name: str = Field(description="用户姓名")
    email: str = Field(description="邮箱地址")
    is_active: bool = Field(description="是否激活")
    is_superuser: bool = Field(description="是否超级用户")
    phone: Optional[str] = Field(default=None, description="电话号码")
    avatar: Optional[str] = Field(default=None, description="头像URL")
    department: Optional[str] = Field(default=None, description="部门")
    bio: Optional[str] = Field(default=None, description="个人简介")
    last_login_at: Optional[str] = Field(default=None, description="最后登录时间")
    created_at: str = Field(description="创建时间")
    updated_at: str = Field(description="更新时间")

    class Config:
        from_attributes = True


class UserListParams(BaseModel):
    """用户列表查询参数"""
    page: int = Field(default=1, ge=1, description="页码")
    size: int = Field(default=20, ge=1, le=100, description="每页数量")
    keyword: Optional[str] = Field(default=None, description="搜索关键词(姓名、邮箱)")
    is_active: Optional[bool] = Field(default=None, description="是否激活")
    is_superuser: Optional[bool] = Field(default=None, description="是否超级用户")
    department: Optional[str] = Field(default=None, description="部门")


class UserListResponse(PaginatedResponse[UserResponse]):
    """用户列表响应"""
    pass


class UserBatchDeleteRequest(BaseModel):
    """批量删除用户请求"""
    ids: List[str] = Field(min_items=1, description="要删除的用户ID列表")


class UserPasswordResetRequest(BaseModel):
    """重置用户密码请求"""
    new_password: str = Field(min_length=6, description="新密码")


class UserStatsResponse(BaseModel):
    """用户统计响应"""
    total_users: int = Field(description="总用户数")
    active_users: int = Field(description="激活用户数")
    superusers: int = Field(description="超级用户数")
    new_users_today: int = Field(description="今日新增用户")
    online_users: int = Field(description="在线用户数")














