from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from pyadvincekit import (
    BaseCRUD, get_database, success_response, error_response,
    paginated_response
)
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
from models.user import User
from schemas.user import UserCreate,UserUpdate


# 创建路由器
router = APIRouter(prefix="/users", tags=["用户管理"])

# 创建 CRUD 实例
user_crud = BaseCRUD(User)


# 请求模型
# class UserCreate(BaseModel):
#     username: str
#     email: str
#     full_name: str
#     age: Optional[int] = None
#     is_active: bool = True
#
#
# class UserUpdate(BaseModel):
#     full_name: Optional[str] = None
#     age: Optional[int] = None
#     is_active: Optional[bool] = None


# API 端点
@router.post("/", summary="创建用户")
async def create_user(user_data: UserCreate):
    """创建新用户"""
    async with get_database() as db:
        try:
            user = await user_crud.create(db, user_data.model_dump())
            return success_response(
                data=user.to_dict(),
                message="用户创建成功"
            )
        except Exception as e:
            return error_response(
                message=f"创建用户失败: {str(e)}",
                ret_code="USER_CREATE_FAILED"
            )


@router.get("/{user_id}", summary="获取用户详情")
async def get_user(user_id: str):
    """根据ID获取用户详情"""
    async with get_database() as db:
        try:
            user = await user_crud.get(db, user_id)
            return success_response(
                data=user.to_dict(),
                message="获取用户成功"
            )
        except Exception as e:
            return error_response(
                message="用户不存在",
                ret_code="USER_NOT_FOUND"
            )


@router.get("/", summary="获取用户列表")
async def list_users(
        skip: int = 0,
        limit: int = 20,
        is_active: Optional[bool] = None,
        search: Optional[str] = None
):
    """获取用户列表，支持分页和筛选"""
    async with get_database() as db:
        # 构建过滤条件
        filters = {}
        if is_active is not None:
            filters["is_active"] = is_active
        if search:
            filters["full_name"] = {"operator": "like", "value": f"%{search}%"}

        # 获取数据
        users = await user_crud.get_multi(
            db,
            skip=skip,
            limit=limit,
            filters=filters,
            order_by="created_at",
            order_desc=True
        )

        # 获取总数
        total = await user_crud.count(db, filters=filters)

        # 转换为字典
        user_list = [user.to_dict() for user in users]

        return paginated_response(
            items=user_list,
            total=total,
            page=skip // limit + 1,
            page_size=limit,
            message="获取用户列表成功"
        )


@router.put("/{user_id}", summary="更新用户")
async def update_user(user_id: str, user_data: UserUpdate):
    """更新用户信息"""
    async with get_database() as db:
        try:
            user = await user_crud.get(db, user_id)
            updated_user = await user_crud.update(
                db,
                user,
                user_data.model_dump(exclude_unset=True)
            )
            return success_response(
                data=updated_user.to_dict(),
                message="用户更新成功"
            )
        except Exception as e:
            return error_response(
                message=f"更新用户失败: {str(e)}",
                ret_code="USER_UPDATE_FAILED"
            )


@router.delete("/{user_id}", summary="删除用户")
async def delete_user(user_id: str):
    """删除用户"""
    async with get_database() as db:
        try:
            success = await user_crud.delete(db, user_id)
            if success:
                return success_response(
                    data={"deleted": True},
                    message="用户删除成功"
                )
            else:
                return error_response(
                    message="删除用户失败",
                    ret_code="USER_DELETE_FAILED"
                )
        except Exception as e:
            return error_response(
                message=f"删除用户失败: {str(e)}",
                ret_code="USER_DELETE_ERROR"
            )