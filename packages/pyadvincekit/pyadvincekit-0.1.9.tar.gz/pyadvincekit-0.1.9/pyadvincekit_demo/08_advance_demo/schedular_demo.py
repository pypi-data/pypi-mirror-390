import time

from pyadvincekit import (
    schedule_once, schedule_interval, start_scheduler, stop_scheduler, list_tasks
)
import asyncio
from datetime import datetime

def simple_task(name: str = "SimpleTask"):
    """简单任务"""
    print(f"🔄 执行任务: {name} - {datetime.now().strftime('%H:%M:%S')}")
    return f"Task {name} completed"


async def async_task(name: str = "AsyncTask"):
    """异步任务"""
    print(f"🔄 执行异步任务: {name} - {datetime.now().strftime('%H:%M:%S')}")
    await asyncio.sleep(0.1)  # 模拟异步操作
    return f"Async task {name} completed"


def failing_task(name: str = "FailingTask"):
    """会失败的任务"""
    print(f"🔄 执行会失败的任务: {name} - {datetime.now().strftime('%H:%M:%S')}")
    raise Exception(f"Task {name} intentionally failed")


def basic_scheduling():
    """测试基本调度功能"""
    print("🎯 测试基本调度功能")
    print("=" * 50)

    # 启动调度器
    start_scheduler()
    print("✅ 调度器已启动")

    # 添加一次性任务
    task_id1 = schedule_once(simple_task, name="一次性任务")

    # 添加间隔任务（每3秒执行一次）
    task_id2 = schedule_interval(
        simple_task,
        interval_seconds=3,
        name="间隔任务"
    )

    # 添加异步任务
    task_id3 = schedule_once(async_task, name="异步任务")

    # 添加会失败的任务
    task_id4 = schedule_once(failing_task, name="失败任务", max_retries=2)

    # 等待任务执行
    print("\n⏳ 等待任务执行...")
    time.sleep(8)

    # 检查任务状态
    print("\n📊 任务状态:")
    tasks = list_tasks()
    for task in tasks:
        print(f"  - {task.name}: {task.status.value}")
        if task.error_message:
            print(f"    错误: {task.error_message}")

    # 停止调度器
    stop_scheduler()
    print("✅ 调度器已停止")

if __name__ == '__main__':
    # 基本调用
    basic_scheduling()