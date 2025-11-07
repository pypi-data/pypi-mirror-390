"""
API文档装饰器系统

提供 @api_category, @api_doc, @api_example 装饰器
用于标记需要生成文档的API方法
"""

from functools import wraps
from typing import Dict, Any, Optional, List, Callable, Union
import inspect
from .registry import register_api

def api_category(category: str, subcategory: str = None):
    """
    API分类装饰器
    
    Args:
        category: 一级分类，如 "数据库操作"、"工具类"、"认证授权" 等
        subcategory: 二级分类，如 "CRUD操作"、"Excel代码生成"、"JWT认证" 等
    
    Example:
        @api_category("数据库操作", "CRUD操作")
        def get_multi(self, ...):
            pass
            
        @api_category("工具类", "Excel代码生成")
        def generate_database_code(...):
            pass
    """
    def decorator(func):
        # 获取函数信息
        module_name = func.__module__
        func_name = func.__name__
        
        # 注册分类信息
        category_info = {'category': category}
        if subcategory:
            category_info['subcategory'] = subcategory
            
        register_api(func_name, module_name, category_info)
        
        return func
    return decorator

def api_doc(
    title: str,
    description: str,
    params: Optional[Dict[str, str]] = None,
    returns: Optional[str] = None,
    version: Optional[str] = None,
    **kwargs
):
    """
    API文档装饰器
    
    Args:
        title: API标题
        description: API描述
        params: 参数说明字典，格式 {"param_name": "参数说明"}
        returns: 返回值说明
        version: API版本
        **kwargs: 其他扩展信息
    
    Example:
        @api_doc(
            title="批量查询数据",
            description="支持分页、过滤、排序的高级查询功能",
            params={
                "session": "数据库会话",
                "skip": "跳过记录数",
                "limit": "限制返回数量"
            },
            returns="List[ModelType]: 查询结果列表",
            version="2.0.0"
        )
        def get_multi(self, ...):
            pass
    """
    def decorator(func):
        # 获取函数信息
        module_name = func.__module__
        func_name = func.__name__
        
        # 获取函数签名
        sig = inspect.signature(func)
        
        # 构建文档信息
        doc_info = {
            'title': title,
            'description': description,
            'params': params or {},
            'returns': returns,
            'version': version,
            'signature': str(sig),
            'docstring': func.__doc__,
            **kwargs
        }
        
        # 注册文档信息
        register_api(func_name, module_name, {
            'doc_info': doc_info
        })
        
        return func
    return decorator

def api_example(code: str, description: Optional[str] = None, title: Optional[str] = None):
    """
    API示例装饰器
    
    Args:
        code: 示例代码字符串
        description: 示例说明
        title: 示例标题
    
    Example:
        @api_example('''
# 基础查询
users = await user_crud.get_multi(session, skip=0, limit=10)

# 高级查询  
users = await user_crud.get_multi(
    session,
    filters={'status': 'active'},
    or_filters=[{'is_vip': True}],
    order_by='created_at'
)
        ''', description="常用查询示例")
        def get_multi(self, ...):
            pass
    """
    def decorator(func):
        # 获取函数信息
        module_name = func.__module__
        func_name = func.__name__
        
        # 构建示例信息
        example_info = {
            'code': code.strip(),
            'description': description,
            'title': title or f"{func_name} 使用示例"
        }
        
        # 注册示例信息
        register_api(func_name, module_name, {
            'examples': [example_info]  # 这里使用列表，支持多个示例
        })
        
        return func
    return decorator

# 工具函数：支持多个示例的装饰器
def api_examples(*examples: Dict[str, str]):
    """
    多个API示例装饰器
    
    Args:
        *examples: 多个示例字典，每个字典包含 code, description, title
    
    Example:
        @api_examples(
            {"code": "简单示例代码", "description": "简单用法"},
            {"code": "复杂示例代码", "description": "高级用法"}
        )
        def get_multi(self, ...):
            pass
    """
    def decorator(func):
        # 获取函数信息
        module_name = func.__module__
        func_name = func.__name__
        
        # 构建示例列表
        example_list = []
        for i, example in enumerate(examples):
            example_info = {
                'code': example.get('code', '').strip(),
                'description': example.get('description'),
                'title': example.get('title', f"{func_name} 示例 {i+1}")
            }
            example_list.append(example_info)
        
        # 注册示例信息
        register_api(func_name, module_name, {
            'examples': example_list
        })
        
        return func
    return decorator

def api_table(title: str, table_data: str, description: Optional[str] = None):
    """
    API表格装饰器
    
    Args:
        title: 表格标题
        table_data: 表格的Markdown格式数据
        description: 表格说明
    
    Example:
        @api_table(
            title="支持的operator操作",
            table_data='''
| operator操作 | 含义                     | 示例                                                      |
| ------------ | ------------------------ | --------------------------------------------------------- |
| like         | 区分大小写的模糊匹配 %A% | filters={"username": {"operator": "like", "value": "A"}}  |
| ilike        | 不区分大小写的模糊匹配   | filters={"username": {"operator": "ilike", "value": "A"}} |
| gt           | 大于 >                   | filters={"age": {"operator": "gt", "value": 30}}          |
            ''',
            description="这些操作符让您能够进行精确和灵活的数据查询"
        )
        def get_multi(self, ...):
            pass
    """
    def decorator(func):
        # 获取函数信息
        module_name = func.__module__
        func_name = func.__name__
        
        # 构建表格信息
        table_info = {
            'title': title,
            'table_data': table_data.strip(),
            'description': description
        }
        
        # 注册表格信息
        register_api(func_name, module_name, {
            'table': table_info
        })
        
        return func
    return decorator