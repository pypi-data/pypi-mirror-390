"""
中间件模块

提供常用的中间件功能。
"""

import logging
import time
import uuid
from typing import Callable, Dict, Any, Optional
from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from pyadvincekit.core.config import get_settings
from pyadvincekit.logging import get_logger
from pyadvincekit.docs.decorators import api_category, api_doc, api_example

logger = get_logger(__name__)


class RequestIDMiddleware(BaseHTTPMiddleware):
    """请求ID中间件"""
    
    def __init__(self, app: FastAPI, header_name: str = "X-Request-ID"):
        super().__init__(app)
        self.header_name = header_name
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # 生成或获取请求ID
        request_id = request.headers.get(self.header_name) or str(uuid.uuid4())
        
        # 设置请求状态
        request.state.request_id = request_id
        
        # 处理请求
        response = await call_next(request)
        
        # 添加响应头
        response.headers[self.header_name] = request_id
        
        return response


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """请求日志中间件"""
    
    def __init__(
        self, 
        app: FastAPI, 
        log_request_body: bool = False,
        log_response_body: bool = False,
        exclude_paths: Optional[list] = None
    ):
        super().__init__(app)
        self.log_request_body = log_request_body
        self.log_response_body = log_response_body
        self.exclude_paths = exclude_paths or ["/health", "/docs", "/redoc", "/openapi.json"]
        self.settings = get_settings()
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # 检查是否需要排除
        if request.url.path in self.exclude_paths:
            return await call_next(request)
        
        start_time = time.time()
        
        # 获取请求ID
        request_id = getattr(request.state, "request_id", "unknown")
        
        # 记录请求开始
        request_data = {
            "request_id": request_id,
            "method": request.method,
            "url": str(request.url),
            "path": request.url.path,
            "query_params": dict(request.query_params),
            "headers": dict(request.headers),
            "client_ip": self._get_client_ip(request),
        }
        
        # 记录请求体（如果启用）
        if self.log_request_body and self.settings.log_request_body:
            try:
                body = await request.body()
                if body:
                    request_data["body"] = body.decode("utf-8")
            except Exception as e:
                request_data["body_error"] = str(e)
        
        logger.info(f"请求开始: {request.method} {request.url.path}", extra=request_data)
        
        # 处理请求
        try:
            response = await call_next(request)
        except Exception as e:
            # 记录异常
            duration = time.time() - start_time
            logger.error(
                f"请求异常: {request.method} {request.url.path}",
                extra={
                    "request_id": request_id,
                    "duration": duration,
                    "exception": str(e)
                },
                exc_info=True
            )
            raise
        
        # 计算处理时间
        duration = time.time() - start_time
        
        # 记录响应
        response_data = {
            "request_id": request_id,
            "status_code": response.status_code,
            "duration": duration,
            "response_headers": dict(response.headers),
        }
        
        # 记录响应体（如果启用且不是大文件）
        if (self.log_response_body and 
            response.headers.get("content-length", "0") != "0" and
            int(response.headers.get("content-length", "0")) < 10000):  # 小于10KB
            # 注意：这里不能直接读取响应体，因为会影响流式响应
            pass
        
        # 根据状态码选择日志级别
        if response.status_code >= 500:
            log_level = logging.ERROR
        elif response.status_code >= 400:
            log_level = logging.WARNING
        else:
            log_level = logging.INFO
        
        logger.log(
            log_level,
            f"请求完成: {request.method} {request.url.path} - {response.status_code} ({duration:.3f}s)",
            extra=response_data
        )
        
        return response
    
    def _get_client_ip(self, request: Request) -> str:
        """获取客户端IP地址"""
        # 检查常见的代理头
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        return request.client.host if request.client else "unknown"


