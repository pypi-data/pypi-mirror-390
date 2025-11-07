"""
认证服务

处理用户认证相关的业务逻辑。
使用PyAdvanceKit的数据库会话管理，无需外部传入AsyncSession。
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from pyadvincekit import BaseCRUD, create_access_token, verify_token, hash_password, get_database
from app.models.user import User
from app.models.auth import UserSession
from pyadvincekit.core.config import get_settings


class AuthService:
    """认证服务类"""
    
    def __init__(self):
        self.user_crud = BaseCRUD(User)
        self.session_crud = BaseCRUD(UserSession)
        self.settings = get_settings()
    
    async def authenticate_user(
        self, 
        email: str, 
        password: str
    ) -> Optional[User]:
        """验证用户
        
        Args:
            email: 邮箱
            password: 密码
            
        Returns:
            验证成功的用户，失败返回None
        """
        # 使用PyAdvanceKit的数据库会话管理
        async with get_database() as db:
            # 根据邮箱查找用户
            users = await self.user_crud.get_multi(
                db, 
                filters={"email": email}, 
                limit=1
            )
            
            if not users:
                return None
            
            user = users[0]
            
            # 验证密码 - 使用模型自带的check_password方法
            if not user.check_password(password):
                return None
            
            # 检查用户状态
            if not user.is_active:
                return None
            
            return user
    
    async def create_user_session(
        self,
        user: User,
        user_agent: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> Dict[str, Any]:
        """创建用户会话
        
        Args:
            user: 用户对象
            user_agent: 用户代理
            ip_address: IP地址
            
        Returns:
            包含令牌信息的字典
        """
        # 使用PyAdvanceKit 创建访问令牌
        access_token = create_access_token(
            subject=str(user.id),
            extra_claims={
                "email": user.email,
                "type": "access"
            }
        )
        
        # 生成JTI（JWT ID）- 用于会话管理
        import uuid
        jti = str(uuid.uuid4())
        
        # 计算过期时间
        expires_at = datetime.now() + timedelta(
            minutes=self.settings.jwt_access_token_expire_minutes
        )
        
        # 使用PyAdvanceKit的数据库会话管理
        async with get_database() as db:
            # 创建会话记录
            session_data = {
                "user_id": user.id,
                "token_jti": jti,
                "user_agent": user_agent,
                "ip_address": ip_address,
                "expires_at": expires_at
            }
            
            await self.session_crud.create(db, session_data)
            
            # 更新用户最后登录时间
            user.last_login_at = datetime.now()
            await db.commit()
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": self.settings.jwt_access_token_expire_minutes * 60,
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "is_active": user.is_active,
                "is_superuser": user.is_superuser,
                "phone": user.phone,
                "avatar": user.avatar,
                "department": user.department,
                "bio": user.bio,
                "last_login_at": user.last_login_at.isoformat() if user.last_login_at else None,
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "updated_at": user.updated_at.isoformat() if user.updated_at else None
            }
        }
    
    async def revoke_user_session(
        self,
        token_jti: str
    ) -> bool:
        """撤销用户会话
        
        Args:
            token_jti: JWT唯一标识
            
        Returns:
            是否成功撤销
        """
        # 使用PyAdvanceKit的数据库会话管理
        async with get_database() as db:
            sessions = await self.session_crud.get_multi(
                db,
                filters={"token_jti": token_jti},
                limit=1
            )
            
            if not sessions:
                return False
            
            session = sessions[0]
            session.revoke()
            await db.commit()
            
            return True
    
    async def cleanup_expired_sessions(self) -> int:
        """清理过期会话
        
        Returns:
            清理的会话数量
        """
        # 使用PyAdvanceKit的数据库会话管理
        async with get_database() as db:
            # 获取所有过期会话
            expired_sessions = await self.session_crud.get_multi(
                db,
                filters={
                    "expires_at": {
                        "operator": "lt",
                        "value": datetime.now()
                    }
                }
            )
            
            # 删除过期会话
            count = 0
            for session in expired_sessions:
                await self.session_crud.delete(db, session.id)
                count += 1
            
            return count
    
    async def change_user_password(
        self,
        user: User,
        current_password: str,
        new_password: str
    ) -> bool:
        """修改用户密码
        
        Args:
            user: 用户对象
            current_password: 当前密码
            new_password: 新密码
            
        Returns:
            是否修改成功
        """
        # 使用PyAdvanceKit的数据库会话管理
        async with get_database() as db:
            # 验证当前密码
            if not user.check_password(current_password):
                return False
            
            # 设置新密码
            user.set_password(new_password)
            await db.commit()
            
            # 撤销所有现有会话（强制重新登录）
            user_sessions = await self.session_crud.get_multi(
                db,
                filters={"user_id": user.id}
            )
            
            for session in user_sessions:
                session.revoke()
            
            await db.commit()
            
            return True


# 创建全局服务实例
auth_service = AuthService()


# 便捷函数
async def authenticate_user(
    email: str, 
    password: str
) -> Optional[User]:
    """验证用户（便捷函数）"""
    return await auth_service.authenticate_user(email, password)


async def create_user_session(
    user: User,
    user_agent: Optional[str] = None,
    ip_address: Optional[str] = None
) -> Dict[str, Any]:
    """创建用户会话（便捷函数）"""
    return await auth_service.create_user_session(
        user, user_agent, ip_address
    )
