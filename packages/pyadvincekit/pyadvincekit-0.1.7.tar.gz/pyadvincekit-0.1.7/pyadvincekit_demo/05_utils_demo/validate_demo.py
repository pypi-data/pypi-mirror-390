from pyadvincekit import validate_email, validate_phone, create_validator

# 邮箱验证
email = "1153@qq.com"
# check_deliverability 检查是否有可投递性
if validate_email(email,True):
    print(f"✅ 有效邮箱: {email}")
else:
    print(f"❌ 无效邮箱: {email}")

# 手机号验证
phone = "13812345678"
if validate_phone(phone):
    print(f"✅ 有效手机号: {phone}")
else:
    print(f"❌ 无效手机号: {phone}")

# 创建验证器链
validator = create_validator()
result = validator \
    .validate_required("张三", "姓名") \
    .validate_email("user@example.com", "邮箱") \
    .validate_phone("13812345678", "手机号") \
    .validate_password_strength("StrongPass123", "密码")

if validator.is_valid():
    print("✅ 所有验证通过")
else:
    print("❌ 验证失败:")
    for error in validator.get_errors():
        print(f"   - {error}")