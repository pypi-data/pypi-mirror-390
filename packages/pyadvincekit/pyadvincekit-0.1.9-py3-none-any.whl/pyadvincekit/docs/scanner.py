"""
API文档扫描器

自动扫描包中被装饰器标记的API方法，生成文档结构
"""

import os
import importlib
import inspect
import pkgutil
from typing import Dict, Any, List, Optional, Set
from pathlib import Path
import logging
from .registry import get_registry, get_apis_by_category, clear_registry

logger = logging.getLogger(__name__)

class APIDocScanner:
    """API文档扫描器"""
    
    def __init__(self, base_package: str = "pyadvincekit"):
        self.base_package = base_package
        self.scanned_modules: Set[str] = set()
        
    def scan_package(self, clear_existing: bool = True) -> Dict[str, Any]:
        """
        扫描包下所有标记的API
        
        Args:
            clear_existing: 是否清空现有注册表
            
        Returns:
            扫描结果统计信息
        """
        if clear_existing:
            clear_registry()
            self.scanned_modules.clear()
            # 清空模块缓存，强制重新导入以执行装饰器
            self._clear_module_cache()
        
        logger.info(f"开始扫描包: {self.base_package}")
        
        try:
            # 导入基础包
            base_module = importlib.import_module(self.base_package)
            
            # 递归扫描所有子模块
            self._scan_module_recursive(base_module)
            
            # 获取扫描结果
            registry = get_registry()
            categorized = get_apis_by_category()
            
            result = {
                'total_apis': len(registry),
                'categories': list(categorized.keys()),
                'apis_by_category': {cat: len(apis) for cat, apis in categorized.items()},
                'scanned_modules': list(self.scanned_modules),
                'registry': registry
            }
            
            logger.info(f"扫描完成: 发现 {result['total_apis']} 个API，{len(result['categories'])} 个分类")
            return result
            
        except Exception as e:
            logger.error(f"扫描包时出错: {e}")
            return {
                'total_apis': 0,
                'categories': [],
                'apis_by_category': {},
                'scanned_modules': [],
                'registry': {},
                'error': str(e)
            }
    
    def _scan_module_recursive(self, module) -> None:
        """递归扫描模块"""
        module_name = module.__name__
        
        if module_name in self.scanned_modules:
            return
            
        self.scanned_modules.add(module_name)
        logger.debug(f"扫描模块: {module_name}")
        
        try:
            # 扫描当前模块中的函数和类
            self._scan_module_members(module)
            
            # 递归扫描子模块
            if hasattr(module, '__path__'):
                for finder, name, ispkg in pkgutil.iter_modules(module.__path__, module.__name__ + "."):
                    if name not in self.scanned_modules:
                        try:
                            submodule = importlib.import_module(name)
                            self._scan_module_recursive(submodule)
                        except Exception as e:
                            logger.warning(f"无法导入子模块 {name}: {e}")
                            
        except Exception as e:
            logger.warning(f"扫描模块 {module_name} 时出错: {e}")
    
    def _scan_module_members(self, module) -> None:
        """扫描模块成员（函数和类方法）"""
        for name, obj in inspect.getmembers(module):
            try:
                # 扫描函数
                if inspect.isfunction(obj):
                    self._check_function_for_docs(obj)
                
                # 扫描类方法  
                elif inspect.isclass(obj):
                    self._scan_class_methods(obj)
                    
            except Exception as e:
                logger.debug(f"扫描成员 {name} 时出错: {e}")
    
    def _scan_class_methods(self, cls) -> None:
        """扫描类中的方法"""
        for name, method in inspect.getmembers(cls, predicate=inspect.isfunction):
            try:
                self._check_function_for_docs(method)
            except Exception as e:
                logger.debug(f"扫描类方法 {cls.__name__}.{name} 时出错: {e}")
    
    def _check_function_for_docs(self, func) -> None:
        """检查函数是否在文档注册表中"""
        # 这里不需要主动检查，因为装饰器已经自动注册了
        # 但我们可以在这里做一些额外的处理，比如提取类型注解等
        pass
    
    def _clear_module_cache(self) -> None:
        """清空相关模块缓存，强制重新导入以执行装饰器"""
        import sys
        
        # 需要清空的模块模式
        modules_to_clear = [
            name for name in sys.modules.keys() 
            if name.startswith(self.base_package)
        ]
        
        logger.debug(f"清空模块缓存: {len(modules_to_clear)} 个模块")
        
        # 从sys.modules中移除这些模块
        for module_name in modules_to_clear:
            if module_name in sys.modules:
                del sys.modules[module_name]
                logger.debug(f"清空模块缓存: {module_name}")
        
        # 特别处理装饰器模块，确保它们被重新导入
        decorator_modules = [
            f"{self.base_package}.docs.decorators",
            f"{self.base_package}.docs.registry"
        ]
        
        for module_name in decorator_modules:
            if module_name in sys.modules:
                del sys.modules[module_name]
                logger.debug(f"强制清空装饰器模块: {module_name}")
        
        # 重新导入核心模块以确保装饰器工作
        try:
            importlib.import_module(f"{self.base_package}.docs.decorators")
            importlib.import_module(f"{self.base_package}.docs.registry")
            logger.debug("重新导入装饰器模块成功")
        except Exception as e:
            logger.warning(f"重新导入装饰器模块失败: {e}")
    
    def get_docs_structure(self) -> Dict[str, Any]:
        """生成文档结构（用于左侧菜单）"""
        categorized = get_apis_by_category()
        
        structure = {}
        for category, apis in categorized.items():
            # 生成分类的安全标识符
            category_id = self._safe_id(category)
            
            structure[category_id] = {
                'title': category,
                'items': []
            }
            
            for api in apis:
                api_id = self._safe_id(api['function_name'])
                structure[category_id]['items'].append({
                    'id': api_id,
                    'title': api.get('doc_info', {}).get('title', api['function_name']),
                    'file': f"{category_id}/{api_id}",
                    'api_info': api
                })
        
        return structure
    
    def get_docs_content(self) -> Dict[str, Any]:
        """生成文档内容"""
        content = {}
        categorized = get_apis_by_category()
        
        for category, apis in categorized.items():
            category_id = self._safe_id(category)
            
            for api in apis:
                api_id = self._safe_id(api['function_name'])
                doc_key = f"{category_id}/{api_id}"
                
                content[doc_key] = {
                    'title': api.get('doc_info', {}).get('title', api['function_name']),
                    'content': self._generate_api_markdown(api)
                }
        
        return content
    
    def _generate_api_markdown(self, api_info: Dict[str, Any]) -> str:
        """为API生成Markdown文档"""
        doc_info = api_info.get('doc_info', {})
        examples = api_info.get('examples', [])
        
        md_lines = []
        
        # 标题
        title = doc_info.get('title', api_info['function_name'])
        md_lines.append(f"# {title}")
        md_lines.append("")
        
        # 描述
        description = doc_info.get('description')
        if description:
            md_lines.append(description)
            md_lines.append("")
        
        # 函数签名
        signature = doc_info.get('signature')
        if signature:
            md_lines.append("## 函数签名")
            md_lines.append("```python")
            md_lines.append(f"def {api_info['function_name']}{signature}")
            md_lines.append("```")
            md_lines.append("")
        
        # 参数说明
        params = doc_info.get('params', {})
        if params:
            md_lines.append("## 参数说明")
            md_lines.append("")
            for param_name, param_desc in params.items():
                md_lines.append(f"- **{param_name}**: {param_desc}")
            md_lines.append("")
        
        # 返回值
        returns = doc_info.get('returns')
        if returns:
            md_lines.append("## 返回值")
            md_lines.append("")
            md_lines.append(returns)
            md_lines.append("")
        
        # 示例代码
        if examples:
            md_lines.append("## 使用示例")
            md_lines.append("")
            
            for i, example in enumerate(examples):
                if len(examples) > 1:
                    example_title = example.get('title', f"示例 {i+1}")
                    md_lines.append(f"### {example_title}")
                    md_lines.append("")
                
                example_desc = example.get('description')
                if example_desc:
                    md_lines.append(example_desc)
                    md_lines.append("")
                
                md_lines.append("```python")
                md_lines.append(example['code'])
                md_lines.append("```")
                md_lines.append("")
        
        # 版本信息
        version = doc_info.get('version')
        if version:
            md_lines.append(f"**版本**: {version}")
            md_lines.append("")
        
        # 模块信息
        md_lines.append("---")
        md_lines.append(f"**模块**: `{api_info['module_name']}`")
        md_lines.append("")
        
        return "\n".join(md_lines)
    
    def _safe_id(self, name: str) -> str:
        """生成安全的标识符"""
        # 将中文和特殊字符转换为安全的ID
        import re
        # 简单的转换规则
        safe_name = re.sub(r'[^\w\u4e00-\u9fff]', '-', name)
        safe_name = re.sub(r'-+', '-', safe_name).strip('-')
        return safe_name.lower() if safe_name else 'unnamed'