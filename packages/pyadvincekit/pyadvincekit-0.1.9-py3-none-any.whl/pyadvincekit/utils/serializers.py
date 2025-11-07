"""
序列化工具函数
"""

from typing import Any, Dict, Optional
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.inspection import inspect


def to_camel_case(snake_str: str) -> str:
    """将蛇形命名转换为驼峰命名"""
    if '_' not in snake_str:
        return snake_str.lower()
    
    components = snake_str.split('_')
    return components[0].lower() + ''.join(word.capitalize() for word in components[1:])


def sqlalchemy_to_dict(obj: Any, use_camel_case: bool = True) -> Dict[str, Any]:
    """
    将 SQLAlchemy 对象转换为字典
    
    Args:
        obj: SQLAlchemy 对象
        use_camel_case: 是否转换为驼峰命名
        
    Returns:
        字典表示
    """
    if obj is None:
        return {}
    
    # 获取对象的所有列
    mapper = inspect(obj.__class__)
    result = {}
    
    for column in mapper.columns:
        # 获取列的 Python 属性名
        attr_name = column.key
        # 特殊处理 id 字段，确保使用小写的 id
        if attr_name.upper() == 'ID':
            attr_name = 'id'
        # 获取值
        value = getattr(obj, attr_name, None)

        # if attr_name.upper() == 'id':
        #     result["id"] = getattr()

        # 转换字段名
        if use_camel_case:

            if hasattr(column, 'name') and column.name != attr_name:
                # 使用数据库列名转换
                field_name = to_camel_case(column.name)
            else:
                # 使用属性名转换
                field_name = to_camel_case(attr_name)
        else:
            field_name = attr_name
            
        result[field_name] = value
    
    return result

