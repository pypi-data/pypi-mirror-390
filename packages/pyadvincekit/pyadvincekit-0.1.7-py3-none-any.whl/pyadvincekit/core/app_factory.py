"""
应用工厂（框架内置）

create_app_with_auto_discovery:
- 创建 FastAPI 应用（基于框架 create_app）
- 自动发现并注册外部工程的路由（api 目录）
- 自动发现模型并按外部配置生成 CRUD API
"""

from typing import List, Optional

from fastapi import FastAPI

from pyadvincekit.core.router_discovery import auto_discover_and_register_routers
from pyadvincekit.core.auto_api_manager import auto_discover_and_generate_apis
from pyadvincekit.logging import  TraceMiddleware
from pyadvincekit.core.config import get_settings
from pyadvincekit.core.database import init_database
from pyadvincekit.docs.decorators import api_category, api_doc, api_example


def create_app_with_auto_discovery(
    title: Optional[str] = None,
    description: Optional[str] = None,
    version: Optional[str] = None,
    api_directory: str = "api",
    models_directory: str = "models",
    exclude_router_files: Optional[List[str]] = None,
    config_module: str = "config.auto_api_config",
) -> FastAPI:
    # 1) 自动发现外部路由
    routers = auto_discover_and_register_routers(api_directory, exclude_router_files)

    # 2) 获取设置并使用默认值
    settings = get_settings()
    
    # 如果没有传入参数，则使用 settings 中的默认值
    app_title = title or settings.app_name
    app_description = description or settings.app_description
    app_version = version or settings.app_version
    
    # 使用框架内部的 create_app 函数（在同一文件中定义）
    app = create_app(
        settings=settings,
        title=app_title,
        description=app_description,
        version=app_version,
        routers=routers,
        include_health_check=True,
        include_database_init=True
    )

    # 3) 自动生成 CRUD API
    auto_discover_and_generate_apis(
        app,
        models_directory=models_directory,
        config_module=config_module,
    )

    return app


# def create_app_with_router_discovery_only(
@api_category("API开发", "路由创建")
@api_doc(
    title="自动路由注册应用创建",
    description="创建FastAPI应用并自动发现和注册指定目录下的路由文件",
    params={
        "title": "应用标题（可选）",
        "description": "应用描述（可选）",
        "version": "应用版本（可选）",
        "api_directory": "API路由文件目录（默认：api）",
        "exclude_router_files": "排除的路由文件列表（可选）",
        "auth_kwargs": "认证相关参数（可选）"
    },
    returns="FastAPI: 配置完成的FastAPI应用实例",
    version="2.0.0"
)
@api_example('''
# 基础用法：创建自动注册路由的应用
app = create_app_auto_register()

# 自定义配置：指定应用信息和API目录
app = create_app_auto_register(
    title="我的API服务",
    description="基于PyAdvanceKit的API服务",
    version="1.0.0",
    api_directory="src/api"
)

# 排除特定路由：不注册某些路由文件
app = create_app_auto_register(
    api_directory="api",
    exclude_router_files=["admin.py", "internal.py"]
)

# 启动应用
import uvicorn
uvicorn.run(app, host="0.0.0.0", port=8000)
''', description="自动路由注册应用的创建和配置")
def create_app_auto_register(
    title: Optional[str] = None,
    description: Optional[str] = None,
    version: Optional[str] = None,
    api_directory: str = "api",
    exclude_router_files: Optional[List[str]] = None,
    **auth_kwargs
) -> FastAPI:
    """
    创建路由自动发现注册功能
    
    这个函数只会自动发现和注册外部路由，不会生成自动 CRUD API。
    适用于已经生成了 API 和 Service 文件的项目。
    自动调用 setup_all_middleware() 来启动所有中间件。
    
    Args:
        title: 应用标题
        description: 应用描述  
        version: 应用版本
        api_directory: API 文件目录
        exclude_router_files: 排除的路由文件列表
        enable_auth: 是否启用身份校验中间件
        **auth_kwargs: 身份校验中间件的额外参数
        
    Returns:
        配置好的 FastAPI 应用实例
    """
    from pyadvincekit.logging import get_logger
    from pyadvincekit.core.middleware import setup_all_middleware
    logger = get_logger(__name__)
    
    # 1) 获取设置
    settings = get_settings()
    
    # 如果没有传入参数，则使用 settings 中的默认值
    app_title = title or settings.app_name
    app_description = description or settings.app_description
    app_version = version or settings.app_version
    
    # 2) 创建基础应用（不包含路由）
    app = create_app(
        settings=settings,
        title=app_title,
        description=app_description,
        version=app_version,
        routers=[],  # 先创建空的路由列表
        include_health_check=True,
        include_database_init=True
    )
    
    # 3) 自动发现并注册外部路由
    logger.info(f"开始发现路由，目录: {api_directory}")
    routers = auto_discover_and_register_routers(api_directory, exclude_router_files)
    logger.info(f"发现 {len(routers)} 个路由")
    
    # 4) 将发现的路由添加到应用中
    for router in routers:
        logger.info(f"注册路由: {router.prefix}, 标签: {router.tags}")
        app.include_router(router)
    
    # 5) 自动设置所有中间件
    logger.info("开始设置所有中间件...")
    enable_auth = settings.jwt_enable
    setup_all_middleware(app, enable_auth=enable_auth, **auth_kwargs)
    logger.info("所有中间件设置完成")

    can_trace = settings.request_trace
    if can_trace:
        app.add_middleware(TraceMiddleware)



    return app


