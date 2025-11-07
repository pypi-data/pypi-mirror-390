from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import time
from pyadvincekit import  get_logger,create_app,setup_all_middleware
from user import User

logger = get_logger(__name__)

class CustomTimingMiddleware(BaseHTTPMiddleware):
    """自定义计时中间件"""

    async def dispatch(self, request: Request, call_next):
        logger.info("自定义请求开始处理")
        start_time = time.time()

        # 处理请求
        response = await call_next(request)

        # 计算处理时间
        process_time = time.time() - start_time
        logger.info(f"请求处理完成，耗时：{process_time:.2f}秒")
        # 添加响应头
        response.headers["X-Process-Time"] = str(process_time)

        # 记录慢请求
        if process_time > 1.0:  # 超过1秒
            logger.warning("慢请求", extra={
                "path": request.url.path,
                "method": request.method,
                "process_time": process_time
            })

        return response


app = create_app(
    title="自动 API 示例",
    description="使用 pyadvancekit自动生成的 CRUD API"
)

# 自动生成用户 CRUD API
app.add_auto_api(
    model_class=User,
    router_prefix="/api/users",
    include_endpoints=["query", "get", "create", "update", "delete", "count"],
    tags=["用户管理"]
    # 可选：排除某些操作
    # exclude_operations=["delete"]
)

# 方式1：添加所有推荐中间件
setup_all_middleware(app)
# 添加自定义中间件
app.add_middleware(CustomTimingMiddleware)

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8008)