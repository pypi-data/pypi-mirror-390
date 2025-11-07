"""
PyAdvanceKit 自动文档生成系统

通过装饰器标记API方法，自动生成在线文档。
"""

from .decorators import api_category, api_doc, api_example, api_table
from .registry import API_REGISTRY, get_registry, register_api
from .scanner import APIDocScanner
from .file_scanner import FileBasedAPIScanner

__all__ = [
    'api_category',
    'api_doc', 
    'api_example',
    'api_table',
    'API_REGISTRY',
    'get_registry',
    'register_api',
    'APIDocScanner',
    'FileBasedAPIScanner'
]