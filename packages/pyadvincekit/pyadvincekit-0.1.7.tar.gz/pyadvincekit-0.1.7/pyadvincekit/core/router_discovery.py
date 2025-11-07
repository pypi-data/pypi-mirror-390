"""
路由自动发现模块（框架内置）

提供在给定目录下自动扫描并加载 FastAPI APIRouter 的能力。
外部工程只需调用 auto_discover_and_register_routers 即可获取路由列表。
"""

import importlib
import inspect
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter


class RouterDiscovery:
    """路由自动发现器"""

    def __init__(self, api_directory: str = "api") -> None:
        self.api_directory = api_directory
        self.discovered_routers: List[APIRouter] = []

    def discover_routers(self, exclude_files: Optional[List[str]] = None) -> List[APIRouter]:
        if exclude_files is None:
            exclude_files = ["__init__.py"]

        routers: List[APIRouter] = []
        api_path = Path(self.api_directory)
        
        print(f"🔍 路由发现: 检查目录 {api_path.absolute()}")
        
        if not api_path.exists():
            print(f"❌ API 目录不存在: {api_path.absolute()}")
            return routers

        py_files = list(api_path.glob("*.py"))
        print(f"📁 发现 {len(py_files)} 个 Python 文件")
        
        for file_path in py_files:
            print(f"📄 检查文件: {file_path.name}")
            
            if file_path.name in exclude_files:
                print(f"⏭️  跳过排除文件: {file_path.name}")
                continue

            try:
                module_name = f"{self.api_directory}.{file_path.stem}"
                print(f"📦 尝试导入模块: {module_name}")
                module = importlib.import_module(module_name)
                print(f"✅ 模块导入成功: {module}")
                
                router = self._extract_router_from_module(module)
                if router:
                    print(f"🎯 找到路由: {router.prefix}, 标签: {router.tags}")
                    routers.append(router)
                else:
                    print(f"❌ 模块中未找到路由: {module_name}")
                    
            except Exception as e:
                print(f"❌ 导入模块失败: {module_name}, 错误: {e}")
                import traceback
                traceback.print_exc()
                continue

        self.discovered_routers = routers
        print(f"🎉 路由发现完成，共找到 {len(routers)} 个路由")
        return routers

    def _extract_router_from_module(self, module) -> Optional[APIRouter]:
        # 优先 router 变量
        if hasattr(module, "router"):
            router_obj = getattr(module, "router")
            if isinstance(router_obj, APIRouter):
                return router_obj

        # 次选：任意 APIRouter 实例
        for _, obj in inspect.getmembers(module):
            if isinstance(obj, APIRouter):
                return obj
        return None


def auto_discover_and_register_routers(
    api_directory: str = "api",
    exclude_files: Optional[List[str]] = None,
) -> List[APIRouter]:
    discovery = RouterDiscovery(api_directory)
    return discovery.discover_routers(exclude_files)


def discover_routers(api_directory: str = "api") -> List[APIRouter]:
    return auto_discover_and_register_routers(api_directory)






