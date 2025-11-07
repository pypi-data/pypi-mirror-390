"""
自动 API 管理器（框架内置）

职责：
- 扫描指定 models 目录，发现 SQLAlchemy 模型
- 读取外部工程提供的配置模块（例如 config.auto_api_config）
- 调用框架的 add_auto_api 自动生成 CRUD 接口

外部工程需提供的配置模块接口：
- get_model_config(model_name) -> dict
- is_model_enabled(model_name) -> bool
- get_enabled_models() -> list[str]
- generate_router_prefix(model_name) -> str
"""

import importlib
import inspect
from pathlib import Path
from typing import List, Dict, Any, Optional, Type

from fastapi import FastAPI


class AutoAPIManager:
    def __init__(self, models_directory: str = "models", config_module: str = "config.auto_api_config") -> None:
        self.models_directory = models_directory
        self.config_module_path = config_module
        self.config_dict = self._load_config_dict(config_module)
        self.discovered_models: Dict[str, Type] = {}
        self.generated_apis: List[Dict[str, Any]] = []

    def _load_config_dict(self, module_path: str) -> Dict[str, Dict[str, Any]]:
        """直接从配置模块加载 AUTO_API_CONFIG 字典"""
        try:
            module = importlib.import_module(module_path)
            if hasattr(module, 'AUTO_API_CONFIG'):
                return module.AUTO_API_CONFIG
            else:
                raise AttributeError(f"配置模块 {module_path} 中未找到 AUTO_API_CONFIG")
        except Exception as exc:
            raise ImportError(f"无法导入配置模块: {module_path}，原因: {exc}")

    def discover_models(self, exclude_files: Optional[List[str]] = None) -> Dict[str, Type]:
        if exclude_files is None:
            exclude_files = ["__init__.py"]

        models: Dict[str, Type] = {}
        models_path = Path(self.models_directory)
        if not models_path.exists():
            return models

        for file_path in models_path.glob("*.py"):
            if file_path.name in exclude_files:
                continue
            try:
                module_name = f"{self.models_directory}.{file_path.stem}"
                module = importlib.import_module(module_name)
                models.update(self._extract_models_from_module(module))
            except Exception:
                # 忽略异常模块，避免中断整体流程
                continue

        self.discovered_models = models
        return models

    def _extract_models_from_module(self, module) -> Dict[str, Type]:
        models: Dict[str, Type] = {}
        for name, obj in inspect.getmembers(module, inspect.isclass):
            if obj.__module__ != module.__name__:
                continue
            # 以是否包含 __tablename__ 作为 SQLAlchemy 模型的特征
            if hasattr(obj, "__tablename__"):
                models[name] = obj
        return models

    def generate_auto_apis(self, app: FastAPI) -> List[Dict[str, Any]]:
        if not self.discovered_models:
            return []

        generated_apis: List[Dict[str, Any]] = []
        for model_name, model_class in self.discovered_models.items():
            try:
                if not self._is_model_enabled(model_name):
                    continue
                cfg: Dict[str, Any] = self._get_model_config(model_name) or {}
                api_cfg = self._build_api_config(model_name, model_class, cfg)

                # 依赖框架 FastAPIWithAutoAPI.add_auto_api 能力
                app.add_auto_api(
                    model_class,
                    router_prefix=api_cfg["router_prefix"],
                    tags=api_cfg["tags"],
                    include_endpoints=api_cfg["include_endpoints"],
                )

                generated_apis.append(api_cfg)
            except Exception:
                # 对单模型失败容错，继续其他模型
                continue

        self.generated_apis = generated_apis
        return generated_apis

    def _get_model_config(self, model_name: str) -> Optional[Dict[str, Any]]:
        """获取指定模型的配置"""
        return self.config_dict.get(model_name)

    def _is_model_enabled(self, model_name: str) -> bool:
        """检查指定模型是否启用了自动 API 生成"""
        return model_name in self.config_dict

    def _get_enabled_models(self) -> List[str]:
        """获取所有启用了自动 API 生成的模型列表"""
        return list(self.config_dict.keys())

    def _build_api_config(self, model_name: str, model_class: Type, config: Dict[str, Any]) -> Dict[str, Any]:
        # 使用框架内置的路由前缀生成函数
        from pyadvincekit.core.auto_api_config import generate_router_prefix
        router_prefix = generate_router_prefix(model_name)
        
        tags = config.get("tags", [f"{model_name}管理"])  # 默认标签
        include_endpoints = config.get("include_endpoints", ["query", "get", "create", "update", "delete"])  # 默认端点

        return {
            "model_name": model_name,
            "model_class": model_class,
            "router_prefix": router_prefix,
            "tags": tags,
            "include_endpoints": include_endpoints,
        }


def auto_discover_and_generate_apis(
    app: FastAPI,
    models_directory: str = "models",
    config_module: str = "config.auto_api_config",
    exclude_files: Optional[List[str]] = None,
) -> AutoAPIManager:
    manager = AutoAPIManager(models_directory=models_directory, config_module=config_module)
    manager.discover_models(exclude_files)
    manager.generate_auto_apis(app)
    return manager



