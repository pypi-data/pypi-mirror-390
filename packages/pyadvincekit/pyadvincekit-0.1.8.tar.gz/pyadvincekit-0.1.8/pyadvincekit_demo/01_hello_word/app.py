from pyadvincekit import create_app, success_response
from fastapi import APIRouter

# 创建路由
router = APIRouter()

@router.get("/hello")
async def hello_world():
    """Hello World 接口"""
    return success_response(
        data={"message": "Hello, PyAdvanceKit!"},
        message="欢迎使用 PyAdvanceKit"
    )

@router.get("/info")
async def app_info():
    """应用信息接口"""
    return success_response(
        data={
            "app_name": "我的第一个 pyadvancekit应用",
            "version": "1.0.0",
            "framework": "PyAdvanceKit"
        },
        message="获取应用信息成功"
    )

# 创建应用（一行代码！）
app = create_app(
    title="我的第一个 pyadvancekit应用",
    description="使用 pyadvancekit构建的示例应用",
    version="1.0.0",
    routers=[router]
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)