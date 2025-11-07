"""
订单管理API接口

提供订单创建功能，使用OrderService处理业务逻辑。
"""

from fastapi import APIRouter, Depends, status
from decimal import Decimal
from datetime import datetime

from pyadvincekit import success_response, error_response
from app.services.dependencies import get_current_active_user
from app.schemas.order import OrderCreate
from app.models.user import User
from app.models.order import Order, OrderStatus
from app.services.order_service import order_service


router = APIRouter(prefix="/orders", tags=["订单管理"])

@router.post("/create_manual", response_model=dict, summary="手动创建订单")
async def create_order_manual(
    order_data: OrderCreate,
    current_user: User = Depends(get_current_active_user)
):
    """手动创建订单（需要认证）
    
    Args:
        order_data: 订单创建数据
        current_user: 当前用户
        
    Returns:
        创建的订单信息
    """
    # 创建订单
    order = await order_service.create_order(order_data)

    return success_response(
        data=order.to_dict(),
        message="订单创建成功"
    )
        


@router.get("/stats/overview", response_model=dict, summary="获取订单统计")
async def get_order_stats(
        current_user: User = Depends(get_current_active_user)
):
    """获取订单统计信息

    Args:
        current_user: 当前用户

    Returns:
        订单统计信息
    """
    stats = await order_service.get_order_stats()

    return success_response(
        data=stats,
        message="获取订单统计成功"
    )

