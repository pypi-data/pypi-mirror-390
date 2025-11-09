"""
测试辅助函数模块
所有函数必须在模块级别定义以支持pickle（Windows ProcessPoolExecutor要求）

Author: Half open flowers
"""
import time
import os


def simple_task(x):
    """简单的计算任务"""
    return x * 2


def cpu_bound_task(x):
    """CPU密集型任务"""
    result = 0
    for i in range(1000):
        result += i * x
    return result


def io_bound_task(x):
    """I/O密集型任务（模拟）"""
    time.sleep(0.01)
    return x * 2


def slow_task(x):
    """慢速任务（用于测试超时）"""
    time.sleep(0.5)
    return x


def very_slow_task(x):
    """非常慢的任务（用于测试超时）"""
    time.sleep(2.0)
    return x


def error_task(x):
    """会抛出异常的任务"""
    if x < 0:
        raise ValueError(f"Negative value not allowed: {x}")
    return x


def pid_task(x):
    """返回进程ID的任务"""
    return (x, os.getpid())


def identity(x):
    """恒等函数"""
    return x


def sum_range(n):
    """计算1到n的和"""
    return sum(range(n + 1))


def factorial(n):
    """计算阶乘"""
    if n <= 1:
        return 1
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result
