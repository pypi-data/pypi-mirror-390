from pyadvincekit import hash_password, encrypt_data, generate_secret_key

# 密码哈希
password = "user_password"
# 返回哈希值和盐值
password_hash, salt = hash_password(password)
print(f"密码哈希: {password_hash}")

# 验证密码
from pyadvincekit.utils.security import verify_password
is_valid = verify_password(password, password_hash, salt)
print(f"密码验证: {is_valid}")

# 数据加密
sensitive_data = "敏感信息"
encrypted = encrypt_data(sensitive_data, "encryption_key")
print(f"加密数据: {encrypted}")

# 生成安全密钥
secret_key = generate_secret_key()
print(f"生成的密钥: {secret_key}")

# JWT 密钥生成
jwt_secret = generate_secret_key(length=64)
print(f"JWT 密钥: {jwt_secret}")