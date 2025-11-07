import asyncio

from pyadvincekit import (
    register_service, call_service, batch_call_services
)


def service_registration():
    """测试服务注册"""
    print("🎯 测试服务注册")
    print("=" * 50)

    # 注册服务A
    service_a = register_service(
        service_name="service-a",
        base_url="http://localhost:8001",
        timeout=30,
        retry_count=3
    )
    print(f"✅ 注册服务A: {service_a.service_name} at {service_a.base_url}")

    # 注册服务B
    service_b = register_service(
        service_name="service-b",
        base_url="http://localhost:8002",
        timeout=30,
        retry_count=3
    )
    print(f"✅ 注册服务B: {service_b.service_name} at {service_b.base_url}")

    # 注册服务C
    service_c = register_service(
        service_name="service-c",
        base_url="http://localhost:8003",
        timeout=30,
        retry_count=3
    )
    print(f"✅ 注册服务C: {service_c.service_name} at {service_c.base_url}")

    return ["service-a", "service-b", "service-c"]


async def service_calls():
    """测试服务调用"""
    print("\n🎯 测试服务调用")
    print("=" * 50)

    try:
        # 调用服务A
        print("📞 调用服务A...")
        result_a = await call_service(
            service_name="service-a",
            endpoint="/process",
            data={"message": "Hello from A", "type": "greeting"}
        )
        print(f"✅ 服务A响应: {result_a}")

        # 调用服务B
        print("📞 调用服务B...")
        result_b = await call_service(
            service_name="service-b",
            endpoint="/calculate",
            data={"value": 42, "operation": "multiply"}
        )
        print(f"✅ 服务B响应: {result_b}")

        # 调用服务C
        print("📞 调用服务C...")
        result_c = await call_service(
            service_name="service-c",
            endpoint="/validate",
            data={"input": "test@example.com", "type": "email"}
        )
        print(f"✅ 服务C响应: {result_c}")

    except Exception as e:
        print(f"⚠️ 服务调用失败（预期行为，因为服务未实际运行）: {e}")


async def batch_calls():
    """测试批量调用"""
    print("\n🎯 测试批量调用")
    print("=" * 50)

    # 准备批量调用
    batch_calls = [
        {
            "service_name": "service-a",
            "endpoint": "/process",
            "data": {"message": "Batch call 1", "type": "batch"}
        },
        {
            "service_name": "service-b",
            "endpoint": "/calculate",
            "data": {"value": 10, "operation": "add"}
        },
        {
            "service_name": "service-c",
            "endpoint": "/validate",
            "data": {"input": "batch@test.com", "type": "email"}
        }
    ]

    try:
        print("📞 执行批量调用...")
        results = await batch_call_services(batch_calls)

        print("📊 批量调用结果:")
        for i, result in enumerate(results):
            if result["success"]:
                print(f"  ✅ 调用{i + 1}: {result['result']}")
            else:
                print(f"  ❌ 调用{i + 1}: {result['error']}")

    except Exception as e:
        print(f"⚠️ 批量调用失败（预期行为）: {e}")



async def main():
    # 测试服务注册
    service_names = service_registration()

    # 测试服务调用
    await service_calls()

    await batch_calls()


if __name__ == '__main__':
    asyncio.run(main())