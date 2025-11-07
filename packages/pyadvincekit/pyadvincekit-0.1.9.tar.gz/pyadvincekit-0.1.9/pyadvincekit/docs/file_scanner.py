#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
基于文件扫描的API发现器
直接从源代码文件中扫描装饰器，不依赖模块导入
"""

import os
import re
import ast
from typing import Dict, List, Any, Optional
from pathlib import Path
import logging
from .registry import register_api, get_registry, clear_registry, get_apis_by_category

logger = logging.getLogger(__name__)

class FileBasedAPIScanner:
    """基于文件的API扫描器"""
    
    def __init__(self, base_path: str = "pyadvincekit"):
        self.base_path = Path(base_path)
        
    def scan_package(self, clear_existing: bool = True) -> Dict[str, Any]:
        """扫描整个项目，与原APIDocScanner接口兼容"""
        if clear_existing:
            clear_registry()
        
        logger.info(f"开始扫描包: {self.base_path}")
        
        # 递归扫描所有.py文件
        python_files = list(self.base_path.rglob("*.py"))
        logger.debug(f"找到 {len(python_files)} 个Python文件")
        
        total_apis = 0
        scanned_files = []
        
        for py_file in python_files:
            try:
                apis = self.scan_file(py_file)
                if apis:
                    total_apis += len(apis)
                    scanned_files.append(str(py_file))
                    logger.debug(f"{py_file.name}: 发现 {len(apis)} 个API")
            except Exception as e:
                logger.warning(f"扫描文件失败 {py_file}: {e}")
        
        # 获取扫描结果
        registry = get_registry()
        categorized = get_apis_by_category()
        
        result = {
            'total_apis': len(registry),
            'categories': list(categorized.keys()),
            'apis_by_category': {cat: len(apis) for cat, apis in categorized.items()},
            'scanned_modules': scanned_files,  # 这里用文件列表代替模块列表
            'registry': registry
        }
        
        logger.info(f"扫描完成: 发现 {result['total_apis']} 个API，{len(result['categories'])} 个分类")
        return result
    
    def scan_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """扫描单个文件"""
        apis = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 解析AST
            tree = ast.parse(content)
            
            # 查找带装饰器的函数
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    api_info = self.extract_api_info(node, file_path, content)
                    if api_info:
                        apis.append(api_info)
                        
                        # 注册到全局注册表
                        module_name = self.get_module_name(file_path)
                        func_name = api_info['function_name']
                        register_api(func_name, module_name, api_info)
        
        except Exception as e:
            logger.warning(f"解析文件出错 {file_path}: {e}")
        
        return apis
    
    def extract_api_info(self, func_node, file_path: Path, content: str) -> Optional[Dict[str, Any]]:
        """从函数节点提取API信息"""
        
        # 检查是否有相关装饰器
        api_decorators = []
        for decorator in func_node.decorator_list:
            decorator_name = self.get_decorator_name(decorator)
            if decorator_name in ['api_category', 'api_doc', 'api_example']:
                api_decorators.append((decorator_name, decorator))
        
        if not api_decorators:
            return None
        
        # 构建API信息
        module_name = self.get_module_name(file_path)
        func_name = func_node.name
        
        api_info = {
            'function_name': func_name,
            'module_name': module_name,
            'full_name': f"{module_name}.{func_name}",
            'file_path': str(file_path),
            'line_number': func_node.lineno,
            'category': None,
            'subcategory': None,
            'doc_info': {},
            'examples': []
        }
        
        # 解析每个装饰器
        for decorator_name, decorator_node in api_decorators:
            if decorator_name == 'api_category':
                category_info = self.parse_api_category(decorator_node)
                api_info.update(category_info)
            elif decorator_name == 'api_doc':
                doc_info = self.parse_api_doc(decorator_node)
                api_info['doc_info'] = doc_info
            elif decorator_name == 'api_example':
                example_info = self.parse_api_example(decorator_node)
                if example_info:
                    api_info['examples'].append(example_info)
        
        # 获取函数签名
        api_info['signature'] = self.get_function_signature(func_node)
        
        # 获取docstring
        api_info['docstring'] = ast.get_docstring(func_node)
        
        return api_info
    
    def get_decorator_name(self, decorator) -> str:
        """获取装饰器名称"""
        if isinstance(decorator, ast.Name):
            return decorator.id
        elif isinstance(decorator, ast.Call) and isinstance(decorator.func, ast.Name):
            return decorator.func.id
        elif isinstance(decorator, ast.Attribute):
            return decorator.attr
        return ""
    
    def parse_api_category(self, decorator_node) -> Dict[str, Any]:
        """解析 @api_category 装饰器"""
        result = {}
        
        if isinstance(decorator_node, ast.Call):
            # 获取参数
            args = []
            for arg in decorator_node.args:
                if isinstance(arg, ast.Constant):
                    args.append(arg.value)
                elif isinstance(arg, ast.Str):  # Python < 3.8
                    args.append(arg.s)
            
            if len(args) >= 1:
                result['category'] = args[0]
            if len(args) >= 2:
                result['subcategory'] = args[1]
                
            # 处理关键字参数
            for keyword in decorator_node.keywords:
                if keyword.arg == 'subcategory' and isinstance(keyword.value, (ast.Constant, ast.Str)):
                    value = keyword.value.value if isinstance(keyword.value, ast.Constant) else keyword.value.s
                    result['subcategory'] = value
        
        return result
    
    def parse_api_doc(self, decorator_node) -> Dict[str, Any]:
        """解析 @api_doc 装饰器"""
        doc_info = {}
        
        if isinstance(decorator_node, ast.Call):
            # 处理关键字参数
            for keyword in decorator_node.keywords:
                if keyword.arg in ['title', 'description', 'returns', 'version']:
                    value = self.get_ast_value(keyword.value)
                    if value:
                        doc_info[keyword.arg] = value
                elif keyword.arg == 'params':
                    params = self.parse_dict_value(keyword.value)
                    if params:
                        doc_info['params'] = params
        
        return doc_info
    
    def parse_api_example(self, decorator_node) -> Optional[Dict[str, Any]]:
        """解析 @api_example 装饰器"""
        example_info = {}
        
        if isinstance(decorator_node, ast.Call):
            # 获取位置参数（代码）
            if decorator_node.args:
                code = self.get_ast_value(decorator_node.args[0])
                if code:
                    example_info['code'] = code.strip()
            
            # 处理关键字参数
            for keyword in decorator_node.keywords:
                if keyword.arg in ['description', 'title']:
                    value = self.get_ast_value(keyword.value)
                    if value:
                        example_info[keyword.arg] = value
        
        return example_info if example_info else None
    
    def get_ast_value(self, node) -> Any:
        """从AST节点获取值"""
        if isinstance(node, ast.Constant):
            return node.value
        elif isinstance(node, ast.Str):  # Python < 3.8
            return node.s
        elif isinstance(node, ast.Num):  # Python < 3.8
            return node.n
        return None
    
    def parse_dict_value(self, node) -> Optional[Dict[str, Any]]:
        """解析字典值"""
        if isinstance(node, ast.Dict):
            result = {}
            for key_node, value_node in zip(node.keys, node.values):
                key = self.get_ast_value(key_node)
                value = self.get_ast_value(value_node)
                if key and value:
                    result[key] = value
            return result
        return None
    
    def get_function_signature(self, func_node) -> str:
        """获取函数签名"""
        args = []
        
        # 处理普通参数
        for arg in func_node.args.args:
            args.append(arg.arg)
        
        # 处理默认参数（简化处理）
        defaults_count = len(func_node.args.defaults)
        if defaults_count > 0:
            for i in range(len(args) - defaults_count, len(args)):
                args[i] += "=..."
        
        # 处理 *args
        if func_node.args.vararg:
            args.append(f"*{func_node.args.vararg.arg}")
        
        # 处理 **kwargs
        if func_node.args.kwarg:
            args.append(f"**{func_node.args.kwarg.arg}")
        
        return f"({', '.join(args)})"
    
    def get_module_name(self, file_path: Path) -> str:
        """从文件路径获取模块名"""
        # 获取相对于base_path的路径
        try:
            relative_path = file_path.relative_to(self.base_path.parent)
            # 转换为模块名（移除.py，替换/为.）
            module_parts = list(relative_path.parts[:-1]) + [relative_path.stem]
            return '.'.join(module_parts)
        except ValueError:
            # 如果无法获得相对路径，使用文件名
            return file_path.stem
    
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

