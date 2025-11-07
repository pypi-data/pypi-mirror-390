import asyncio
from pyadvincekit import BaseCRUD, get_database
from models import User


async def user_crud_example():
    """用户 CRUD 操作示例"""
    # 创建 CRUD 实例
    user_crud = BaseCRUD(User)

    async with get_database() as db:
        # 1. 创建用户
        user_data = {
            "username": "alice",
            "email": "alice@example.com",
            "full_name": "Alice Johnson",
            "age": 28,
            "is_active": True
        }
        user = await user_crud.create(db, user_data)
        print(f"✅ 创建用户: {user.username} (ID: {user.id})")

        # 2. 获取用户
        retrieved_user = await user_crud.get(db, user.id)
        print(f"📖 获取用户: {retrieved_user.full_name}")

        # 3. 更新用户
        update_data = {"full_name": "Alice Williams", "age": 30}
        updated_user = await user_crud.update(db, retrieved_user, update_data)
        print(f"📝 更新用户: {updated_user.full_name}, 年龄: {updated_user.age}")

        # 4. 查询用户列表
        users = await user_crud.get_multi(db, limit=10)
        print(f"📋 用户总数: {len(users)}")

        # 5. 条件查询
        active_users = await user_crud.get_multi(
            db,
            filters={"is_active": True},
            order_by="created_at",
            order_desc=True
        )
        print(f"👥 激活用户: {len(active_users)}")

        # 6. 分页查询
        page1 = await user_crud.get_multi(db, skip=0, limit=5)
        page2 = await user_crud.get_multi(db, skip=5, limit=5)
        print(f"📄 第1页: {len(page1)} 用户")

        # 7. 计数
        total_count = await user_crud.count(db)
        active_count = await user_crud.count(db, filters={"is_active": True})
        print(f"📊 总数: {total_count}, 激活: {active_count}")

        # 8. 检查存在
        exists = await user_crud.exists(db, user.id)
        print(f"🔍 用户存在: {exists}")

        # 9. 删除用户
        success = await user_crud.delete(db, user.id)
        print(f"🗑️ 删除成功: {success}")


async def main():
    await user_crud_example()


if __name__ == "__main__":
    asyncio.run(main())