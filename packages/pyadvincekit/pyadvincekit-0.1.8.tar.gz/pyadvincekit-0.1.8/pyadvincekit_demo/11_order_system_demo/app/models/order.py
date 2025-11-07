"""
订单数据模型

定义订单相关的数据库模型。
"""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional

from sqlalchemy import String, Text, Numeric, DateTime, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column

from pyadvincekit.models.base import (
    BaseModel,
    create_required_string_column,
    create_optional_string_column,
    create_text_column,
    create_integer_column,
    create_decimal_column,
    create_datetime_column
)


class OrderStatus(str, Enum):
    """订单状态枚举"""
    PENDING = "pending"      # 待处理
    PAID = "paid"           # 已支付
    SHIPPED = "shipped"     # 已发货
    COMPLETED = "completed" # 已完成
    CANCELLED = "cancelled" # 已取消


class Order(BaseModel):
    """订单模型"""
    
    __tablename__ = "orders"
    
    # 订单基本信息
    order_no: Mapped[str] = create_required_string_column(
        max_length=50,
        unique=True,
        comment="订单编号"
    )
    
    # 客户信息
    customer_name: Mapped[str] = create_required_string_column(
        max_length=100,
        comment="客户姓名"
    )
    
    customer_phone: Mapped[str] = create_required_string_column(
        max_length=20,
        comment="客户电话"
    )
    
    # 商品信息
    product_name: Mapped[str] = create_required_string_column(
        max_length=200,
        comment="商品名称"
    )
    
    quantity: Mapped[int] = create_integer_column(
        comment="数量",
        nullable=False,
        default=1
    )
    
    unit_price: Mapped[Decimal] = create_decimal_column(
        precision=10,
        scale=2,
        comment="单价",
        nullable=False
    )
    
    total_amount: Mapped[Decimal] = create_decimal_column(
        precision=10,
        scale=2,
        comment="总金额",
        nullable=False
    )
    
    # 订单状态和时间
    status: Mapped[OrderStatus] = mapped_column(
        SQLEnum(OrderStatus),
        nullable=False,
        default=OrderStatus.PENDING,
        comment="订单状态"
    )
    
    order_date: Mapped[datetime] = create_datetime_column(
        comment="订单日期",
        nullable=False,
        default=datetime.now
    )
    
    # 备注
    notes: Mapped[Optional[str]] = create_text_column(
        comment="备注信息"
    )
    
    def __repr__(self) -> str:
        return f"<Order {self.order_no}: {self.customer_name}>"
    
    def to_dict(self, exclude_sensitive: bool = False) -> dict:
        """转换为字典格式"""
        data = {
            "id": self.id,
            "order_no": self.order_no,
            "customer_name": self.customer_name,
            "customer_phone": self.customer_phone,
            "product_name": self.product_name,
            "quantity": self.quantity,
            "unit_price": float(self.unit_price),
            "total_amount": float(self.total_amount),
            "status": self.status.value,
            "order_date": self.order_date.isoformat() if self.order_date else None,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
        
        return data
    
    @classmethod
    def generate_order_no(cls) -> str:
        """生成订单编号"""
        from datetime import datetime
        now = datetime.now()
        return f"ORD{now.strftime('%Y%m%d%H%M%S')}"
    
    def calculate_total(self) -> None:
        """计算总金额"""
        self.total_amount = self.unit_price * self.quantity
    
    def update_status(self, new_status: OrderStatus) -> None:
        """更新订单状态"""
        self.status = new_status
        self.updated_at = datetime.now()
