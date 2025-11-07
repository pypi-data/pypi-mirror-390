from pyadvincekit.utils.datetime_utils import (
    DateTimeUtils, now, utc_now, format_duration,
    humanize_datetime, timestamp_to_datetime, datetime_to_timestamp
)
from datetime import datetime, timedelta, timezone

# 获取当前时间
current_time = now()  # 本地时间
utc_time = utc_now()  # UTC 时间

print(f"本地时间: {current_time}")
print(f"UTC 时间: {utc_time}")

# 测试获取今天日期
today = DateTimeUtils.today()

print(f"今天的 时间: {today}")

#时间戳转换
"""测试字符串转换"""
dt = datetime(2025, 10, 13, 12, 30, 45)
date_string = DateTimeUtils.datetime_to_str(dt)
print(f"时间字符串: {date_string}")
converted_dt = DateTimeUtils.str_to_datetime(date_string)

# 格式化持续时间
duration1 = timedelta(seconds=3661)  # 1小时1分1秒
duration2 = timedelta(days=2, hours=3, minutes=30)

print(f"持续时间1: {format_duration(3661)}")  # "1小时1分钟"

# 测试周末/工作日
saturday = datetime(2025, 10, 18)
monday = datetime(2025, 10, 13)
print(f"18号是周末吗? {DateTimeUtils.is_weekend(saturday)}")
print(f"13号是周末吗? {DateTimeUtils.is_weekend(monday)}")

