#!/usr/bin/env python3
"""
数据库逆向生成器

提供从数据库连接逆向生成ORM和Schema对象的API
"""

from typing import Dict, List, Optional, Any

from pyadvincekit.logging import get_logger
from pyadvincekit.core.database_extractor import DatabaseMetadataExtractor
from pyadvincekit.core.code_generator import DatabaseCodeGenerator
from pyadvincekit.docs.decorators import api_category, api_doc, api_example

logger = get_logger(__name__)


@api_category("工具类使用", "数据库逆向")
@api_doc(
    title="从数据库逆向生成代码",
    description="连接现有数据库，自动分析表结构并生成ORM模型和Pydantic Schema",
    params={
        "database_url": "数据库连接URL（如：mysql://user:pass@localhost/db）",
        "database_name": "数据库名称（可选，从URL推断）",
        "output_dir": "输出目录（默认：generated_from_db）",
        "orm_output_dir": "ORM模型输出目录（可选）",
        "schema_output_dir": "Schema输出目录（可选）",
        "separate_files": "是否分文件生成（默认：True）",
        "include_tables": "包含的表名列表（可选）",
        "exclude_tables": "排除的表名列表（可选）",
        "add_standard_fields": "是否添加标准字段"
    },
    returns="Dict[str, Any]: 生成的文件信息",
    version="2.0.0"
)
@api_example('''
from pyadvincekit import generate_from_database
import asyncio

# 基础用法：逆向生成整个数据库
async def main():
    # 默认访问.env配置的数据库
    result = await generate_from_database(
        output_dir="./",
    )
    print(f"生成了 {len(result['orm_files'])} 个模型文件")

    # 可选配置参数：
    # result = await generate_from_database(
    #     output_dir="./",
    #     auto_init_files=True, # 是否自动生成 init文件
    #     generate_sql=False,   # 是否自动生成 sql文件
    #     generate_orm=True,   # 是否自动生成 models 对象
    #     generate_pydantic=True  # 是否自动生成 schemas 对象
    # )

if __name__ == "__main__":
    asyncio.run(main())
''', description="数据库逆向工程的多种使用场景")
async def generate_from_database(
    database_url: Optional[str] = None,
    database_name: Optional[str] = None,
    output_dir: str = "generated_from_db",
    
    # 复用现有选项
    orm_output_dir: Optional[str] = None,
    schema_output_dir: Optional[str] = None,
    sql_output_dir: Optional[str] = None,
    separate_files: bool = True,
    auto_init_files: bool = True,
    
    # 过滤选项
    include_tables: Optional[List[str]] = None,
    exclude_tables: Optional[List[str]] = None,
    table_prefix: Optional[str] = None,
    
    # 生成选项
    generate_sql: bool = False,
    generate_orm: bool = True,
    generate_pydantic: bool = True
) -> Dict[str, Any]:
    """
    从数据库逆向生成代码
    
    Args:
        database_url: 可选的数据库连接URL，如果不提供则使用PyAdvanceKit配置
        database_name: 数据库名称
        output_dir: 输出目录
        orm_output_dir: ORM文件输出目录
        schema_output_dir: Schema文件输出目录
        sql_output_dir: SQL文件输出目录
        separate_files: 是否按表分别生成文件
        auto_init_files: 是否自动生成__init__.py文件
        include_tables: 指定要生成的表列表
        exclude_tables: 排除的表列表
        table_prefix: 表名前缀过滤
        generate_sql: 是否生成SQL
        generate_orm: 是否生成ORM
        generate_pydantic: 是否生成Pydantic
    
    Returns:
        生成文件信息的字典
    """
    
    logger.info(f"Starting database reverse generation")
    logger.info(f"Database URL: {'<configured>' if not database_url else database_url}")
    logger.info(f"Output directory: {output_dir}")
    logger.info(f"Separate files: {separate_files}")
    
    # 1. 创建元数据提取器（使用PyAdvanceKit的数据库管理器）
    extractor = DatabaseMetadataExtractor(database_url)
    
    # 2. 提取数据库设计
    design = await extractor.extract_database_design(database_name)
    
    logger.info(f"Extracted {len(design.tables)} tables from database")
    
    # 3. 过滤表
    original_table_count = len(design.tables)
    
    if include_tables:
        design.tables = [t for t in design.tables if t.name in include_tables]
        logger.info(f"Filtered by include_tables: {len(design.tables)} tables remaining")
    
    if exclude_tables:
        design.tables = [t for t in design.tables if t.name not in exclude_tables]
        logger.info(f"Filtered by exclude_tables: {len(design.tables)} tables remaining")
    
    if table_prefix:
        design.tables = [t for t in design.tables if t.name.startswith(table_prefix)]
        logger.info(f"Filtered by table_prefix '{table_prefix}': {len(design.tables)} tables remaining")
    
    if len(design.tables) != original_table_count:
        filtered_table_names = [t.name for t in design.tables]
        logger.info(f"Final table list: {filtered_table_names}")
    
    if not design.tables:
        logger.warning("No tables found after filtering, nothing to generate")
        return {
            "orm_files": [],
            "schema_files": [],
            "sql_files": [],
            "init_files": []
        }
    
    # 4. 使用现有的代码生成器
    generator = DatabaseCodeGenerator()
    
    if separate_files:
        logger.info("Using separate files generation mode")
        return generator.generate_separate_files_from_design(
            design=design,
            output_dir=output_dir,
            orm_output_dir=orm_output_dir,
            schema_output_dir=schema_output_dir,
            sql_output_dir=sql_output_dir,
            generate_sql=generate_sql,
            generate_orm=generate_orm,
            generate_pydantic=generate_pydantic,
            auto_init_files=auto_init_files
        )
    else:
        logger.info("Using single file generation mode")
        return generator.generate_from_design(
            design=design,
            output_dir=output_dir,
            generate_sql=generate_sql,
            generate_orm=generate_orm,
            generate_pydantic=generate_pydantic
        )


