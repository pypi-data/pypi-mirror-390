"""
API文档注册表

全局存储被装饰器标记的API信息
"""

from typing import Dict, Any, List, Optional
import threading
from collections import defaultdict

# 全局API注册表
API_REGISTRY: Dict[str, Any] = {}

# 线程锁，确保并发安全
_registry_lock = threading.Lock()

def register_api(func_name: str, module_name: str, api_info: Dict[str, Any]) -> None:
    """注册API信息到全局注册表"""
    with _registry_lock:
        full_name = f"{module_name}.{func_name}"
        
        if full_name not in API_REGISTRY:
            API_REGISTRY[full_name] = {
                'function_name': func_name,
                'module_name': module_name,
                'full_name': full_name,
                'category': None,
                'doc_info': None,
                'examples': []
            }
        
        # 合并API信息
        API_REGISTRY[full_name].update(api_info)

def get_registry() -> Dict[str, Any]:
    """获取完整的API注册表"""
    with _registry_lock:
        return API_REGISTRY.copy()

def get_apis_by_category() -> Dict[str, List[Dict[str, Any]]]:
    """按分类获取API列表"""
    with _registry_lock:
        categorized = defaultdict(list)
        
        for api_name, api_info in API_REGISTRY.items():
            category = api_info.get('category', '未分类')
            categorized[category].append(api_info)
        
        return dict(categorized)

def clear_registry() -> None:
    """清空注册表（主要用于测试和热重载）"""
    with _registry_lock:
        API_REGISTRY.clear()

def get_api_count() -> int:
    """获取已注册API数量"""
    with _registry_lock:
        return len(API_REGISTRY)