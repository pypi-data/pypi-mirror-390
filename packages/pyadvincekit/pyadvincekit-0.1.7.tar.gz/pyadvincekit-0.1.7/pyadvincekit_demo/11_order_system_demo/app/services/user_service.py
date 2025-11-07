"""
用户服务

处理用户管理相关的业务逻辑。
使用PyAdvanceKit的数据库会话管理，无需外部传入AsyncSession。
"""

from typing import Optional

from app.models.user import User
from app.schemas.user import UserCreate
from pyadvincekit import BaseCRUD, hash_password, get_database


class UserService:
    """用户服务类"""
    
    def __init__(self):
        self.user_crud = BaseCRUD(User)

    async def get_user_by_id(
            self,
            user_id: str
    ) -> Optional[User]:
        """根据ID获取用户

        Args:
            user_id: 用户ID

        Returns:
            用户对象或None
        """
        # 使用PyAdvanceKit的数据库会话管理
        async with get_database() as db:
            return await self.user_crud.get(db, user_id, raise_not_found=False)

    async def get_user_by_email(
        self, 
        email: str
    ) -> Optional[User]:
        """根据邮箱获取用户
        
        Args:
            email: 邮箱地址
            
        Returns:
            用户对象或None
        """
        # 使用PyAdvanceKit的数据库会话管理
        async with get_database() as db:
            users = await self.user_crud.get_multi(
                db, 
                filters={"email": email}, 
                limit=1
            )
            return users[0] if users else None
    
    async def create_user(
        self, 
        user_data: UserCreate
    ) -> User:
        """创建用户
        
        Args:
            user_data: 用户创建数据
            
        Returns:
            创建的用户对象
            
        Raises:
            ValueError: 邮箱已存在时抛出异常
        """
        # 使用PyAdvanceKit的数据库会话管理
        async with get_database() as db:
            # 检查邮箱是否已存在
            existing_user = await self.get_user_by_email(user_data.email)
            if existing_user:
                raise ValueError(f"Email {user_data.email} already registered")
            
            # 准备用户数据
            user_dict = user_data.model_dump(exclude={'password'})
            # hash_password返回(hashed_password, salt)元组
            hashed_password, salt = hash_password(user_data.password)
            # 存储格式为 "hash:salt"
            user_dict['hashed_password'] = f"{hashed_password}:{salt}"
            
            # 创建用户
            user = await self.user_crud.create(db, user_dict)
            return user

# 创建全局服务实例
user_service = UserService()

# 便捷函数
async def get_user_by_id(user_id: str) -> Optional[User]:
    """根据ID获取用户（便捷函数）"""
    return await user_service.get_user_by_id(user_id)


async def get_user_by_email(email: str) -> Optional[User]:
    """根据邮箱获取用户（便捷函数）"""
    return await user_service.get_user_by_email(email)


async def create_user(user_data: UserCreate) -> User:
    """创建用户（便捷函数）"""
    return await user_service.create_user(user_data)

