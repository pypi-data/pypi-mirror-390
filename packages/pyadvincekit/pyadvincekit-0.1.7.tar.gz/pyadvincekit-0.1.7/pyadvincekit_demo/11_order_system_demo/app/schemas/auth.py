"""
认证相关Pydantic模型

定义认证相关的请求和响应模型。
"""

from typing import Optional
from pydantic import BaseModel, Field, EmailStr


class LoginRequest(BaseModel):
    """登录请求"""
    email: EmailStr = Field(description="邮箱地址")
    password: str = Field(min_length=6, description="密码")


class TokenData(BaseModel):
    """令牌数据"""
    access_token: str = Field(description="访问令牌")
    token_type: str = Field(default="bearer", description="令牌类型")
    expires_in: int = Field(description="过期时间(秒)")


class LoginResponse(BaseModel):
    """登录响应"""
    access_token: str = Field(description="访问令牌")
    token_type: str = Field(default="bearer", description="令牌类型")
    expires_in: int = Field(description="过期时间(秒)")
    user: "UserInfo" = Field(description="用户信息")


class UserInfo(BaseModel):
    """用户信息"""
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


class ChangePasswordRequest(BaseModel):
    """修改密码请求"""
    current_password: str = Field(min_length=6, description="当前密码")
    new_password: str = Field(min_length=6, description="新密码")


class RefreshTokenRequest(BaseModel):
    """刷新令牌请求"""
    refresh_token: str = Field(description="刷新令牌")














