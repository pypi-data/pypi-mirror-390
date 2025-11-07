from pyadvincekit import transactional, get_database,BaseCRUD
from models import User, Product
import asyncio
from pyadvincekit import begin_transaction, commit_transaction, rollback_transaction

async def auto_roolback_demo():
    try:
        @transactional(session_param="db")
        async def create_user_with_exception(db):
            """创建用户后抛出异常（应该回滚）"""
            # 使用transactional 注解处理事务时候，需使用原生 SQLAlchemy 操作，不使用 CRUD（避免自动提交）
            user = User(
                username="rollback_user_test2",
                email="rollback1@test.com",
                full_name="Rollback Test User",
                age=30,
                is_active=True
            )
            db.add(user)
            await db.flush()  # 刷新到数据库但不提交
            print(f"  📝 创建用户: {user.username} (ID: {user.id})")
            # 故意抛出异常触发回滚
            i = 1/0
            await db.commit()  # 刷新到数据库但不提交

        # 执行会失败的事务
        try:
            await create_user_with_exception()
            print("  ❌ 异常未被正确抛出")
        except Exception as e:
            print(f"  ❌ 捕获到异常: {e}")
            # 验证回滚效果
            async with get_database() as db:
                user_crud = BaseCRUD(User)
                rollback_users = await user_crud.get_multi(
                    db,
                    filters={"username": "rollback_user_test2"},
                    limit=1
                )

                if not rollback_users:
                    print("  ✅ 事务回滚成功：异常用户未被保存")
                else:
                    print("  ❌ 事务回滚失败：异常用户仍然存在")


    except Exception as e:
        print(f"  ❌ 异常事务测试失败: {e}")


async def manual_transaction_example():
    """手动事务控制示例"""
    session = await begin_transaction()
    try:
        user = User(
            username="manual_rollback_user3",
            email="manual_rollback3@test.com",
            full_name="manual_Rollback Test User",
            age=30,
            is_active=True
        )
        session.add(user)

        i = 1/0

        # 提交事务
        await commit_transaction(session)
        print("✅ 事务提交成功")

    except Exception as e:
        print(f"  ❌ 事务提交失败: {e}")
        # 回滚事务
        await rollback_transaction(session)

        async with get_database() as db:
            user_crud = BaseCRUD(User)
            rollback_users = await user_crud.get_multi(
                db,
                filters={"username": "rollback_user_test3"},
                limit=1
            )

            if not rollback_users:
                print("  ✅ 事务回滚成功：异常用户未被保存")
            else:
                print("  ❌ 事务回滚失败：异常用户仍然存在")




async def main():
    """主函数"""
    # success = await auto_roolback_demo()
    success = await manual_transaction_example()

    if success:
        print(f"\n{'🎊' * 20}")
        print("第一阶段集成测试完全通过！")
        print("PyAdvanceKit 框架改进第一阶段成功！")
        print(f"{'🎊' * 20}")

    return success

if __name__ == '__main__':
    # 运行集成测试
    asyncio.run(main())
