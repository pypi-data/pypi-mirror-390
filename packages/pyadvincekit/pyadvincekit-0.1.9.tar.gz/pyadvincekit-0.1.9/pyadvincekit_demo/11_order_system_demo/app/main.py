"""
PyAdvanceKit Admin Backend 主应用

基于PyAdvanceKit框架构建的管理系统后端API服务 - 使用FastAPI工厂和自动API生成。
"""


import sys
from pathlib import Path
from fastapi import APIRouter

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from pyadvincekit import (
    # FastAPI应用创建
    create_app,
    # 数据库
    init_database, get_database,
    # 日志
    get_logger,
    # 响应
    success_response, error_response
)
# 配置 - 从具体模块导入
from pyadvincekit.core.config import get_settings
from app.models.user import User
from app.models.order import Order
from app.services.user_service import user_service
from app.api.auth import router as auth_router
from app.api.users import router as users_router
from app.api.orders import router as orders_router
# from app.api.orders import router as orders_router  # 改用自动生成API
from dotenv import load_dotenv
from pyadvincekit.core.middleware import setup_all_middleware

load_dotenv("../.env")

# PyAdvanceKit会自动从.env文件加载配置，无需手动设置
logger = get_logger(__name__)


async def create_default_admin():
    """创建默认管理员账号"""
    try:
        from app.schemas.user import UserCreate
        
        # 检查是否已存在管理员 - 使用PyAdvanceKit服务层管理数据库会话
        admin = await user_service.get_user_by_email(
            "admin@example.com"
        )
        
        if not admin:
            # 创建默认管理员
            admin_data = UserCreate(
                name="系统管理员",
                email="admin@example.com",
                password="password123",
                is_active=True,
                is_superuser=True
            )
            
            admin = await user_service.create_user(admin_data)
            logger.info(f"Default admin created: {admin.email}")
            print(f"✅ 默认管理员创建成功: {admin.email} (密码: password123)")
        else:
            logger.info(f"Admin already exists: {admin.email}")
            print(f"ℹ️ 管理员已存在: {admin.email}")
            
    except Exception as e:
        logger.error(f"Failed to create default admin: {e}")
        print(f"❌ 创建默认管理员失败: {e}")


def create_application():
    """创建FastAPI应用 - get_settings()自动从.env加载配置"""
    
    # get_settings()会自动从.env文件加载配置
    settings = get_settings()
    
    # 使用标准的create_app方法
    app = create_app(
        title=settings.app_name,
        description="基于PyAdvanceKit框架构建的管理系统后端API - 使用.env配置和自动API生成",
        version=settings.app_version,
        routers=[auth_router, orders_router, users_router]  # 包含认证、订单管理、用户管理路由
    )
    
    # 使用PyAdvanceKit自动生成用户管理API（除了create，使用手动的create_manual）
    app.add_auto_api(
        model_class=User,
        router_prefix="/users",
        tags=["用户管理自动生成"],
        include_endpoints=["query", "get", "update", "delete", "count"]  # 不包含create，使用手动的create_manual
    )

    app.add_auto_api(
        model_class=Order,
        router_prefix="/orders",
        tags=["订单自动生成"],
        include_endpoints=["query", "get", "update", "delete", "count"]  # 不包含create，使用手动的create_manual
    )

    # 订单API使用手动定义的路由（包含认证），不使用自动生成
    # 手动定义的订单API在 orders_manual_router 中，已经包含了JWT认证
    

    print(f"应用名称: {settings.app_name}")
    print(f"服务器端口: {settings.port}")
    print(f"数据库URL: {settings.database_url}")
    print(f"连接池大小: {settings.database_pool_size}")
    print(f"SQL日志: {settings.database_echo_sql}")
    print(f"日志级别: {settings.log_level}")
    print(f"日志文件: {settings.log_file_path}")
    
    # 添加启动事件
    @app.on_event("startup")
    async def startup_event():
        """启动事件"""
        logger.info("Initializing database...")
        await init_database()
        logger.info("Database initialized successfully")
        
        logger.info("Creating default admin...")
        await create_default_admin()
        
        logger.info("Application startup completed")
    
    # 添加关闭事件
    @app.on_event("shutdown")
    async def shutdown_event():
        """关闭事件"""
        logger.info("Application shutdown completed")
    
    # 添加根路径路由
    @app.get("/", include_in_schema=False)
    async def root():
        """API根路径"""
        settings = get_settings()  # 从.env配置获取设置
        return success_response(
            data={
                "name": settings.app_name,
                "version": settings.app_version,
                "description": "PyAdvanceKit Admin Backend with .env config and Auto-Generated APIs",
                "features": [
                    ".env配置加载",
                    "自动API生成",
                    "统一响应格式", 
                    "全局异常处理",
                    "JWT认证",
                    "数据库会话管理"
                ],
                "docs": "/docs",
                "health": "/health"
            },
            message="PyAdvanceKit Admin Backend API - Powered by .env config"
        )
    
    logger.info("FastAPI application created using PyAdvanceKit create_app() with .env config")
    logger.info("API endpoints:")
    logger.info("- User API: /users (GET, POST, PUT, DELETE)")
    logger.info("- Order API: /orders (GET, POST, PUT, DELETE)")
    logger.info("- Order Stats API: /orders/stats/overview (GET)")
    
    return app


# 创建应用实例
app = create_application()
setup_all_middleware(
        app,
        enable_auth=True,
        exclude_paths={"/auth/login", "/auth", "/public", "/health", "/docs", "/redoc", "/openapi.json", "/","/auth/me"},
        require_auth_by_default=True
    )

if __name__ == "__main__":
    import uvicorn
    
    # 从.env配置获取服务器设置
    settings = get_settings()
    
    logger.info(f"Starting PyAdvanceKit Admin Backend on {settings.host}:{settings.port}")
    logger.info("Features:")
    logger.info("- .env配置自动加载")
    logger.info("- 自动生成用户管理CRUD接口")
    logger.info("- PyAdvanceKit统一响应格式") 
    logger.info("- PyAdvanceKit数据库会话管理")
    logger.info("- PyAdvanceKit异常处理")
    
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info"
    )