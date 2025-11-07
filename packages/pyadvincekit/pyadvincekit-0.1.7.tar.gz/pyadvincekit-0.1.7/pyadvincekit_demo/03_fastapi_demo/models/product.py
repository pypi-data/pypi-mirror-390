from sqlalchemy.orm import Mapped
from pyadvincekit import (
    SoftDeleteModel,
    create_required_string_column, create_text_column,
    create_decimal_column, create_integer_column, create_boolean_column
)
from decimal import Decimal

class Product(SoftDeleteModel):
    """产品模型（支持软删除）"""
    __tablename__ = "products"

    name: Mapped[str] = create_required_string_column(200, comment="产品名称")
    description: Mapped[str] = create_text_column(comment="产品描述")
    price: Mapped[Decimal] = create_decimal_column(10, 2, comment="价格")
    stock: Mapped[int] = create_integer_column(default=0, comment="库存")
    category: Mapped[str] = create_required_string_column(100, comment="分类")