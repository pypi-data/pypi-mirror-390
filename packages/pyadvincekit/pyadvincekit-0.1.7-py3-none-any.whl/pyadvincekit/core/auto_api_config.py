"""
自动 API 配置工具（框架内置）

提供通用的配置验证、工具函数等，外部项目只需定义具体的配置变量。
"""

import re
from typing import Dict, Any, List, Optional


# 📋 可用端点定义
AVAILABLE_ENDPOINTS = [
    "query",    # 查询列表 - POST /model/query
    "get",      # 获取单个 - POST /model/get
    "create",   # 创建 - POST /model/create
    "update",   # 更新 - POST /model/update
    "delete",   # 删除 - POST /model/delete
    "count"     # 统计 - POST /model/count
]


def generate_router_prefix(model_name: str) -> str:
    """
    根据模型名称生成路由前缀
    
    Args:
        model_name: 模型名称（如 User, Department）
        
    Returns:
        路由前缀（如 /users, /departments）
    """
    # 将驼峰命名转换为小写复数形式
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', model_name)
    s2 = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
    
    # 简单的复数化规则
    if s2.endswith('y'):
        plural = s2[:-1] + 'ies'
    elif s2.endswith(('s', 'sh', 'ch', 'x', 'z')):
        plural = s2 + 'es'
    else:
        plural = s2 + 's'
    
    return f"/{plural}"


def validate_config(config: Dict[str, Dict[str, Any]]) -> bool:
    """
    验证配置文件的正确性
    
    Args:
        config: 自动 API 配置字典
        
    Returns:
        验证是否通过
        
    Raises:
        ValueError: 配置验证失败时抛出异常
    """
    errors = []
    
    for model_name, model_config in config.items():
        # 检查必需字段
        if "tags" not in model_config:
            errors.append(f"{model_name}: 缺少 'tags' 配置")
        
        if "include_endpoints" not in model_config:
            errors.append(f"{model_name}: 缺少 'include_endpoints' 配置")
        
        # 检查端点配置
        include_endpoints = model_config.get("include_endpoints", [])
        
        for endpoint in include_endpoints:
            if endpoint not in AVAILABLE_ENDPOINTS:
                errors.append(f"{model_name}: 无效的端点 '{endpoint}'，可用端点: {AVAILABLE_ENDPOINTS}")
    
    if errors:
        raise ValueError("配置验证失败:\n" + "\n".join(errors))
    
    return True


class AutoAPIConfigHelper:
    """自动 API 配置助手类"""
    
    def __init__(self, config: Dict[str, Dict[str, Any]]):
        self.config = config
        self.validate()
    
    def validate(self) -> bool:
        """验证配置"""
        return validate_config(self.config)
    
    def get_model_config(self, model_name: str) -> Optional[Dict[str, Any]]:
        """获取指定模型的配置"""
        return self.config.get(model_name)
    
    def is_model_enabled(self, model_name: str) -> bool:
        """检查指定模型是否启用了自动 API 生成"""
        return model_name in self.config
    
    def get_enabled_models(self) -> List[str]:
        """获取所有启用了自动 API 生成的模型列表"""
        return list(self.config.keys())
    
    def get_router_prefix(self, model_name: str) -> str:
        """获取模型的路由前缀"""
        return generate_router_prefix(model_name)
    
    def get_tags(self, model_name: str) -> List[str]:
        """获取模型的标签"""
        config = self.get_model_config(model_name)
        return config.get("tags", [f"{model_name}管理"]) if config else []
    
    def get_include_endpoints(self, model_name: str) -> List[str]:
        """获取模型包含的端点"""
        config = self.get_model_config(model_name)
        return config.get("include_endpoints", ["query", "get", "create", "update", "delete"]) if config else []


def create_config_helper(config: Dict[str, Dict[str, Any]]) -> AutoAPIConfigHelper:
    """
    创建配置助手实例
    
    Args:
        config: 自动 API 配置字典
        
    Returns:
        配置助手实例
    """
    return AutoAPIConfigHelper(config)


# 为了兼容外部项目的函数调用方式，提供这些函数
def get_model_config_from_dict(config: Dict[str, Dict[str, Any]], model_name: str) -> Optional[Dict[str, Any]]:
    """从配置字典获取模型配置"""
    return config.get(model_name)


def is_model_enabled_in_dict(config: Dict[str, Dict[str, Any]], model_name: str) -> bool:
    """检查模型在配置字典中是否启用"""
    return model_name in config


def get_enabled_models_from_dict(config: Dict[str, Dict[str, Any]]) -> List[str]:
    """从配置字典获取启用的模型列表"""
    return list(config.keys())



















