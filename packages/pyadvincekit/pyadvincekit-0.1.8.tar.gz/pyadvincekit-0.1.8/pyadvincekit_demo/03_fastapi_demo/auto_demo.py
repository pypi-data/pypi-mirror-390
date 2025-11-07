from pyadvincekit import create_app, FastAPIWithAutoAPI
from models import User, Product

# 创建应用
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

# 自动生成产品 CRUD API（支持软删除）
app.add_auto_api(
    model_class=Product,# 软删除模型会自动包含["soft_delete", "restore"] 接口
    router_prefix="/api/products",
    tags=["产品管理"],
)

# 启动应用
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)