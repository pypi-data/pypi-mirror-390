"""
用户数据模型

定义用户相关的数据库模型。
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import String, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from pyadvincekit.models.base import BaseModel, create_required_string_column, create_optional_string_column


class User(BaseModel):
    """用户模型"""
    
    __tablename__ = "users"
    
    # 基本信息
    name: Mapped[str] = create_required_string_column(100, comment="用户姓名")
    email: Mapped[str] = create_required_string_column(255, unique=True, index=True, comment="邮箱地址")
    
    # 认证信息
    hashed_password: Mapped[str] = create_required_string_column(255, comment="加密后的密码")
    
    # 用户状态
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, comment="是否激活")
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, comment="是否超级用户")
    
    # 个人信息
    phone: Mapped[Optional[str]] = create_optional_string_column(20, comment="电话号码")
    avatar: Mapped[Optional[str]] = create_optional_string_column(500, comment="头像URL")
    department: Mapped[Optional[str]] = create_optional_string_column(100, comment="部门")
    bio: Mapped[Optional[str]] = create_optional_string_column(500, comment="个人简介")
    
    # 时间信息
    last_login_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), 
        nullable=True, 
        comment="最后登录时间"
    )
    password_changed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), 
        nullable=True, 
        comment="密码修改时间"
    )
    
    def to_dict(self, exclude: Optional[list] = None, include_sensitive: bool = False) -> dict:
        """转换为字典
        
        Args:
            exclude: 要排除的字段列表
            include_sensitive: 是否包含敏感信息
            
        Returns:
            字典格式的用户数据
        """
        exclude = exclude or []
        
        # 默认排除敏感信息
        if not include_sensitive:
            exclude.extend(['hashed_password'])
        
        return super().to_dict(exclude=exclude)
    
    def check_password(self, password: str) -> bool:
        """检查密码
        
        Args:
            password: 明文密码
            
        Returns:
            密码是否正确
        """
        from pyadvincekit.utils.security import verify_password
        # 假设hashed_password存储格式为 "hash:salt"
        if ':' in self.hashed_password:
            hashed_password, salt = self.hashed_password.split(':', 1)
            return verify_password(password, hashed_password, salt)
        else:
            # 如果格式不正确，返回False
            return False
    
    def set_password(self, password: str) -> None:
        """设置密码
        
        Args:
            password: 明文密码
        """
        from pyadvincekit import hash_password
        # hash_password返回(hashed_password, salt)元组
        hashed_password, salt = hash_password(password)
        # 存储格式为 "hash:salt"
        self.hashed_password = f"{hashed_password}:{salt}"
        self.password_changed_at = datetime.now()
    
    def update_last_login(self) -> None:
        """更新最后登录时间"""
        self.last_login_at = datetime.now()
    
    @property
    def is_admin(self) -> bool:
        """是否是管理员"""
        return self.is_superuser
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email}, name={self.name})>"
