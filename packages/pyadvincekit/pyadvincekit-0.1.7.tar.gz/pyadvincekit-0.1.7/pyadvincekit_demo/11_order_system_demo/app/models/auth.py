"""
认证相关数据模型

定义认证、会话相关的数据库模型。
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import String, DateTime, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from pyadvincekit.models.base import BaseModel, create_required_string_column, create_optional_string_column


class UserSession(BaseModel):
    """用户会话模型"""
    
    __tablename__ = "user_sessions"
    
    # 关联用户
    user_id: Mapped[str] = mapped_column(
        String(36), 
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        comment="用户ID"
    )
    
    # 会话信息
    token_jti: Mapped[str] = create_required_string_column(255, unique=True, index=True, comment="JWT唯一标识")
    refresh_token: Mapped[Optional[str]] = create_optional_string_column(500, comment="刷新令牌")
    
    # 客户端信息
    user_agent: Mapped[Optional[str]] = create_optional_string_column(500, comment="用户代理")
    ip_address: Mapped[Optional[str]] = create_optional_string_column(45, comment="IP地址")
    
    # 时间信息
    login_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.now,
        comment="登录时间"
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        comment="过期时间"
    )
    last_activity_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.now,
        onupdate=datetime.now,
        comment="最后活动时间"
    )
    
    # 状态
    is_revoked: Mapped[bool] = mapped_column(
        default=False,
        comment="是否已撤销"
    )
    
    def is_expired(self) -> bool:
        """检查会话是否过期"""
        return datetime.now() > self.expires_at
    
    def is_valid(self) -> bool:
        """检查会话是否有效"""
        return not self.is_revoked and not self.is_expired()
    
    def revoke(self) -> None:
        """撤销会话"""
        self.is_revoked = True
    
    def update_activity(self) -> None:
        """更新活动时间"""
        self.last_activity_at = datetime.now()
    
    def __repr__(self) -> str:
        return f"<UserSession(id={self.id}, user_id={self.user_id}, token_jti={self.token_jti[:8]}...)>"
