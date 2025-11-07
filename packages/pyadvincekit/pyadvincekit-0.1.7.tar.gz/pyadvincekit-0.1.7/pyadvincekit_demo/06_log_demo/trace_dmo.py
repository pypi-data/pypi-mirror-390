import asyncio

from pyadvincekit import create_app, TraceMiddleware,get_logger,setup_all_middleware
from pyadvincekit.core.middleware import setup_request_id_middleware,setup_request_logging_middleware
from user import User
import uvicorn

# 获取日志器
logger = get_logger(__name__)

# 创建 FastAPI 应用
app = create_app(
    title="追踪示例",
    description="基于 PyAdvanceKit 示例 演示",
    enable_tracing=True,
    version="1.0.0"
)

# 自动生成用户管理 API
app.add_auto_api(
    model_class=User,
    router_prefix="/api/users",
    tags=["用户管理"]
)


# 方式一： 请求通过 request_id 进行追踪
setup_request_logging_middleware(app)
setup_request_id_middleware(app)

# 请求过程自动打印 request_id
# 请求开始: POST /api/users/query extra={'request_id': '78a2ef5d-eef4-4526-9efc-5117b455bc5f' ...
# 请求完成: POST /api/users/query extra={'request_id': '78a2ef5d-eef4-4526-9efc-5117b455bc5f' ...



# 方式二：添加追踪中间件
app.add_middleware(TraceMiddleware)
# 请求过程自动打印 打印traceId
# Trace context started            ... trace_id=e772cc30-f9fe-4e00-b92c-de33e002a527 ...
# Trace context ended successfully ... trace_id=e772cc30-f9fe-4e00-b92c-de33e002a527 ...

def basic_trace():
    """测试基本跟踪功能"""
    print("🔍 测试基本跟踪功能")
    print("-" * 40)

    try:
        from pyadvincekit import (
            TraceContext, TraceManager, trace_function, trace_method,
            get_current_trace_id, get_current_span_id, get_current_context
        )

        # 测试基本跟踪上下文
        with TraceContext(user_id="user123", request_id="req456") as trace:
            print(f"✅ TraceId: {trace.trace_id}")
            print(f"✅ SpanId: {trace.span_id}")
            print(f"✅ UserId: {trace.user_id}")
            print(f"✅ RequestId: {trace.request_id}")

            # 测试获取当前上下文
            current_trace_id = get_current_trace_id()
            current_span_id = get_current_span_id()
            context = get_current_context()

            print(f"✅ 当前TraceId: {current_trace_id}")
            print(f"✅ 当前SpanId: {current_span_id}")
            print(f"✅ 当前上下文: {context}")

        print("✅ 基本跟踪功能测试通过")
        return True

    except Exception as e:
        print(f"❌ 基本跟踪功能测试失败: {e}")
        return False


async def process_trace():
    """测试嵌套跟踪"""
    try:
        from pyadvincekit import TraceManager, get_current_trace_id, get_current_span_id

        # 创建父跟踪
        with TraceManager.start_trace("parent_operation", user_id="user123") as parent:
            print(f"✅ 父跟踪 - TraceId: {parent.trace_id}, SpanId: {parent.span_id}")

            # 创建子跟踪
            with TraceManager.create_child_span("child_operation") as child:
                print(f"✅ 子跟踪 - TraceId: {child.trace_id}, SpanId: {child.span_id}")
                print(f"✅ 子跟踪 - 父SpanId: {child.parent_span_id}")

                # 创建孙跟踪
                with TraceManager.create_child_span("grandchild_operation") as grandchild:
                    print(f"✅ 孙跟踪 - TraceId: {grandchild.trace_id}, SpanId: {grandchild.span_id}")
                    print(f"✅ 孙跟踪 - 父SpanId: {grandchild.parent_span_id}")

                    # 验证跟踪链
                    current_trace = get_current_trace_id()
                    current_span = get_current_span_id()
                    print(f"✅ 当前跟踪链 - TraceId: {current_trace}, SpanId: {current_span}")

        print("✅ 嵌套跟踪测试通过")
        return True

    except Exception as e:
        print(f"❌ 嵌套跟踪测试失败: {e}")
        return False

if __name__ == '__main__':
    basic_trace()
    asyncio.run(process_trace())
    # 启动服务器
    uvicorn.run(app, host="0.0.0.0", port=8004)

    # asyncio.run(process_order({"order_id": "ORDER-001"}))

