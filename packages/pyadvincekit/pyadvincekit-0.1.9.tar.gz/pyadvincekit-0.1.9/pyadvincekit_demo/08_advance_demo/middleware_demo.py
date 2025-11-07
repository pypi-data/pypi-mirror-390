from pyadvincekit import create_app, setup_all_middleware
from pyadvincekit.core.middleware import (
    setup_request_logging_middleware,
    setup_performance_middleware,
    setup_security_headers_middleware,
    setup_request_id_middleware
)

app = create_app(title="中间件示例")

# 方式1：添加所有推荐中间件
setup_all_middleware(app)

# 方式2：选择性添加中间件
setup_request_logging_middleware(app)  # 请求日志
setup_performance_middleware(app)      # 性能监控
setup_security_headers_middleware(app)         # 安全头
setup_request_id_middleware(app)  # 自动添加request_id