"""
FastAPI应用工厂

提供可配置的FastAPI应用创建功能。
"""

from typing import List, Optional, Dict, Any, Callable
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from pyadvincekit.core.config import Settings, get_settings
from pyadvincekit.core.database import (
    get_database_manager, 
    init_database, 
    close_database,
    check_database_health
)
from pyadvincekit.core.exception_handler import setup_exception_handlers
from pyadvincekit.core.response import success_response,error_response
from pyadvincekit.core.auto_api import AutoAPIGenerator

from pyadvincekit.logging import get_logger

logger = get_logger(__name__)


class FastAPIAppFactory:
    """FastAPI应用工厂类"""
    
    def __init__(self, settings: Optional[Settings] = None):
        self.settings = settings or get_settings()
        self.routers: List[APIRouter] = []
        self.middleware_callbacks: List[Callable[[FastAPI], None]] = []
        self.startup_callbacks: List[Callable[[], None]] = []
        self.shutdown_callbacks: List[Callable[[], None]] = []
        self.auto_api_generator = AutoAPIGenerator()
    
    def create_app(
        self,
        title: Optional[str] = None,
        description: Optional[str] = None,
        version: Optional[str] = None,
        include_health_check: bool = True,
        include_database_init: bool = True,
        **kwargs
    ) -> FastAPI:
        """
        创建FastAPI应用实例
        
        Args:
            title: 应用标题
            description: 应用描述
            version: 应用版本
            include_health_check: 是否包含健康检查端点
            include_database_init: 是否在启动时初始化数据库
            **kwargs: 其他FastAPI参数
            
        Returns:
            配置好的FastAPI应用实例
        """
        
        # 应用基础配置
        app_config = {
            "title": title or self.settings.app_name,
            "description": description or f"{self.settings.app_name} API",
            "version": version or self.settings.app_version,
            "docs_url": self.settings.docs_url,
            "redoc_url": self.settings.redoc_url,
            "openapi_url": self.settings.openapi_url,
            **kwargs
        }
        
        # 创建FastAPI应用
        app = FastAPI(**app_config)
        
        # 设置应用状态
        app.state.settings = self.settings
        
        # 注册中间件
        self._setup_middleware(app)
        
        # 注册路由
        self._setup_routes(app, include_health_check)
        
        # 设置异常处理器
        setup_exception_handlers(app)
        
        # 注册生命周期事件
        self._setup_lifespan_events(app, include_database_init)
        
        logger.info(f"FastAPI应用创建成功: {app_config['title']} v{app_config['version']}")
        
        return app
    
    def _setup_middleware(self, app: FastAPI) -> None:
        """设置中间件"""
        
        # CORS中间件
        if self.settings.jwt_allow_origins:
            app.add_middleware(
                CORSMiddleware,
                allow_origins=self.settings.jwt_allow_origins,
                allow_credentials=self.settings.jwt_allow_credentials,
                allow_methods=self.settings.jwt_allow_methods,
                allow_headers=self.settings.jwt_allow_headers,
            )
            logger.info("CORS中间件已配置")
        
        # 可信主机中间件（生产环境）
        if self.settings.is_production():
            app.add_middleware(
                TrustedHostMiddleware,
                allowed_hosts=["*"]  # 生产环境应该设置具体的主机名
            )
            logger.info("可信主机中间件已配置")
        
        # 执行自定义中间件回调
        for callback in self.middleware_callbacks:
            callback(app)
    
    def _setup_routes(self, app: FastAPI, include_health_check: bool) -> None:
        """设置路由"""
        
        # 注册自定义路由
        for router in self.routers:
            app.include_router(router)
            logger.info(f"路由已注册: {router.prefix or '/'}")
        
        # 健康检查端点
        if include_health_check:
            self._add_health_check_routes(app)
    
    def _add_health_check_routes(self, app: FastAPI) -> None:
        """添加健康检查路由"""
        
        @app.get("/health", tags=["健康检查"])
        async def health_check():
            """健康检查端点"""
            return success_response({
                "status": "healthy",
                "app_name": self.settings.app_name,
                "version": self.settings.app_version,
                "environment": self.settings.environment
            }, message="系统健康检查成功")
        
        @app.get("/health/database", tags=["健康检查"])
        async def database_health_check():
            """数据库健康检查端点"""
            is_healthy = await check_database_health()
            
            if is_healthy:
                return success_response({
                    "status": "healthy",
                    "database": "connected"
                }, message="数据库连接正常")
            else:
                return error_response(
                    message="数据库连接异常", 
                    ret_code="500002",
                    details={"database": "disconnected"},
                    http_status=503
                )
        
        logger.info("健康检查端点已注册")
    
    def _setup_lifespan_events(self, app: FastAPI, include_database_init: bool) -> None:
        """设置生命周期事件"""
        
        @app.on_event("startup")
        async def startup_event():
            """应用启动事件"""
            logger.info(f"正在启动 {self.settings.app_name}...")
            
            # 数据库初始化
            if include_database_init:
                try:
                    await init_database()
                    logger.info("数据库初始化完成")
                except Exception as e:
                    logger.error(f"数据库初始化失败: {e}")
                    raise
            
            # 执行自定义启动回调
            for callback in self.startup_callbacks:
                try:
                    if hasattr(callback, '__await__'):
                        await callback()
                    else:
                        callback()
                except Exception as e:
                    logger.error(f"启动回调执行失败: {e}")
                    raise
            
            logger.info(f"{self.settings.app_name} 启动完成")
        
        @app.on_event("shutdown")
        async def shutdown_event():
            """应用关闭事件"""
            logger.info(f"正在关闭 {self.settings.app_name}...")
            
            # 执行自定义关闭回调
            for callback in self.shutdown_callbacks:
                try:
                    if hasattr(callback, '__await__'):
                        await callback()
                    else:
                        callback()
                except Exception as e:
                    logger.error(f"关闭回调执行失败: {e}")
            
            # 关闭数据库连接
            try:
                await close_database()
                logger.info("数据库连接已关闭")
            except Exception as e:
                logger.error(f"数据库连接关闭失败: {e}")
            
            logger.info(f"{self.settings.app_name} 关闭完成")
    
    def add_router(self, router: APIRouter) -> "FastAPIAppFactory":
        """添加路由器"""
        self.routers.append(router)
        return self
    
    def add_middleware(self, callback: Callable[[FastAPI], None]) -> "FastAPIAppFactory":
        """添加中间件配置回调"""
        self.middleware_callbacks.append(callback)
        return self
    
    def add_startup_callback(self, callback: Callable[[], None]) -> "FastAPIAppFactory":
        """添加启动回调"""
        self.startup_callbacks.append(callback)
        return self
    
    def add_shutdown_callback(self, callback: Callable[[], None]) -> "FastAPIAppFactory":
        """添加关闭回调"""
        self.shutdown_callbacks.append(callback)
        return self
    
    def add_auto_api(
        self,
        model_class,
        crud_class=None,
        router_prefix=None,
        tags=None,
        include_endpoints=None
    ) -> "FastAPIAppFactory":
        """
        为模型自动生成 REST API 接口
        
        Args:
            model_class: 模型类
            crud_class: CRUD 类，如果为 None 则自动创建
            router_prefix: 路由前缀，默认为模型名称的小写复数形式
            tags: API 标签
            include_endpoints: 包含的端点列表，默认为所有端点
            
        Returns:
            FastAPIAppFactory: 返回自身以支持链式调用
        """
        router = self.auto_api_generator.generate_api(
            model_class=model_class,
            crud_class=crud_class,
            router_prefix=router_prefix,
            tags=tags,
            include_endpoints=include_endpoints
        )
        self.add_router(router)
        return self


