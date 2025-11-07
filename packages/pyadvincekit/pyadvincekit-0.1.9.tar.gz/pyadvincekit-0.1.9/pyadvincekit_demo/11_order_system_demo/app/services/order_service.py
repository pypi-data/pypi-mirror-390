"""
订单服务

处理订单管理相关的业务逻辑。
使用PyAdvanceKit的数据库会话管理，无需外部传入AsyncSession。
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, date
from decimal import Decimal

from pyadvincekit import BaseCRUD, get_database
from app.models.order import Order, OrderStatus
from app.schemas.order import OrderCreate, OrderUpdate, OrderListParams


class OrderService:
    """订单服务类"""
    
    def __init__(self):
        self.order_crud = BaseCRUD(Order)
    
    # async def get_order_by_id(self, order_id: int) -> Optional[Order]:
    #     """根据ID获取订单"""
    #     async with get_database() as db:
    #         return await self.order_crud.get(db, order_id, raise_not_found=False)
    
    async def get_order_by_no(self, order_no: str) -> Optional[Order]:
        """根据订单号获取订单"""
        async with get_database() as db:

            orders = await self.order_crud.get_multi(
                db,
                filters={"order_no": order_no},
                limit=1
            )
            return orders[0] if orders else None
    
    async def create_order(self, order_data: OrderCreate) -> Order:
        """创建订单"""
        async with get_database() as db:
            # 生成订单号
            order_no = Order.generate_order_no()
            
            # 检查订单号是否已存在（极小概率）
            existing_order = await self.get_order_by_no(order_no)
            if existing_order:
                # 如果存在，添加随机后缀
                import random
                order_no = f"{order_no}{random.randint(10, 99)}"
            
            # 准备订单数据
            order_dict = order_data.model_dump()
            order_dict['order_no'] = order_no
            order_dict['status'] = OrderStatus.PENDING
            order_dict['order_date'] = datetime.now()
            
            # 计算总金额
            total_amount = order_data.unit_price * order_data.quantity
            order_dict['total_amount'] = total_amount
            
            # 创建订单
            order = await self.order_crud.create(db, order_dict)
            return order
    
    async def get_order_stats(self) -> Dict[str, Any]:
        """获取订单统计信息"""
        async with get_database() as db:
            # 总订单数
            total_orders = await self.order_crud.count(db)

            # 各状态订单数
            pending_orders = await self.order_crud.count(
                db, filters={"status": OrderStatus.PENDING}
            )
            completed_orders = await self.order_crud.count(
                db, filters={"status": OrderStatus.COMPLETED}
            )

            # 总金额（这里简化，实际应该通过SQL聚合查询）
            all_orders = await self.order_crud.get_multi(db, limit=10000)
            total_amount = sum(order.total_amount for order in all_orders)

            # 今日订单 - 使用get_multi然后计算数量
            today = datetime.now().date()
            today_order_list = await self.order_crud.get_multi(
                db,
                filters={
                    "order_date": {
                        "operator": "gte",
                        "value": today
                    }
                },
                limit=1000
            )
            today_orders = len(today_order_list)

            # 今日金额（使用上面已经获取的数据）
            today_amount = sum(order.total_amount for order in today_order_list)

            return {
                "total_orders": total_orders,
                "pending_orders": pending_orders,
                "completed_orders": completed_orders,
                "total_amount": float(total_amount),
                "today_orders": today_orders,
                "today_amount": float(today_amount)
            }



# 创建全局服务实例
order_service = OrderService()

async def create_order(order_data: OrderCreate) -> Order:
    """创建订单（便捷函数）"""
    return await order_service.create_order(order_data)
