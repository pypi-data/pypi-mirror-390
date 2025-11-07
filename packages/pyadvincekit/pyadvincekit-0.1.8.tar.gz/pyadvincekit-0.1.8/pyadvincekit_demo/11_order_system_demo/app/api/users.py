"""
用户管理API接口

提供用户创建、更新等功能，使用UserService处理业务逻辑。
"""

from app.models.user import User
from app.schemas.user import UserCreate
from app.services.dependencies import get_current_active_user
from app.services.user_service import user_service
from fastapi import APIRouter, Depends
from pyadvincekit import success_response, error_response

router = APIRouter(prefix="/users", tags=["用户管理"])


@router.post("/create_manual", response_model=dict, summary="手动创建用户")
async def create_user(
    user_data: UserCreate,
    current_user: User = Depends(get_current_active_user)
):
    """创建用户
    
    Args:
        user_data: 用户创建数据
        current_user: 当前用户
        
    Returns:
        创建的用户信息
    """
    try:
        # 检查权限（只有超级用户可以创建用户）
        if not current_user.is_superuser:
            return error_response(
                message="没有权限创建用户",
                ret_code="403001"
            )
        
        # 调用UserService创建用户
        user = await user_service.create_user(user_data)
        
        return success_response(
            data=user.to_dict(),
            message="用户创建成功"
        )
        
    except ValueError as e:
        return error_response(
            message=str(e),
            ret_code="400001"
        )
    except Exception as e:
        return error_response(
            message=f"创建用户失败: {str(e)}",
            ret_code="500001"
        )