class FastAPIWithAutoAPI(FastAPI):
    """支持自动 API 生成的 FastAPI 应用"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.auto_api_generator = AutoAPIGenerator()
    
    def add_auto_api(
        self,
        model_class,
        crud_class=None,
        router_prefix=None,
        tags=None,
        include_endpoints=None
    ) -> "FastAPIWithAutoAPI":
        """
        为模型自动生成 REST API 接口
        
        Args:
            model_class: 模型类
            crud_class: CRUD 类，如果为 None 则自动创建
            router_prefix: 路由前缀，默认为模型名称的小写复数形式
            tags: API 标签
            include_endpoints: 包含的端点列表，默认为所有端点
            
        Returns:
            FastAPIWithAutoAPI: 返回自身以支持链式调用
        """
        router = self.auto_api_generator.generate_api(
            model_class=model_class,
            crud_class=crud_class,
            router_prefix=router_prefix,
            tags=tags,
            include_endpoints=include_endpoints
        )
        self.include_router(router)
        return self


# 便捷函数
def create_app(
    settings: Optional[Settings] = None,
    title: Optional[str] = None,
    description: Optional[str] = None,
    version: Optional[str] = None,
    routers: Optional[List[APIRouter]] = None,
    include_health_check: bool = True,
    include_database_init: bool = True,
    **kwargs
) -> FastAPIWithAutoAPI:
    """
    便捷的应用创建函数
    
    Args:
        settings: 配置对象
        title: 应用标题
        description: 应用描述
        version: 应用版本
        routers: 路由器列表
        include_health_check: 是否包含健康检查端点
        include_database_init: 是否在启动时初始化数据库
        **kwargs: 其他FastAPI参数
        
    Returns:
        配置好的FastAPI应用实例（支持自动API生成）
    """
    
    factory = FastAPIAppFactory(settings)
    
    # 添加路由器
    if routers:
        for router in routers:
            factory.add_router(router)
    
    # 创建应用
    app = factory.create_app(
        title=title,
        description=description,
        version=version,
        include_health_check=include_health_check,
        include_database_init=include_database_init,
        **kwargs
    )
    
    # 转换为支持自动API生成的类型
    auto_api_app = FastAPIWithAutoAPI(
        title=app.title,
        description=app.description,
        version=app.version,
        openapi_url=app.openapi_url,
        docs_url=app.docs_url,
        redoc_url=app.redoc_url,
        **kwargs
    )
    
    # 复制中间件
    for middleware in app.user_middleware:
        auto_api_app.user_middleware.append(middleware)
    
    # 复制路由
    for route in app.routes:
        auto_api_app.routes.append(route)
    
    # 复制异常处理器
    for exc_handler in app.exception_handlers:
        auto_api_app.exception_handlers[exc_handler] = app.exception_handlers[exc_handler]
    
    # 复制事件处理器
    for handler in app.router.on_startup:
        auto_api_app.router.on_startup.append(handler)
    for handler in app.router.on_shutdown:
        auto_api_app.router.on_shutdown.append(handler)
    
    return auto_api_app


# 应用工厂实例
app_factory = FastAPIAppFactory()
