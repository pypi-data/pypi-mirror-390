import sys
from datetime import datetime
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from pyadvincekit import (
    start_scheduler, list_tasks, get_scheduler,
    cron_task, interval_task, scheduled_task, TaskType
)
from pyadvincekit.logging import get_logger

logger = get_logger(__name__)

def demo_decorator_usage():
    """演示装饰器用法"""
    print("\n🎨 装饰器用法演示")
    print("=" * 60)

    # 定义装饰器任务
    @cron_task("*/1 * * * *", name="装饰器每分钟任务")
    def minute_decorator_task():
        """使用 @cron_task 装饰器的任务"""
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"🎯 [{current_time}] 装饰器任务: 每分钟执行")
        logger.info(f"Decorator cron task executed at {current_time}")

    @cron_task("*/3 * * * *", name="装饰器每3分钟任务")
    def three_minute_decorator_task():
        """每3分钟执行的装饰器任务"""
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"🔥 [{current_time}] 装饰器任务: 每3分钟执行")
        logger.info(f"Decorator 3-minute task executed at {current_time}")

    @cron_task("@hourly", name="装饰器小时任务")
    def hourly_decorator_task():
        """使用特殊表达式的装饰器任务"""
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"⏰ [{current_time}] 装饰器任务: 每小时执行")
        logger.info(f"Decorator hourly task executed at {current_time}")

    @interval_task(seconds=120, name="装饰器间隔任务")
    def interval_decorator_task():
        """使用 @interval_task 装饰器的任务"""
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"🔄 [{current_time}] 装饰器任务: 每2分钟间隔执行")
        logger.info(f"Decorator interval task executed at {current_time}")

    @scheduled_task(
        name="装饰器复杂任务",
        task_type=TaskType.CRON,
        cron_expression="0,30 * * * *",  # 每小时的0分和30分
        max_retries=5
    )
    def complex_decorator_task():
        """使用 @scheduled_task 装饰器的复杂任务"""
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"⚙️ [{current_time}] 装饰器任务: 复杂定时规则")
        logger.info(f"Decorator complex task executed at {current_time}")

    @cron_task("*/2 * * * * *", name="装饰器每2秒任务")  # 6字段格式：每2秒
    def two_second_decorator_task():
        """使用 @cron_task 装饰器的每2秒任务"""
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]  # 包含毫秒
        print(f"⚡ [{current_time}] 装饰器任务: 每2秒执行")
        logger.info(f"Decorator 2-second task executed at {current_time}")

    @interval_task(seconds=2, name="装饰器间隔2秒任务")
    def two_second_interval_task():
        """使用 @interval_task 装饰器的每2秒间隔任务"""
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]  # 包含毫秒
        print(f"🔥 [{current_time}] 装饰器任务: 间隔2秒执行")
        logger.info(f"Decorator 2-second interval task executed at {current_time}")

    print("装饰器任务已定义和注册")
    print("定义的装饰器任务:")
    print("   - @cron_task('*/1 * * * *'): 每分钟任务")
    print("   - @cron_task('*/3 * * * *'): 每3分钟任务")
    print("   - @cron_task('@hourly'): 每小时任务")
    print("   - @interval_task(seconds=120): 每2分钟间隔任务")
    print("   - @scheduled_task(...): 复杂定时任务")
    print("   - @cron_task('*/2 * * * * *'): 每2秒任务 (6字段格式)")
    print("   - @interval_task(seconds=2): 每2秒间隔任务")

    # 启动调度器以便装饰器任务能够执行
    scheduler = get_scheduler()
    if not scheduler.running:
        start_scheduler()
        print("✅ 调度器已启动，装饰器任务开始生效")

    # 显示所有任务
    print("\n📋 当前所有任务:")
    all_tasks = list_tasks()
    decorator_tasks = [task for task in all_tasks if "装饰器" in task.name]

    for task in decorator_tasks:
        next_run_str = task.next_run.strftime('%Y-%m-%d %H:%M:%S') if task.next_run else 'N/A'
        print(f"   - {task.name}: {task.status.value} (下次: {next_run_str})")

    return decorator_tasks

if __name__ == '__main__':
    # 装饰器用法演示
    decorator_tasks = demo_decorator_usage()