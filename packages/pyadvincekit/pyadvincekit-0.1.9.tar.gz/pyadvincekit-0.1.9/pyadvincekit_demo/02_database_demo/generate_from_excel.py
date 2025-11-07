from pyadvincekit import generate_database_code

def generate_from_excel():
    # 从 Excel 生成完整的数据库代码
    result = generate_database_code(
        excel_file="database_design.xls",

        # 指定各自的输出目录
        orm_output_dir="models",  # ORM对象放到models文件夹
        schema_output_dir="schemas",  # Schema对象放到schemas文件夹
        sql_output_dir="sql",  # SQL文件放到sql文件夹

        # 每个表生成一个文件
        separate_files=True,

        # 自动生成__init__.py
        auto_init_files=True,
        add_standard_fields=True  # 自动添加 id, created_at, updated_at
    )


from pyadvincekit import generate_from_database


async def reverse_engineer_database():
    """数据库逆向工程"""

    # 从现有数据库生成所有代码
    result = await generate_from_database(
        database_url="postgresql://user:pass@localhost/existing_db",  # 不传递url，默认访问.env配置的数据库
        output_dir="reverse_generated",
        separate_files=True,
        auto_init_files=True,
        generate_sql=False,  # 是否生成建表语句
        generate_orm=True,  # 是否生成ORM 对象
        generate_pydantic=True  # 是否生成pydantic对象
    )

    print("逆向工程完成:")
    print(f"   - 处理表数: {result.table_count}")
    print(f"   - 生成文件: {len(result.generated_files)}")

    for file_path in result.generated_files:
        print(f"   - {file_path}")

if __name__ == "__main__":
    generate_from_excel()


