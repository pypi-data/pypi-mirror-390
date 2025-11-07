from pyadvincekit import HTTPUtils, create_http_client, create_api_client
import asyncio

# 测试URL解析
url = "https://api.example.com:8080/v1/users?page=1&size=10#section"
parsed = HTTPUtils.parse_url(url)
print(f"✅ URL解析: {url}")
print(f"   - 域名: {parsed['hostname']}")
print(f"   - 端口: {parsed['port']}")
print(f"   - 路径: {parsed['path']}")
print(f"   - 查询参数: {parsed['query_dict']}")

# 测试URL验证
valid_urls = [
    "https://www.example.com",
    "http://localhost:8080",
    "ftp://files.example.com"
]
invalid_urls = [
    "not-a-url",
    "http://",
    "just-text"
]

print("✅ URL验证:")
for url in valid_urls:
    is_valid = HTTPUtils.is_valid_url(url)
    print(f"   - {url}: {'有效' if is_valid else '无效'}")

for url in invalid_urls:
    is_valid = HTTPUtils.is_valid_url(url)
    print(f"   - {url}: {'有效' if is_valid else '无效'}")

# HTTP客户端创建
http_client = create_http_client(timeout=30, verify_ssl=True)
print(f"✅ HTTP客户端创建: {type(http_client).__name__}")


# GET 请求
async def fetch_data():
    response = await http_client.async_get("http://localhost:8000/users")
    status_code = response.get("status_code")
    if status_code == 200:
        print(f"请求成功: {response.get('data')}")
        return response.get("data")
    else:
        print(f"请求失败: {status_code}")



# POST 请求
def create_user():
    user_data = {
        "username": "xiaoming",
        "email": "11@qq.com",
        "full_name": "string",
        "age": 0,
        "is_active": True,
        "hashed_password": "string"
    }
    response = http_client.post("http://localhost:8000/users", json_data=user_data)
    if response.status_code == 200:
        print(f"请求成功: {response.json()}")
    else:
        print(f"请求失败: {response.status_code}")

    return response.json()


# 创建 API 客户端（带认证）
api_client = create_api_client("http://localhost:8000", api_key="test-key")
print(f"✅ API客户端创建: {type(api_client).__name__}")


# 批量请求
async def get_data():
    path = "/users"
    response = await api_client.async_get(path)

    status_code = response.get("status_code")
    if status_code == 200:
        print(f"请求成功: {response.get('data')}")
        return response.get("data")
    else:
        print(f"请求失败: {status_code}")

if __name__ == '__main__':
    asyncio.run(fetch_data())
    # create_user()
    # asyncio.run(get_data())