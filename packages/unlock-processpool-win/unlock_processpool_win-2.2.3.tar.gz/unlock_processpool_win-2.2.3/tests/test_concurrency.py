"""
并发测试 - 验证多线程安全性和竞态条件修复
测试RLock是否完全消除了竞态条件风险

Author: Half open flowers
"""
import sys
import unittest
import threading
import concurrent.futures
import time

from test_helpers import simple_task, cpu_bound_task


@unittest.skipIf(sys.platform != "win32", "仅Windows测试")
class TestConcurrency(unittest.TestCase):
    """测试并发安全性"""

    def test_please_multiple_threads_safe(self):
        """测试多线程同时调用please()是线程安全的"""
        from unlock_processpool import please

        errors = []

        def call_please():
            try:
                result = please()
                if not result:
                    errors.append("please() returned False on Windows")
            except Exception as e:
                errors.append(f"Exception in thread: {e}")

        # 创建20个线程同时调用please()
        threads = [threading.Thread(target=call_please) for _ in range(20)]

        for t in threads:
            t.start()

        for t in threads:
            t.join()

        # 不应该有任何错误
        self.assertEqual(len(errors), 0, f"Errors occurred: {errors}")

    def test_please_idempotent(self):
        """测试please()多次调用是幂等的"""
        from unlock_processpool import please
        import _winapi

        # 第一次调用
        result1 = please()
        func1 = _winapi.WaitForMultipleObjects

        # 第二次调用
        result2 = please()
        func2 = _winapi.WaitForMultipleObjects

        # 第三次调用
        result3 = please()
        func3 = _winapi.WaitForMultipleObjects

        # 所有调用应该返回True
        self.assertTrue(result1)
        self.assertTrue(result2)
        self.assertTrue(result3)

        # 函数应该保持不变（已经是_hacked_wait）
        self.assertIs(func1, func2)
        self.assertIs(func2, func3)

    def test_concurrent_executor_creation(self):
        """测试多线程同时创建进程池执行器"""
        from unlock_processpool import please
        please()

        results = []
        errors = []

        def create_and_use_executor():
            try:
                with concurrent.futures.ProcessPoolExecutor(max_workers=50) as executor:
                    result = list(executor.map(simple_task, range(20)))
                    results.append(result)
            except Exception as e:
                errors.append(f"Error in thread: {e}")

        # 创建5个线程同时创建和使用进程池
        threads = [threading.Thread(target=create_and_use_executor) for _ in range(5)]

        for t in threads:
            t.start()

        for t in threads:
            t.join()

        # 不应该有错误
        self.assertEqual(len(errors), 0, f"Errors: {errors}")

        # 所有线程都应该成功
        self.assertEqual(len(results), 5)

        # 验证结果正确性
        expected = [x * 2 for x in range(20)]
        for result in results:
            self.assertEqual(result, expected)

    def test_concurrent_task_submission(self):
        """测试多线程向同一个进程池提交任务"""
        from unlock_processpool import please
        please()

        with concurrent.futures.ProcessPoolExecutor(max_workers=100) as executor:
            all_futures = []
            errors = []

            def submit_tasks(start, count):
                try:
                    futures = [executor.submit(cpu_bound_task, i) for i in range(start, start + count)]
                    all_futures.extend(futures)
                except Exception as e:
                    errors.append(f"Error submitting tasks: {e}")

            # 创建10个线程，每个提交20个任务
            threads = [
                threading.Thread(target=submit_tasks, args=(i * 20, 20))
                for i in range(10)
            ]

            for t in threads:
                t.start()

            for t in threads:
                t.join()

            # 不应该有提交错误
            self.assertEqual(len(errors), 0, f"Errors: {errors}")

            # 应该有200个futures
            self.assertEqual(len(all_futures), 200)

            # 所有任务都应该成功完成
            results = [f.result(timeout=30) for f in all_futures]
            self.assertEqual(len(results), 200)

    def test_stress_many_workers_concurrent(self):
        """压力测试：多线程同时使用大量worker"""
        from unlock_processpool import please
        please()

        results = []
        errors = []

        def run_with_many_workers():
            try:
                # 降低worker数量和任务数量，使测试更快完成
                with concurrent.futures.ProcessPoolExecutor(max_workers=80) as executor:
                    result = list(executor.map(simple_task, range(50)))
                    results.append(len(result))
            except Exception as e:
                errors.append(f"Error: {e}")

        # 创建3个线程同时使用大量worker
        threads = [threading.Thread(target=run_with_many_workers) for _ in range(3)]

        for t in threads:
            t.start()

        for t in threads:
            t.join(timeout=120)  # 增加超时时间

        # 检查所有线程都完成了
        for t in threads:
            self.assertFalse(t.is_alive(), "Thread timed out")

        # 不应该有错误
        self.assertEqual(len(errors), 0, f"Errors: {errors}")

        # 所有线程都应该处理50个任务
        self.assertEqual(results, [50, 50, 50])

    def test_no_race_condition_in_wait_api(self):
        """测试_SAVED_WAIT_API不会被错误覆盖（竞态条件检测）"""
        import unlock_processpool.core as core
        from unlock_processpool import please

        # 先调用一次please()确保已初始化
        please()

        # 记录初始状态
        initial_saved_api = core._SAVED_WAIT_API
        saved_apis = []

        def capture_saved_api():
            please()  # 重复调用应该是幂等的
            saved_apis.append(core._SAVED_WAIT_API)

        # 创建50个线程同时调用
        threads = [threading.Thread(target=capture_saved_api) for _ in range(50)]

        for t in threads:
            t.start()

        for t in threads:
            t.join()

        # 所有线程看到的_SAVED_WAIT_API应该是同一个对象
        self.assertEqual(len(set(id(api) for api in saved_apis)), 1,
                        "竞态条件：_SAVED_WAIT_API被多次设置为不同的值")

        # 并且应该与初始值相同（幂等性）
        self.assertIs(saved_apis[0], initial_saved_api,
                     "please()不是幂等的，_SAVED_WAIT_API被修改了")

        # 验证不是_hacked_wait自己
        self.assertNotEqual(saved_apis[0].__name__, '_hacked_wait',
                          "严重BUG：_SAVED_WAIT_API被设置为_hacked_wait自己！")


if __name__ == '__main__':
    unittest.main()
