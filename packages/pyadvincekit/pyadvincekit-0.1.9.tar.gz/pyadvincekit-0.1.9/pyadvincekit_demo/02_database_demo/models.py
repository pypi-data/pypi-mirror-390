from sqlalchemy.orm import Mapped
from sqlalchemy import Integer, Boolean
from pyadvincekit import (
    BaseModel, SoftDeleteModel,
    create_required_string_column, create_text_column,
    create_decimal_column, create_integer_column, create_boolean_column
)
from decimal import Decimal


class User(BaseModel):
    """用户模型"""
    __tablename__ = "users"

    # 使用便捷字段函数
    username: Mapped[str] = create_required_string_column(50, unique=True, comment="用户名")
    email: Mapped[str] = create_required_string_column(255, unique=True, comment="邮箱")
    full_name: Mapped[str] = create_required_string_column(100, comment="全名")
    age: Mapped[int] = create_integer_column(nullable=True, comment="年龄")
    is_active: Mapped[bool] = create_boolean_column(nullable=True, comment="是否激活")


class Product(SoftDeleteModel):
    """产品模型（支持软删除）"""
    __tablename__ = "products"

    name: Mapped[str] = create_required_string_column(200, comment="产品名称")
    description: Mapped[str] = create_text_column(comment="产品描述")
    price: Mapped[Decimal] = create_decimal_column(10, 2, comment="价格")
    stock: Mapped[int] = create_integer_column(default=0, comment="库存")
    category: Mapped[str] = create_required_string_column(100, comment="分类")