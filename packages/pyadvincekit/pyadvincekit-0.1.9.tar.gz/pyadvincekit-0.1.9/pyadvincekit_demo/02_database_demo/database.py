from pyadvincekit import init_database
from models import User, Product


async def initialize_database():
    """初始化数据库"""
    print("📊 正在初始化数据库...")

    # 自动创建所有表
    await init_database()

    print("✅ 数据库初始化完成")


# 在应用启动时调用
if __name__ == "__main__":
    import asyncio

    asyncio.run(initialize_database())

