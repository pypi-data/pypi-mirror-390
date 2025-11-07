from pyadvincekit import generate_from_database
import asyncio

async def database_reverse_generation():
    result = await generate_from_database(
                    database_url="postgresql://user:pass@localhost/existing_db",  # 不传递url，默认访问.env配置的数据库
                    output_dir="reverse_generated",
                    separate_files=True,
                    auto_init_files=True,
                    generate_sql=False,
                    generate_orm=True,
                    generate_pydantic=True
                )

if __name__ == '__main__':
    asyncio.run(database_reverse_generation())