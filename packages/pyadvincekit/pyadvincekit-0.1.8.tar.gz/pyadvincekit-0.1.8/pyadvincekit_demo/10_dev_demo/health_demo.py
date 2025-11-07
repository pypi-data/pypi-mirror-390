from pyadvincekit import get_database,create_app

app = create_app(
    title="健康检查 API 示例",
    description="使用 pyadvancekit自动生成的 健康检查 API"
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)

