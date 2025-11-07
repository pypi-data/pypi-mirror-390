import asyncio
from pyadvincekit import BaseCRUD, get_database
from models import User


async def complex_example():
    """用户 CRUD 操作示例"""
    # 创建 CRUD 实例
    user_crud = BaseCRUD(User)

    async with get_database() as db:
        # 复杂过滤
        young_users = await user_crud.get_multi(
            db,
            filters={"age": {"operator": "lt", "value": 30}}
        )
        print(f"   30岁以下用户: {[u.username for u in young_users]}")
        # 模糊查询
        a_users = await user_crud.get_multi(
            db,
            filters={"username": {"operator": "like", "value": "A"}}
        )
        print(f"   姓名包含'A'的用户: {[u.username for u in a_users]}")

        # 列表过滤
        selected_users = await user_crud.get_multi(
            db,
            filters={"username": ["zhangsan", "Bob"]}
        )
        print(f"   指定姓名用户: {[u.username for u in selected_users]}")

async def main():
    await complex_example()


if __name__ == "__main__":
    asyncio.run(main())