from pyadvincekit import setup_logging, get_logger,Settings

# 自定义设置日志 ，或在.env 中配置
settings = Settings(
    logging={
        "log_level": "INFO",
        "structured_logging": True,
        "log_file_enabled": False  # 演示时不写文件
    }
)
setup_logging(settings)

# 获取日志器
logger = get_logger(__name__)

# 基础日志
logger.info("应用启动")
logger.warning("这是一个警告")
logger.error("发生错误", extra={"error_code": "E001"})

# 结构化日志
logger.info("用户登录", extra={
    "user_id": "12345",
    "username": "alice",
    "ip_address": "192.168.1.100",
    "user_agent": "Mozilla/5.0..."
})

# 业务日志
logger.info("订单创建", extra={
    "order_id": "ORDER-001",
    "user_id": "12345",
    "amount": 99.99,
    "currency": "CNY",
    "payment_method": "alipay"
})