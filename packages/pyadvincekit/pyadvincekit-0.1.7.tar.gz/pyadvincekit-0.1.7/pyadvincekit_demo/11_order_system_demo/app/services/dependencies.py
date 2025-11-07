"""
依赖注入

定义FastAPI依赖项。
使用PyAdvanceKit的数据库会话管理，无需外部传入AsyncSession。
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from pyadvincekit import verify_token
from app.models.user import User
from app.services.user_service import get_user_by_id

# JWT Bearer token - auto_error=False让依赖项处理认证错误
security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    """获取当前用户
    
    Args:
        credentials: HTTP认证凭据
        
    Returns:
        当前登录用户
        
    Raises:
        HTTPException: 认证失败时抛出异常
    """
    try:
        # 检查是否提供了认证凭据
        if credentials is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # 使用PyAdvanceKit的verify_token
        payload = verify_token(credentials.credentials)
        
        # 获取用户ID
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # 查询用户 - 使用PyAdvanceKit的数据库会话管理
        user = await get_user_by_id(user_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return user
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """获取当前活跃用户
    
    Args:
        current_user: 当前用户
        
    Returns:
        当前活跃用户
        
    Raises:
        HTTPException: 用户未激活时抛出异常
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user
