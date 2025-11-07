"""
API 和 Service 层代码生成器

为模型自动生成标准的 FastAPI 路由和业务服务层代码
"""

import os
import re
import importlib.util
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from pyadvincekit.logging import get_logger
from pyadvincekit.core.excel_generator import TableDefinition

logger = get_logger(__name__)


@dataclass
class EndpointConfig:
    """API 端点配置"""
    method: str  # GET, POST, PUT, DELETE
    path: str    # 路径
    function_name: str  # 函数名
    description: str    # 描述
    service_method: str # 对应的 Service 方法
    params: List[Dict[str, Any]]  # 参数列表
    return_type: str    # 返回类型


@dataclass
class ServiceMethodConfig:
    """Service 方法配置"""
    name: str           # 方法名
    description: str    # 描述
    params: str         # 参数字符串
    return_type: str    # 返回类型
    body: str          # 方法体


class APIServiceGenerator:
    """API 和 Service 层代码生成器"""
    
    def __init__(self):
        self.logger = logger
        self.auto_api_config = None
    
    def generate_for_model(self, table: TableDefinition, output_dir: str, force_generate: bool = False, overwrite_existing: bool = False) -> Dict[str, str]:
        """为指定模型生成 API 和 Service 代码"""
        model_name = self._to_pascal_case(table.name)
        snake_name = self._to_snake_case(table.name)
        
        # 检查是否需要生成（根据 auto_api_config.py 配置）
        if not force_generate and not self._should_generate_for_model(model_name):
            self.logger.info(f"Skipping API/Service generation for {model_name} (not in auto_api_config)")
            return {}
        
        generated_files = {}
        
        # 创建输出目录
        api_dir = Path(output_dir) / "api"
        service_dir = Path(output_dir) / "services"
        api_dir.mkdir(exist_ok=True)
        service_dir.mkdir(exist_ok=True)
        
        # 生成 API 文件
        api_file = api_dir / f"{snake_name}_api.py"
        if not overwrite_existing and api_file.exists():
            self.logger.info(f"API file {api_file} already exists, skipping generation")
        else:
            api_content = self._generate_api_content(table)
            self._write_file(api_file, api_content)
            generated_files['api'] = str(api_file)
        
        # 生成 Service 文件
        service_file = service_dir / f"{snake_name}_service.py"
        if not overwrite_existing and service_file.exists():
            self.logger.info(f"Service file {service_file} already exists, skipping generation")
        else:
            service_content = self._generate_service_content(table)
            self._write_file(service_file, service_content)
            generated_files['service'] = str(service_file)
        
        # 更新 __init__.py 文件
        self._update_init_files(output_dir, table)
        
        self.logger.info(f"Generated API and Service for {model_name}")
        return generated_files
    
    def _generate_api_content(self, table: TableDefinition) -> str:
        """生成 API 层代码"""
        model_name = self._to_pascal_case(table.name)
        snake_name = self._to_snake_case(table.name)
        service_class = f"{model_name}Service"
        
        # 生成端点配置
        endpoints = self._get_api_endpoints(table)
        
        # 构建导入部分
        imports = [
            "from fastapi import APIRouter, Depends, HTTPException",
            "from typing import List, Optional",
            "from sqlalchemy.ext.asyncio import AsyncSession",
            f"from services.{snake_name}_service import {service_class}",
            f"from schemas.{snake_name} import (",
            f"    {model_name}Create, {model_name}Update, {model_name}Response,",
            f"    {model_name}Query, {model_name}Filter",
            ")",
            "from pyadvincekit import (",
            "    StandardResponse, paginated_response, get_db, success_response, error_response,",
            "    GetByIdRequest, DeleteRequest, UpdateRequest",
            ")",
            ""
        ]
        
        # 构建路由定义
        route_prefix = f"/{snake_name}s"
        tags = [f"{table.comment or model_name}管理"]
        
        router_lines = [
            f'router = APIRouter(prefix="{route_prefix}", tags={tags})',
            ""
        ]
        
        # 生成端点函数
        endpoint_functions = []
        for endpoint in endpoints:
            func_code = self._generate_endpoint_function(endpoint, table)
            endpoint_functions.append(func_code)
        
        # 组合完整代码
        content = "\n".join([
            "#!/usr/bin/env python3",
            '"""',
            f"Generated API for {model_name}",
            f"Generated at: {datetime.now().isoformat()}",
            '"""',
            "",
            *imports,
            *router_lines,
            *endpoint_functions
        ])
        
        return content
    
    def _generate_service_content(self, table: TableDefinition) -> str:
        """生成 Service 层代码"""
        model_name = self._to_pascal_case(table.name)
        snake_name = self._to_snake_case(table.name)
        service_class = f"{model_name}Service"
        
        # 生成服务方法配置
        methods = self._get_service_methods(table)
        
        # 构建导入部分
        imports = [
            "from typing import Optional, List, Dict, Any",
            "from sqlalchemy.ext.asyncio import AsyncSession",
            "from sqlalchemy import select, func, and_, or_",
            "from fastapi import HTTPException",
            "from pyadvincekit import (",
            "    BaseCRUD,",
            "    GetByIdRequest, DeleteRequest, UpdateRequest",
            ")",
            f"from models.{snake_name} import {model_name}",
            f"from schemas.{snake_name} import (",
            f"    {model_name}Create, {model_name}Update, {model_name}Query, {model_name}Filter",
            ")",
            ""
        ]
        
        # 构建类定义
        class_lines = [
            f"class {service_class}:",
            f'    """{table.comment or model_name}服务"""',
            "",
            "    def __init__(self):",
            f"        self.crud = BaseCRUD({model_name})",
            ""
        ]
        
        # 生成服务方法
        method_functions = []
        for method in methods:
            func_code = self._generate_service_method(method)
            method_functions.append(func_code)
        
        # 组合完整代码
        content = "\n".join([
            "#!/usr/bin/env python3",
            '"""',
            f"Generated Service for {model_name}",
            f"Generated at: {datetime.now().isoformat()}",
            '"""',
            "",
            *imports,
            *class_lines,
            *method_functions
        ])
        
        return content
    
    def _get_api_endpoints(self, table: TableDefinition) -> List[EndpointConfig]:
        """获取 API 端点配置"""
        model_name = self._to_pascal_case(table.name)
        snake_name = self._to_snake_case(table.name)
        
        endpoints = [
            # 创建
            EndpointConfig(
                method="post",
                path="/create",
                function_name=f"create_{snake_name}",
                description=f"创建{table.comment or model_name}",
                service_method="create",
                params=[
                    {"name": "data", "type": f"{model_name}Create"},
                    {"name": "db", "type": "AsyncSession", "default": "Depends(get_db)"},
                    {"name": "service", "type": f"{model_name}Service", "default": "Depends()"}
                ],
                return_type="dict"
            ),
            
            # 查询列表
            EndpointConfig(
                method="post",
                path="/query",
                function_name=f"query_{snake_name}s",
                description=f"查询{table.comment or model_name}列表",
                service_method="get_list",
                params=[
                    {"name": "query", "type": f"{model_name}Query"},
                    {"name": "db", "type": "AsyncSession", "default": "Depends(get_db)"},
                    {"name": "service", "type": f"{model_name}Service", "default": "Depends()"}
                ],
                return_type="StandardResponse"
            ),
            
            # 获取详情
            EndpointConfig(
                method="post",
                path="/get",
                function_name=f"get_{snake_name}",
                description=f"获取{table.comment or model_name}详情",
                service_method="get_by_id",
                params=[
                    {"name": "request", "type": "GetByIdRequest"},
                    {"name": "db", "type": "AsyncSession", "default": "Depends(get_db)"},
                    {"name": "service", "type": f"{model_name}Service", "default": "Depends()"}
                ],
                return_type="dict"
            ),
            
            # 更新
            EndpointConfig(
                method="post",
                path="/update",
                function_name=f"update_{snake_name}",
                description=f"更新{table.comment or model_name}",
                service_method="update",
                params=[
                    {"name": "request", "type": f"UpdateRequest[{model_name}Update]"},
                    {"name": "db", "type": "AsyncSession", "default": "Depends(get_db)"},
                    {"name": "service", "type": f"{model_name}Service", "default": "Depends()"}
                ],
                return_type="dict"
            ),
            
            # 删除
            EndpointConfig(
                method="post",
                path="/delete",
                function_name=f"delete_{snake_name}",
                description=f"删除{table.comment or model_name}",
                service_method="delete",
                params=[
                    {"name": "request", "type": "DeleteRequest"},
                    {"name": "db", "type": "AsyncSession", "default": "Depends(get_db)"},
                    {"name": "service", "type": f"{model_name}Service", "default": "Depends()"}
                ],
                return_type="StandardResponse"
            ),
            
            # 统计数量
            EndpointConfig(
                method="post",
                path="/count",
                function_name=f"count_{snake_name}s",
                description=f"统计{table.comment or model_name}数量",
                service_method="count",
                params=[
                    {"name": "filter_params", "type": f"{model_name}Filter"},
                    {"name": "db", "type": "AsyncSession", "default": "Depends(get_db)"},
                    {"name": "service", "type": f"{model_name}Service", "default": "Depends()"}
                ],
                return_type="StandardResponse"
            )
        ]
        
        return endpoints
    
    def _get_service_methods(self, table: TableDefinition) -> List[ServiceMethodConfig]:
        """获取 Service 方法配置"""
        model_name = self._to_pascal_case(table.name)
        
        methods = [
            # 创建方法
            ServiceMethodConfig(
                name="create",
                description=f"创建{table.comment or model_name}",
                params=f", data: {model_name}Create, db: AsyncSession",
                return_type=f"{model_name}",
                body=f"""        # 数据验证
        await self._validate_create_data(data)
        
        # 转换驼峰命名为数据库字段名
        db_data = data.model_dump(by_alias=True)
        
        # 创建记录
        db_obj = await self.crud.create(db, db_data)
        return db_obj"""
            ),
            
            # 获取列表方法
            ServiceMethodConfig(
                name="get_list",
                description=f"获取{table.comment or model_name}列表",
                params=f", query: {model_name}Query, filter_params: {model_name}Filter, db: AsyncSession",
                return_type="Dict[str, Any]",
                body="""        # 构建查询条件
        conditions = await self._build_filter_conditions(filter_params)
        
        # 分别执行查询和计数
        items = await self.crud.get_multi(
            db,
            skip=(query.page - 1) * query.size,
            limit=query.size,
            filters=conditions,
            order_by=query.order_by,
            order_desc=query.order_desc
        )
        
        total = await self.crud.count(
            db,
            filters=conditions
        )
        
        return {
            "items": items,
            "total": total,
            "page": query.page,
            "size": query.size,
            "pages": (total + query.size - 1) // query.size
        }"""
            ),
            
            # 获取详情方法
            ServiceMethodConfig(
                name="get_by_id",
                description=f"根据ID获取{table.comment or model_name}",
                params=", request: GetByIdRequest, db: AsyncSession",
                return_type=f"{model_name}",
                body="""        db_obj = await self.crud.get(db, request.id)
        if not db_obj:
            raise HTTPException(status_code=404, detail="记录不存在")
        return db_obj"""
            ),
            
            # 更新方法
            ServiceMethodConfig(
                name="update",
                description=f"更新{table.comment or model_name}",
                params=f", request: UpdateRequest[{model_name}Update], db: AsyncSession",
                return_type=f"{model_name}",
                body="""        # 检查记录是否存在
        db_obj = await self.crud.get(db, request.id)
        if not db_obj:
            raise HTTPException(status_code=404, detail="记录不存在")
        
        # 数据验证
        await self._validate_update_data(request.id, request.data)
        
        # 转换驼峰命名为数据库字段名
        update_data = request.data.model_dump(exclude_unset=True, by_alias=True)
        updated_obj = await self.crud.update(db, db_obj, update_data)
        return updated_obj"""
            ),
            
            # 删除方法
            ServiceMethodConfig(
                name="delete",
                description=f"删除{table.comment or model_name}",
                params=", request: DeleteRequest, db: AsyncSession",
                return_type="Dict[str, Any]",
                body="""        # 检查记录是否存在
        db_obj = await self.crud.get(db, request.id)
        if not db_obj:
            raise HTTPException(status_code=404, detail="记录不存在")
        
        # 删除前验证
        await self._validate_delete(request.id, db_obj)
        
        # 执行删除
        await self.crud.delete(db, request.id)
        return {"message": "删除成功", "id": request.id}"""
            ),
            
            # 统计方法
            ServiceMethodConfig(
                name="count",
                description=f"统计{table.comment or model_name}数量",
                params=f", filter_params: {model_name}Filter, db: AsyncSession",
                return_type="Dict[str, Any]",
                body="""        # 构建查询条件
        conditions = await self._build_filter_conditions(filter_params)
        
        # 统计数量
        total = await self.crud.count(db, filters=conditions)
        return {"total": total}"""
            ),
            
            # 辅助方法
            ServiceMethodConfig(
                name="_validate_create_data",
                description="验证创建数据",
                params=f", data: {model_name}Create",
                return_type="None",
                body="""        # TODO: 添加业务验证逻辑
        # 例如：检查唯一性约束、业务规则等
        pass"""
            ),
            
            ServiceMethodConfig(
                name="_validate_update_data",
                description="验证更新数据",
                params=f", item_id: str, data: {model_name}Update",
                return_type="None",
                body="""        # TODO: 添加业务验证逻辑
        # 例如：检查唯一性约束、业务规则等
        pass"""
            ),
            
            ServiceMethodConfig(
                name="_validate_delete",
                description="验证删除操作",
                params=f", item_id: str, db_obj: {model_name}",
                return_type="None",
                body="""        # TODO: 添加删除前验证逻辑
        # 例如：检查关联数据、业务规则等
        pass"""
            ),
            
            ServiceMethodConfig(
                name="_build_filter_conditions",
                description="构建过滤条件",
                params=f", filter_params: {model_name}Filter",
                return_type="List[Any]",
                body="""        conditions = []
        
        # TODO: 根据 filter_params 构建具体的查询条件
        # 例如：
        # if filter_params.name:
        #     conditions.append(Model.name.like(f"%{filter_params.name}%"))
        
        return conditions"""
            )
        ]
        
        return methods
    
    def _generate_endpoint_function(self, endpoint: EndpointConfig, table: TableDefinition) -> str:
        """生成端点函数代码"""
        # 获取模型名称和蛇形命名（与 _generate_api_content 保持一致）
        model_name = self._to_pascal_case(table.name)
        snake_name = self._to_snake_case(table.name)
        service_class = f"{model_name}Service"
        
        # 构建参数列表
        params = []
        service_args = []
        
        for param in endpoint.params:
            if param["name"] == "service":
                params.append(f'    {param["name"]}: {param["type"]} = {param["default"]}')
            elif "default" in param:
                params.append(f'    {param["name"]}: {param["type"]} = {param["default"]}')
            else:
                params.append(f'    {param["name"]}: {param["type"]}')
                if param["name"] != "service":
                    service_args.append(param["name"])
        
        params_str = ",\n".join(params)
        service_args_str = ", ".join(service_args)
        
        # 构建返回类型
        if endpoint.return_type == "StandardResponse":
            response_model = ""
        else:
            response_model = f", response_model={endpoint.return_type}"
        
        # 构建函数体
        if endpoint.service_method == "get_list":
            function_body = f"""    # 创建过滤器参数，使用 query 中的搜索条件
    from schemas.{snake_name} import {model_name}Filter
    filter_params = {model_name}Filter()
    # 将 query 中的搜索条件传递给 filter_params
    if hasattr(query, 'search') and query.search:
        filter_params.search = query.search
    result = await service.{endpoint.service_method}({service_args_str}, filter_params, db)
    # 转换列表中的每个项目为字典
    from pyadvincekit.utils.serializers import sqlalchemy_to_dict
    camel_items = [sqlalchemy_to_dict(item) for item in result["items"]]
    return paginated_response(
        items=camel_items,
        total=result["total"],
        page=result["page"],
        page_size=result["size"]
    )"""
        elif endpoint.service_method == "create":
            function_body = f"""    await service.{endpoint.service_method}({service_args_str}, db)
    return success_response(
        message="新增成功",
        ret_code='000000'
    )"""
        elif endpoint.service_method == "get_by_id":
            function_body = f"""    result = await service.{endpoint.service_method}({service_args_str}, db)
    # 将 SQLAlchemy 对象转换为字典
    from pyadvincekit.utils.serializers import sqlalchemy_to_dict
    result_dict = sqlalchemy_to_dict(result) if result else {{}}
    return success_response(
        data=result_dict,
        message="查询成功",
        ret_code='000000'
    )"""
        elif endpoint.service_method == "update":
            function_body = f"""    result = await service.{endpoint.service_method}({service_args_str}, db)
    # 将 SQLAlchemy 对象转换为字典
    from pyadvincekit.utils.serializers import sqlalchemy_to_dict
    result_dict = sqlalchemy_to_dict(result) if result else {{}}
    return success_response(
        data=result_dict,
        message="更新成功",
        ret_code='000000'
    )"""
        elif endpoint.service_method == "delete":
            function_body = f"""    result = await service.{endpoint.service_method}({service_args_str}, db)
    return success_response(
        message="删除成功",
        ret_code='000000'
    )"""
        elif endpoint.service_method == "count":
            function_body = f"""    result = await service.{endpoint.service_method}({service_args_str}, db)
    return success_response(
        data=result,
        message="统计成功",
        ret_code='000000'
    )"""
        else:
            function_body = f"""    result = await service.{endpoint.service_method}({service_args_str}, db)
    return success_response(
        data=result,
        message="操作成功",
        ret_code='000000'
    )"""
        
        return f"""
@router.{endpoint.method}("{endpoint.path}"{response_model})
async def {endpoint.function_name}(
{params_str}
):
    \"\"\"{endpoint.description}\"\"\"
{function_body}
"""
    
    def _generate_service_method(self, method: ServiceMethodConfig) -> str:
        """生成服务方法代码"""
        return f"""    async def {method.name}(self{method.params}) -> {method.return_type}:
        \"\"\"{method.description}\"\"\"
{method.body}

"""
    
    def _update_init_files(self, output_dir: str, table: TableDefinition):
        """更新 __init__.py 文件"""
        model_name = self._to_pascal_case(table.name)
        snake_name = self._to_snake_case(table.name)
        
        # 更新 api/__init__.py
        api_init_file = Path(output_dir) / "api" / "__init__.py"
        self._update_init_file(api_init_file, f"from .{snake_name}_api import router as {snake_name}_router")
        
        # 更新 services/__init__.py
        service_init_file = Path(output_dir) / "services" / "__init__.py"
        self._update_init_file(service_init_file, f"from .{snake_name}_service import {model_name}Service")
    
    def _update_init_file(self, file_path: Path, import_line: str):
        """更新单个 __init__.py 文件"""
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if import_line not in content:
                content += f"\n{import_line}\n"
        else:
            content = f'"""\n{file_path.parent.name} module\n"""\n\n{import_line}\n'
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def _write_file(self, file_path: Path, content: str):
        """写入文件"""
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def _to_pascal_case(self, name: str) -> str:
        """转换为PascalCase"""
        return ''.join(word.capitalize() for word in name.split('_'))
    
    def _should_generate_for_model(self, model_name: str) -> bool:
        """检查是否应该为指定模型生成 API 和 Service"""
        if self.auto_api_config is None:
            self._load_auto_api_config()
        
        return model_name in self.auto_api_config if self.auto_api_config else False
    
    def _load_auto_api_config(self):
        """加载 auto_api_config.py 配置"""
        try:
            # 尝试导入外部项目的 auto_api_config
            import sys
            import importlib.util
            
            # 查找 config/auto_api_config.py 文件
            config_paths = [
                "config/auto_api_config.py",
                "./config/auto_api_config.py",
                "../config/auto_api_config.py"
            ]
            
            for config_path in config_paths:
                if os.path.exists(config_path):
                    spec = importlib.util.spec_from_file_location("auto_api_config", config_path)
                    if spec and spec.loader:
                        auto_api_config_module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(auto_api_config_module)
                        
                        if hasattr(auto_api_config_module, 'AUTO_API_CONFIG'):
                            self.auto_api_config = auto_api_config_module.AUTO_API_CONFIG
                            self.logger.info(f"Loaded auto_api_config from {config_path}")
                            return
            
            # 如果找不到配置文件，尝试直接导入
            try:
                from config.auto_api_config import AUTO_API_CONFIG
                self.auto_api_config = AUTO_API_CONFIG
                self.logger.info("Loaded auto_api_config from config module")
            except ImportError:
                self.logger.warning("No auto_api_config found, will generate for all models")
                self.auto_api_config = {}
                
        except Exception as e:
            self.logger.error(f"Failed to load auto_api_config: {e}")
            self.auto_api_config = {}
    
    def _to_pascal_case(self, name: str) -> str:
        """转换为PascalCase"""
        return ''.join(word.capitalize() for word in name.split('_'))
    
    def _to_snake_case(self, name: str) -> str:
        """转换为snake_case"""
        # 如果已经是snake_case，直接返回
        if '_' in name and name.islower():
            return name
        
        # 处理PascalCase到snake_case的转换
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
