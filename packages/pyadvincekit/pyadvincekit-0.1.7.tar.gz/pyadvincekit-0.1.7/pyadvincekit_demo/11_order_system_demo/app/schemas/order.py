"""
订单相关的Pydantic模型

定义订单的请求和响应模型。
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from enum import Enum

from pydantic import BaseModel, Field, validator, ConfigDict
from pyadvincekit import validate_email, validate_phone, create_validator


class OrderStatus(str, Enum):
    """订单状态枚举"""
    PENDING = "pending"
    PAID = "paid" 
    SHIPPED = "shipped"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class OrderBase(BaseModel):
    """订单基础模型"""
    model_config = ConfigDict(
        # 允许从字符串解析Decimal
        str_strip_whitespace=True,
        # 使用字符串验证器
        validate_assignment=True
    )
    
    customer_name: str = Field(..., min_length=1, max_length=100, description="客户姓名")
    customer_phone: str = Field(..., min_length=10, max_length=20, description="客户电话")
    product_name: str = Field(..., min_length=1, max_length=200, description="商品名称")
    quantity: int = Field(..., gt=0, description="数量")
    unit_price: Decimal = Field(..., gt=0, description="单价")
    notes: Optional[str] = Field(None, max_length=500, description="备注信息")
    
    @validator('customer_phone')
    def validate_phone(cls, v):
        """验证手机号格式"""
        is_phone = validate_phone(v)
        if not is_phone:
            raise ValueError('请输入正确的手机号格式')
        return v
    
    @validator('unit_price')
    def validate_price(cls, v):
        """验证价格格式"""
        if v <= 0:
            raise ValueError('价格必须大于0')
        # 保留2位小数
        return round(v, 2)


class OrderCreate(OrderBase):
    """创建订单模型"""
    pass


class OrderUpdate(BaseModel):
    """更新订单模型"""
    model_config = ConfigDict(
        # 允许从字符串解析Decimal
        str_strip_whitespace=True,
        # 使用字符串验证器
        validate_assignment=True
    )
    
    customer_name: Optional[str] = Field(None, min_length=1, max_length=100)
    customer_phone: Optional[str] = Field(None, min_length=10, max_length=20)
    product_name: Optional[str] = Field(None, min_length=1, max_length=200)
    quantity: Optional[int] = Field(None, gt=0)
    unit_price: Optional[Decimal] = Field(None, gt=0)
    status: Optional[OrderStatus] = None
    notes: Optional[str] = Field(None, max_length=500)
    
    @validator('customer_phone')
    def validate_phone(cls, v):
        is_phone = validate_phone(v)
        if not is_phone:
            raise ValueError('请输入正确的手机号格式')
        return v
    
    @validator('unit_price')
    def validate_price(cls, v):
        if v is not None:
            if v <= 0:
                raise ValueError('价格必须大于0')
            return round(v, 2)
        return v


class OrderResponse(OrderBase):
    """订单响应模型"""
    id: int
    order_no: str
    total_amount: Decimal
    status: OrderStatus
    order_date: datetime
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class OrderListParams(BaseModel):
    """订单列表查询参数"""
    page: int = Field(1, ge=1, description="页码")
    size: int = Field(10, ge=1, le=100, description="每页数量")
    keyword: Optional[str] = Field(None, max_length=100, description="搜索关键词(订单号/客户姓名/商品名称)")
    status: Optional[OrderStatus] = Field(None, description="订单状态")
    start_date: Optional[datetime] = Field(None, description="开始日期")
    end_date: Optional[datetime] = Field(None, description="结束日期")
    
    @validator('end_date')
    def validate_date_range(cls, v, values):
        """验证日期范围"""
        if v is not None and 'start_date' in values and values['start_date'] is not None:
            if v < values['start_date']:
                raise ValueError('结束日期不能早于开始日期')
        return v


class OrderStatsResponse(BaseModel):
    """订单统计响应模型"""
    total_orders: int = Field(..., description="总订单数")
    pending_orders: int = Field(..., description="待处理订单数")
    completed_orders: int = Field(..., description="已完成订单数")
    total_amount: Decimal = Field(..., description="总金额")
    today_orders: int = Field(..., description="今日订单数")
    today_amount: Decimal = Field(..., description="今日金额")


class BatchDeleteRequest(BaseModel):
    """批量删除请求模型"""
    order_ids: List[int] = Field(..., min_items=1, description="订单ID列表")


class OrderStatusUpdateRequest(BaseModel):
    """订单状态更新请求模型"""
    status: OrderStatus = Field(..., description="新状态")
