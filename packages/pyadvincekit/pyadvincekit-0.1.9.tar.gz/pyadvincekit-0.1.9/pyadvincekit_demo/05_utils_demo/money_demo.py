from pyadvincekit import Money, MoneyUtils, Currency, RoundingMode, money, cny, usd
from decimal import Decimal

# 创建金额对象
price1 = Money(Decimal("99.99"), Currency.CNY)
price2 = cny(99.99)  # 便捷方法
price3 = usd(19.99)

print(f"价格1: {price1}")  # ¥99.99
print(f"价格2: {price2}")  # ¥99.99
print(f"价格3: {price3}")  # $19.99

# 金额运算
total = price1 + cny(10.01)
print(f"总价: {total}")  # ¥110.00

discount = price1 * Decimal("0.8")
print(f"折后价: {discount}")  # ¥79.99

# 金额比较
if price1 > cny(50):
    print("价格超过50元")


# 测试金额格式化
formatted = total.format(show_symbol=True, thousands_separator=",")
print(f"✅ 格式化显示: {formatted}")

# 测试税额计算
tax_amount, total_with_tax = MoneyUtils.calculate_tax(cny(100), 13)  # 13%增值税
print(f"✅ 税额计算: 不含税价100元, 税额{tax_amount}, 含税总价{total_with_tax}")

# 汇率转换（需要配置汇率）
usd_amount = usd(100)
cny_converted = MoneyUtils.convert_currency(usd_amount, Currency.CNY, 7.2)
print(f"✅ 货币转换: {usd_amount} × 7.2 = {cny_converted}")

