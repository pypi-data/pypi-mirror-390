import sys
import unittest
from unittest.mock import patch
import _winapi
import concurrent.futures
import concurrent.futures.process as process
from unlock_processpool import please


def _double(x):
    """可pickle的测试函数"""
    return x * 2


class TestUnlock(unittest.TestCase):

    def test_patch_application(self):
        # 应用补丁
        result = please()
        self.assertTrue(result)

        # 验证API已被Hook（函数名应该是_hacked_wait）
        self.assertEqual(_winapi.WaitForMultipleObjects.__name__, '_hacked_wait')

        # 验证进程数限制
        if sys.platform == "win32":
            self.assertEqual(process._MAX_WINDOWS_WORKERS, 508)  # 510 - 2

    @unittest.skipIf(sys.platform != "win32", "仅Windows测试")
    def test_worker_limit(self):
        # 测试是否能突破默认限制
        please()

        try:
            with concurrent.futures.ProcessPoolExecutor(max_workers=100) as executor:
                results = list(executor.map(_double, range(50)))
                self.assertEqual(len(results), 50)
        except Exception as e:
            self.fail(f"创建进程池失败: {str(e)}")

    def test_non_windows_behavior(self):
        # 模拟非Windows环境
        with patch('sys.platform', 'linux'):
            result = please()
            self.assertFalse(result)

if __name__ == '__main__':
    unittest.main()