class PerformanceMiddleware(BaseHTTPMiddleware):
    """性能监控中间件"""
    
    def __init__(
        self, 
        app: FastAPI,
        slow_request_threshold: float = 1.0,
        enable_metrics: bool = True
    ):
        super().__init__(app)
        self.slow_request_threshold = slow_request_threshold
        self.enable_metrics = enable_metrics
        self.request_metrics: Dict[str, Any] = {}
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        start_time = time.time()
        
        # 处理请求
        response = await call_next(request)
        
        # 计算处理时间
        duration = time.time() - start_time
        
        # 获取请求ID
        request_id = getattr(request.state, "request_id", "unknown")
        
        # 添加性能头
        response.headers["X-Process-Time"] = str(duration)
        
        # 记录慢请求
        if duration > self.slow_request_threshold:
            logger.warning(
                f"慢请求检测: {request.method} {request.url.path}",
                extra={
                    "request_id": request_id,
                    "duration": duration,
                    "threshold": self.slow_request_threshold
                }
            )
        
        # 收集性能指标
        if self.enable_metrics:
            self._collect_metrics(request, response, duration)
        
        return response
    
    def _collect_metrics(self, request: Request, response: Response, duration: float):
        """收集性能指标"""
        endpoint = f"{request.method} {request.url.path}"
        
        if endpoint not in self.request_metrics:
            self.request_metrics[endpoint] = {
                "count": 0,
                "total_duration": 0,
                "min_duration": float("inf"),
                "max_duration": 0,
                "status_codes": {}
            }
        
        metrics = self.request_metrics[endpoint]
        metrics["count"] += 1
        metrics["total_duration"] += duration
        metrics["min_duration"] = min(metrics["min_duration"], duration)
        metrics["max_duration"] = max(metrics["max_duration"], duration)
        
        status_code = response.status_code
        metrics["status_codes"][status_code] = metrics["status_codes"].get(status_code, 0) + 1
    
    def get_metrics(self) -> Dict[str, Any]:
        """获取性能指标"""
        result = {}
        for endpoint, metrics in self.request_metrics.items():
            if metrics["count"] > 0:
                result[endpoint] = {
                    "count": metrics["count"],
                    "avg_duration": metrics["total_duration"] / metrics["count"],
                    "min_duration": metrics["min_duration"],
                    "max_duration": metrics["max_duration"],
                    "status_codes": metrics["status_codes"]
                }
        return result


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    安全头中间件
    继承BaseHTTPMiddleware基类实现中间件
    在初始化时设置默认的安全头部字段
    支持通过custom_headers参数自定义额外头部
    使用字典解包语法合并默认头和自定义头
    """
    
    def __init__(self, app: FastAPI, custom_headers: Optional[Dict[str, str]] = None):
        super().__init__(app)
        self.security_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            **(custom_headers or {})
        }
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        response = await call_next(request)
        
        # 添加安全头
        for header, value in self.security_headers.items():
            response.headers[header] = value
        
        return response


# 中间件设置函数
# @api_category("高级功能", "中间件配置")
# @api_doc(
#     title="设置请求日志中间件",
#     description="为FastAPI应用添加请求日志中间件，自动记录请求和响应信息",
#     params={
#         "app": "FastAPI应用实例",
#         "log_request_body": "是否记录请求体，默认False",
#         "log_response_body": "是否记录响应体，默认False",
#         "max_body_size": "记录的最大请求体大小，超过则截断"
#     },
#     returns="None: 无返回值，直接修改应用配置",
#     version="2.0.0"
# )
# @api_example('''
# from fastapi import FastAPI
# from pyadvincekit.core.middleware import setup_request_logging_middleware
#
# app = FastAPI()
#
# # 基础请求日志中间件
# setup_request_logging_middleware(app)
#
# # 包含请求体的日志中间件
# setup_request_logging_middleware(
#     app,
#     log_request_body=True,
#     max_body_size=1024  # 只记录前1024字节
# )
#
# # 完整日志中间件（开发环境）
# setup_request_logging_middleware(
#     app,
#     log_request_body=True,
#     log_response_body=True,
#     max_body_size=2048
# )
#
# # 运行后会自动记录如下信息：
# # [INFO] 请求开始: POST /api/users/ - request_id=abc123
# # [INFO] 请求完成: POST /api/users/ - 200 - 45.2ms - request_id=abc123
#     ''', description="请求日志中间件配置示例", title="setup_request_logging_middleware 使用示例")
def setup_request_logging_middleware(app: FastAPI, **kwargs) -> None:
    """设置请求日志中间件"""
    app.add_middleware(RequestLoggingMiddleware, **kwargs)
    logger.info("请求日志中间件已配置")


def setup_performance_middleware(app: FastAPI, **kwargs) -> None:
    """设置性能监控中间件"""
    app.add_middleware(PerformanceMiddleware, **kwargs)
    logger.info("性能监控中间件已配置")


def setup_request_id_middleware(app: FastAPI, **kwargs) -> None:
    """设置请求ID中间件"""
    app.add_middleware(RequestIDMiddleware, **kwargs)
    logger.info("请求ID中间件已配置")


def setup_security_headers_middleware(app: FastAPI, **kwargs) -> None:
    """设置安全头中间件"""
    app.add_middleware(SecurityHeadersMiddleware, **kwargs)
    logger.info("安全头中间件已配置")


# @api_category("高级功能", "中间件配置")
# @api_doc(
#     title="设置所有推荐的中间件",
#     description="一键配置PyAdvanceKit推荐的所有中间件，包括安全头、性能监控、请求日志、请求ID等",
#     params={
#         "app": "FastAPI应用实例",
#         "enable_auth": "是否启用认证中间件，默认False",
#         "auth_kwargs": "认证中间件的额外参数"
#     },
#     returns="None: 无返回值，直接修改应用配置",
#     version="2.0.0"
# )
# @api_example('''
# from fastapi import FastAPI
# from pyadvincekit.core.middleware import setup_all_middleware
#
# app = FastAPI()
#
# # 基础中间件配置（推荐生产环境使用）
# setup_all_middleware(app)
#
# # 包含认证的完整中间件配置
# setup_all_middleware(
#     app,
#     enable_auth=True,
#     secret_key="your-secret-key",
#     token_expire_minutes=30
# )
#
# # 配置后应用将自动包含：
# # ✅ 安全头中间件 - 添加X-Frame-Options等安全头
# # ✅ 性能监控中间件 - 监控请求耗时和性能指标
# # ✅ 请求日志中间件 - 记录请求和响应信息
# # ✅ 请求ID中间件 - 为每个请求生成唯一ID
# # ✅ 认证中间件 - JWT认证和权限控制（可选）
#
# # 启动应用
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)
#     ''', description="一键配置所有推荐中间件", title="setup_all_middleware 使用示例")
def setup_all_middleware(app: FastAPI, enable_auth: bool = False, **auth_kwargs) -> None:
    """设置所有推荐的中间件"""
    setup_security_headers_middleware(app)
    setup_performance_middleware(app)
    setup_request_logging_middleware(app)
    setup_request_id_middleware(app)
    
    # 🔥 可选启用身份校验中间件（占位功能）
    if enable_auth:
        from pyadvincekit.auth.middleware import setup_auth_middleware
        setup_auth_middleware(app,require_auth_by_default=enable_auth, **auth_kwargs)
        logger.info("身份校验中间件已启用")
    else:
        logger.info("身份校验中间件未启用（占位状态）")
    
    logger.info("所有中间件已配置")
