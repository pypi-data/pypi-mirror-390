#!/usr/bin/env python3
"""
Generated ORM model for user
Generated at: 2025-10-11T11:20:35.392240
"""

from pyadvincekit.models.base import (
    BaseModel, create_required_string_column, create_decimal_column,
    create_uuid_column, create_float_column, create_bigint_column,
    create_enum_column, create_date_column, create_time_column,
    create_binary_column, create_email_column, create_phone_column,
    create_url_column, create_status_column, create_sort_order_column,
    create_foreign_key_column, create_version_column
)
from datetime import datetime, date, time
from typing import Optional
from sqlalchemy.orm import Mapped


from typing import Optional
from datetime import datetime, date, time
from decimal import Decimal
from sqlalchemy.orm import Mapped
from sqlalchemy import Index
from pyadvincekit import (
    BaseModel,
    # 字段创建函数
    create_required_string_column, create_optional_string_column, create_text_column,
    create_integer_column, create_bigint_column, create_float_column,
    create_boolean_column, create_datetime_column, create_date_column,
    create_time_column, create_decimal_column, create_json_column,
    create_status_column, create_version_column, create_foreign_key_column
)

class User(BaseModel):
    """用户表"""
    __tablename__ = "user"

    username: Mapped[Optional[str]] = create_optional_string_column(comment="用户名", max_length=50)
    email: Mapped[Optional[str]] = create_email_column(comment="电子邮件")
    # 认证信息
    hashed_password: Mapped[str] = create_required_string_column(255, comment="加密后的密码")
    full_name: Mapped[Optional[str]] = create_optional_string_column(comment="全名", max_length=100)
    age: Mapped[Optional[int]] = create_integer_column(comment="年龄")
    is_active: Mapped[Optional[bool]] = create_boolean_column(comment="是否激活")

    # 索引定义
    __table_args__ = (Index('UIDX1_user', 'username', unique=True),)

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