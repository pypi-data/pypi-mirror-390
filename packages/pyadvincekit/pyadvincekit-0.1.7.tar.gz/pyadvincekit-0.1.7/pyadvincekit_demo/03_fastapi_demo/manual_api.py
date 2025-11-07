from pyadvincekit import create_app, FastAPIWithAutoAPI
from api.users import router
import uvicorn

# 创建应用
app = create_app(
    title="自动 API 示例",
    description="使用 pyadvancekit自动生成的 CRUD API",
    routers=[router, ]

)

if __name__ == '__main__':
    uvicorn.run(
        "03_fastapi_demo.manual_api:app",
        host="0.0.0.0",
        port=8000
    )