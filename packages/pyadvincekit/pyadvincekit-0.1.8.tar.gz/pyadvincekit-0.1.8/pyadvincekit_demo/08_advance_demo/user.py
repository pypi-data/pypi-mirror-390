#!/usr/bin/env python3
"""
Generated ORM model for user
Generated at: 2025-10-11T16:43:12.282748
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
    full_name: Mapped[Optional[str]] = create_optional_string_column(comment="全名", max_length=100)
    age: Mapped[Optional[int]] = create_integer_column(comment="年龄")
    is_active: Mapped[Optional[bool]] = create_boolean_column(comment="是否激活")
    hashed_password: Mapped[Optional[str]] = create_optional_string_column(comment="密码", max_length=225)

    # 索引定义
    __table_args__ = (Index('UIDX1_user', 'username', unique=True),)