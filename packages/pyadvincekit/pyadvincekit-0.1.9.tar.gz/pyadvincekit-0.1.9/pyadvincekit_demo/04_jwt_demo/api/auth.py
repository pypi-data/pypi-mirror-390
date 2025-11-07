from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from pyadvincekit import success_response,create_access_token

import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
from services.auth import AuthService

router = APIRouter(prefix="/auth", tags=["认证"])
security = HTTPBearer()
auth_service = AuthService()


class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str
    full_name: str


class LoginRequest(BaseModel):
    username: str
    password: str


@router.post("/register", summary="用户注册")
async def register(request: RegisterRequest):
    """用户注册"""
    return await auth_service.register(
        username=request.username,
        email=request.email,
        password=request.password,
        full_name=request.full_name
    )


@router.post("/login", summary="用户登录")
async def login(request: LoginRequest):
    """用户登录"""
    return await auth_service.login(
        username=request.username,
        password=request.password
    )


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """获取当前登录用户"""
    user = await auth_service.get_current_user(credentials.credentials)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证令牌",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


@router.get("/me", summary="获取当前用户信息")
async def get_me(current_user=Depends(get_current_user)):
    """获取当前用户信息"""
    return success_response(
        data=current_user.to_dict(exclude=["password_hash"]),
        message="获取用户信息成功"
    )


@router.post("/refresh", summary="刷新令牌")
async def refresh_token(current_user=Depends(get_current_user)):
    """刷新访问令牌"""
    new_token = create_access_token(
        data={"sub": current_user.id, "email": current_user.email}
    )

    return success_response(
        data={
            "access_token": new_token,
            "token_type": "bearer",
            "expires_in": 1800
        },
        message="令牌刷新成功"
    )