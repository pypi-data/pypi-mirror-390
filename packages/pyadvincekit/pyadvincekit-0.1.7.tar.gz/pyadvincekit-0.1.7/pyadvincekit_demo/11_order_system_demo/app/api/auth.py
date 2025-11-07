"""
认证相关API接口

提供用户登录、退出、令牌刷新等认证功能。
使用PyAdvanceKit的数据库会话管理，无需外部传入AsyncSession。
"""

from fastapi import APIRouter, Depends, Request, status

from pyadvincekit import success_response, error_response
from app.services.dependencies import get_current_active_user
from app.schemas.auth import (
    LoginRequest, LoginResponse, UserInfo, ChangePasswordRequest
)
from app.schemas.common import MessageResponse
from app.services.auth_service import auth_service
from app.models.user import User


router = APIRouter(prefix="/auth", tags=["认证"])


@router.post("/login", response_model=dict, summary="用户登录")
async def login(
    request: Request,
    login_data: LoginRequest
):
    """用户登录
    
    Args:
        request: 请求对象
        login_data: 登录数据
        
    Returns:
        登录响应，包含访问令牌和用户信息
    """
    # 验证用户 - 服务层内部管理数据库会话
    user = await auth_service.authenticate_user(
        login_data.email, login_data.password
    )

    if not user:
        return error_response(
            message="Incorrect email or password",
            ret_code=status.HTTP_401_UNAUTHORIZED
        )
    
    # 获取客户端信息
    user_agent = request.headers.get("user-agent")
    ip_address = request.client.host if request.client else None
    
    # 创建会话 - 服务层内部管理数据库会话
    session_data = await auth_service.create_user_session(
        user, user_agent, ip_address
    )
    
    return success_response(
        data=session_data,
        message="Login successful"
    )


@router.post("/logout", response_model=dict, summary="用户退出")
async def logout(
):
    """用户退出
    
    Args:
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        退出响应
    """
    # 这里需要从token中获取jti，暂时简化处理
    # 在实际实现中，应该从请求头的token中解析jti
    
    return success_response(
        message="Logout successful"
    )


@router.get("/me", response_model=dict, summary="获取当前用户信息")
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """获取当前用户信息
    
    Args:
        current_user: 当前用户
        
    Returns:
        用户信息
    """
    user_data = current_user.to_dict()
    
    return success_response(
        data=user_data,
        message="User info retrieved successfully"
    )


@router.post("/change-password", response_model=dict, summary="修改密码")
async def change_password(
    password_data: ChangePasswordRequest,
    current_user: User = Depends(get_current_active_user)
):
    """修改密码
    
    Args:
        password_data: 密码修改数据
        current_user: 当前用户
        
    Returns:
        修改结果
    """
    # 修改密码 - 服务层内部管理数据库会话
    success = await auth_service.change_user_password(
        current_user,
        password_data.current_password,
        password_data.new_password
    )

    if not success:
        return error_response(
            message="Current password is incorrect",
            code=status.HTTP_400_BAD_REQUEST
        )

    return success_response(
        message="Password changed successfully"
    )


@router.post("/refresh", response_model=dict, summary="刷新令牌")
async def refresh_token():
    """刷新令牌
    
    注意：这是一个占位实现，实际需要实现refresh token机制
    
    Returns:
        新的访问令牌
    """

    return success_response(
        message="Token refresh not implemented yet"
    )