# 便捷函数
async def generate_models_from_database(
    database_url: Optional[str] = None,
    output_dir: str = "generated_models",
    include_tables: Optional[List[str]] = None,
    exclude_tables: Optional[List[str]] = None,
    separate_files: bool = True
) -> Dict[str, Any]:
    """
    从数据库生成ORM模型的便捷函数
    
    Args:
        database_url: 数据库连接URL
        output_dir: 输出目录
        include_tables: 包含的表
        exclude_tables: 排除的表
        separate_files: 是否分文件生成
    
    Returns:
        生成文件信息
    """
    return await generate_from_database(
        database_url=database_url,
        output_dir=output_dir,
        include_tables=include_tables,
        exclude_tables=exclude_tables,
        separate_files=separate_files,
        generate_sql=False,
        generate_orm=True,
        generate_pydantic=False
    )


async def generate_schemas_from_database(
    database_url: Optional[str] = None,
    output_dir: str = "generated_schemas",
    include_tables: Optional[List[str]] = None,
    exclude_tables: Optional[List[str]] = None,
    separate_files: bool = True
) -> Dict[str, Any]:
    """
    从数据库生成Pydantic Schema的便捷函数
    
    Args:
        database_url: 数据库连接URL
        output_dir: 输出目录
        include_tables: 包含的表
        exclude_tables: 排除的表
        separate_files: 是否分文件生成
    
    Returns:
        生成文件信息
    """
    return await generate_from_database(
        database_url=database_url,
        output_dir=output_dir,
        include_tables=include_tables,
        exclude_tables=exclude_tables,
        separate_files=separate_files,
        generate_sql=False,
        generate_orm=False,
        generate_pydantic=True
    )


async def generate_all_from_database(
    database_url: Optional[str] = None,
    output_dir: str = "generated_project",
    project_dir: Optional[str] = None,  # 向后兼容
    include_tables: Optional[List[str]] = None,
    exclude_tables: Optional[List[str]] = None,
    generate_api: bool = True,
    generate_service: bool = True,
    generate_sql: bool = False,  # 新增参数：是否生成SQL文件
    separate_files: bool = True,
    auto_init_files: bool = True,
    overwrite_existing: bool = False  # 新增参数：是否覆盖已存在的文件
) -> Dict[str, Any]:
    """
    从数据库生成完整项目结构的便捷函数
    
    Args:
        database_url: 数据库连接URL
        output_dir: 输出目录
        project_dir: 项目目录（向后兼容，优先使用output_dir）
        include_tables: 包含的表
        exclude_tables: 排除的表
        generate_api: 是否生成API层
        generate_service: 是否生成Service层
        generate_sql: 是否生成SQL文件，默认为True
        separate_files: 是否按表分别生成文件
        auto_init_files: 是否自动生成__init__.py文件
        overwrite_existing: 是否覆盖已存在的文件，默认为False（不覆盖）
    
    Returns:
        生成文件信息
    """
    # 向后兼容：如果提供了project_dir但没有output_dir，使用project_dir
    final_output_dir = project_dir if project_dir and output_dir == "generated_project" else output_dir
    
    # 如果需要生成API或Service，需要使用支持这些功能的生成器
    if generate_api or generate_service:
        # 首先从数据库提取表结构
        extractor = DatabaseMetadataExtractor(database_url)
        
        # 提取数据库设计
        design = await extractor.extract_database_design()
        
        # 过滤表
        if include_tables:
            design.tables = [t for t in design.tables if t.name in include_tables]
        if exclude_tables:
            design.tables = [t for t in design.tables if t.name not in exclude_tables]
        
        # 使用支持API/Service生成的代码生成器
        generator = DatabaseCodeGenerator()
        
        # 先生成基础的 ORM 和 Schema
        base_result = generator.generate_separate_files_from_design(
            design=design,
            output_dir=final_output_dir,
            generate_sql=generate_sql,
            generate_orm=True,
            generate_pydantic=True,
            auto_init_files=auto_init_files,
            overwrite_existing=overwrite_existing
        )
        
        # 如果需要生成 API 和 Service，使用 API 生成器
        if generate_api or generate_service:
            api_service_result = {
                "api_files": [],
                "service_files": []
            }
            
            for table in design.tables:
                try:
                    api_service_files = generator.api_service_generator.generate_for_model(
                        table, final_output_dir, overwrite_existing=overwrite_existing
                    )
                    if generate_api and 'api' in api_service_files:
                        api_service_result["api_files"].append(api_service_files['api'])
                    if generate_service and 'service' in api_service_files:
                        api_service_result["service_files"].append(api_service_files['service'])
                except Exception as e:
                    logger.error(f"Failed to generate API/Service for table {table.name}: {e}")
            
            # 合并结果
            base_result.update(api_service_result)
        
        return base_result
    else:
        # 使用原有的生成逻辑
        return await generate_from_database(
            database_url=database_url,
            output_dir=final_output_dir,
            orm_output_dir=f"{final_output_dir}/models",
            schema_output_dir=f"{final_output_dir}/schemas",
            sql_output_dir=f"{final_output_dir}/sql",
            include_tables=include_tables,
            exclude_tables=exclude_tables,
            separate_files=separate_files,
            auto_init_files=auto_init_files,
            generate_sql=True,
            generate_orm=True,
            generate_pydantic=True
        )
























