# 添加性能监控中间件
from pyadvincekit.core.middleware import setup_performance_middleware,setup_request_logging_middleware
from pyadvincekit import create_app
from user import User

app = create_app(title="监控应用")
setup_request_logging_middleware(app)  # 请求日志
setup_performance_middleware(
    app,
    slow_request_threshold=1.0,  # 1秒
    enable_metrics=True
)

app.add_auto_api(
    model_class=User,
    router_prefix="/api/users",
    include_endpoints=["query", "get", "create", "update", "delete", "count"],
    tags=["用户管理"]
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8010)

    # 访问 http://localhost:8010/api/users/query
    # 日志会打印访问时间： 请求完成: POST /api/users/query - 200 (0.013s)

