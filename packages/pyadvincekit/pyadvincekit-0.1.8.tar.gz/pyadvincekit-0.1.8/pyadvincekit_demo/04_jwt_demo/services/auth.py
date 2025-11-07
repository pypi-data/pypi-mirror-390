from pyadvincekit import (
    BaseCRUD, get_database, create_access_token, verify_token,
    hash_password, success_response, error_response
)
from pyadvincekit.utils import verify_password
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
from models.user import User    
from datetime import timedelta


class AuthService:
    """认证服务"""

    def __init__(self):
        self.user_crud = BaseCRUD(User)

    async def register(self, username: str, email: str, password: str, full_name: str):
        """用户注册"""
        async with get_database() as db:
            # 检查用户是否已存在
            existing_user = await self.user_crud.get_multi(
                db,
                filters={"username": username}
            )
            if existing_user:
                return error_response(
                    message="用户名已存在",
                    ret_code="USERNAME_EXISTS"
                )

            existing_email = await self.user_crud.get_multi(
                db,
                filters={"email": email}
            )
            if existing_email:
                return error_response(
                    message="邮箱已被使用",
                    ret_code="EMAIL_EXISTS"
                )

            # # 创建用户
            # user = User()
            # user.username = username
            # user.email = email
            # user.full_name = full_name
            # user.hashed_password = user.set_password(password)
            # user.is_active = True

            user_data = {
                "username": username,
                "email": email,
                "full_name": full_name,
                "is_active": True
            }

            hashed_password, salt = hash_password(password)
            # 存储格式为 "hash:salt"
            user_data['hashed_password'] = f"{hashed_password}:{salt}"

            user = await self.user_crud.create(db, user_data)

            # 生成令牌
            access_token = create_access_token(
                subject=user.id
            )

            return success_response(
                data={
                    "access_token": access_token,
                    "token_type": "bearer",
                    "expires_in": 1800,  # 30分钟
                    "user": user.to_dict(exclude=["hashed_password"])
                },
                message="注册成功"
            )

    async def login(self, username: str, password: str):
        """用户登录"""
        async with get_database() as db:
            # 查找用户
            users = await self.user_crud.get_multi(
                db,
                filters={"username": username}
            )

            if not users:
                return error_response(
                    message="用户名或密码错误",
                    ret_code="INVALID_CREDENTIALS"
                )

            user = users[0]

            # 验证密码
            if not user.check_password(password):
                return error_response(
                    message="用户名或密码错误",
                    ret_code="INVALID_CREDENTIALS"
                )
            # 验证密码
            # if not verify_password(password, user.hashed_password):
            #     return error_response(
            #         message="用户名或密码错误",
            #         ret_code="INVALID_CREDENTIALS"
            #     )

            # 检查用户状态
            if not user.is_active:
                return error_response(
                    message="账户已被禁用",
                    ret_code="ACCOUNT_DISABLED"
                )

            # 生成令牌
            access_token = create_access_token(
                subject=user.id
            )



            return success_response(
                data={
                    "access_token": access_token,
                    "token_type": "bearer",
                    "expires_in": 1800,
                    "user": user.to_dict(exclude=["hashed_password"])
                },
                message="登录成功"
            )

    async def get_current_user(self, token: str):
        """获取当前用户"""
        try:
            payload = verify_token(token)
            user_id = payload.get("sub")

            if not user_id:
                return None

            async with get_database() as db:
                user = await self.user_crud.get(db, user_id)
                return user

        except Exception:
            return None