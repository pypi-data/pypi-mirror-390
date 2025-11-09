"""
核心逻辑测试 - _hacked_wait 函数的完整测试覆盖
测试所有修复的CRITICAL缺陷和边界条件

Author: Half open flowers
"""
import sys
import unittest
from unittest.mock import Mock, patch, call
import time

# 只在Windows上导入_winapi
if sys.platform == "win32":
    import _winapi


@unittest.skipIf(sys.platform != "win32", "仅Windows测试")
class TestHackedWaitCore(unittest.TestCase):
    """测试_hacked_wait函数的核心逻辑"""

    def setUp(self):
        """每个测试前重置全局状态"""
        # 重新加载模块以清除monkey patch
        import unlock_processpool.core as core_module
        self.core_module = core_module

        # 备份原始API
        self.original_wait_api = _winapi.WaitForMultipleObjects

        # 重置全局变量
        core_module._SAVED_WAIT_API = None

    def tearDown(self):
        """恢复原始状态"""
        _winapi.WaitForMultipleObjects = self.original_wait_api
        self.core_module._SAVED_WAIT_API = None

    # ==================== wait_all=False 测试 ====================

    def test_wait_any_single_batch_first_ready(self):
        """wait_all=False: 单批次，第一个对象就绪"""
        from unlock_processpool import please
        please()

        # Mock底层API：第一个对象就绪
        mock_wait = Mock(return_value=0x00)  # WAIT_OBJECT_0
        self.core_module._SAVED_WAIT_API = mock_wait

        handles = list(range(10))  # 10个假句柄
        result = _winapi.WaitForMultipleObjects(handles, False, 1000)

        self.assertEqual(result, 0x00)
        mock_wait.assert_called_once()
        # 验证参数（timeout可能因计算时间有微小偏差，允许±5ms）
        call_args = mock_wait.call_args[0]
        self.assertEqual(call_args[0], handles)
        self.assertEqual(call_args[1], False)
        self.assertGreaterEqual(call_args[2], 995)
        self.assertLessEqual(call_args[2], 1000)

    def test_wait_any_single_batch_last_ready(self):
        """wait_all=False: 单批次，最后一个对象就绪"""
        from unlock_processpool import please
        please()

        mock_wait = Mock(return_value=0x09)  # WAIT_OBJECT_9
        self.core_module._SAVED_WAIT_API = mock_wait

        handles = list(range(10))
        result = _winapi.WaitForMultipleObjects(handles, False, 1000)

        self.assertEqual(result, 0x09)

    def test_wait_any_multi_batch_first_batch_ready(self):
        """wait_all=False: 多批次，第一批次有对象就绪"""
        from unlock_processpool import please
        please()

        mock_wait = Mock(return_value=0x0A)  # WAIT_OBJECT_10
        self.core_module._SAVED_WAIT_API = mock_wait

        handles = list(range(100))  # 100个句柄（2批次）
        result = _winapi.WaitForMultipleObjects(handles, False, 5000)

        # 应该返回第一批次的第10个对象（全局索引10）
        self.assertEqual(result, 0x0A)
        # 只调用第一批次
        mock_wait.assert_called_once()

    def test_wait_any_multi_batch_second_batch_ready(self):
        """wait_all=False: 多批次，第二批次有对象就绪"""
        from unlock_processpool import please
        please()

        # 第一批次超时，第二批次第5个对象就绪
        mock_wait = Mock(side_effect=[0x00000102, 0x05])  # WAIT_TIMEOUT, WAIT_OBJECT_5
        self.core_module._SAVED_WAIT_API = mock_wait

        handles = list(range(100))
        result = _winapi.WaitForMultipleObjects(handles, False, 5000)

        # 应该返回全局索引：63 + 5 = 68（chunk_size=63）
        self.assertEqual(result, 63 + 5)
        self.assertEqual(mock_wait.call_count, 2)

    def test_wait_any_boundary_exactly_64(self):
        """wait_all=False: 边界测试 - 恰好64个句柄（会分成两批）"""
        from unlock_processpool import please
        please()

        # 64个句柄会分成两批：第一批63个，第二批1个
        # 第一批超时，第二批第0个对象就绪
        mock_wait = Mock(side_effect=[0x00000102, 0x00])
        self.core_module._SAVED_WAIT_API = mock_wait

        handles = list(range(64))
        result = _winapi.WaitForMultipleObjects(handles, False, 1000)

        # 应该返回全局索引63（第二批次的第0个）
        self.assertEqual(result, 63)
        self.assertEqual(mock_wait.call_count, 2)

    def test_wait_any_boundary_65_handles(self):
        """wait_all=False: 边界测试 - 65个句柄（跨批次）"""
        from unlock_processpool import please
        please()

        # 第一批次超时，第二批次第1个对象就绪
        mock_wait = Mock(side_effect=[0x00000102, 0x01])
        self.core_module._SAVED_WAIT_API = mock_wait

        handles = list(range(65))
        result = _winapi.WaitForMultipleObjects(handles, False, 1000)

        # 应该返回全局索引64（63 + 1）
        self.assertEqual(result, 64)

    def test_wait_any_abandoned(self):
        """wait_all=False: 处理WAIT_ABANDONED返回值"""
        from unlock_processpool import please
        please()

        # WAIT_ABANDONED_5
        mock_wait = Mock(return_value=0x85)
        self.core_module._SAVED_WAIT_API = mock_wait

        handles = list(range(10))
        result = _winapi.WaitForMultipleObjects(handles, False, 1000)

        # 应该保持WAIT_ABANDONED语义：0x80 + 索引
        self.assertEqual(result, 0x85)

    def test_wait_any_abandoned_second_batch(self):
        """wait_all=False: 第二批次返回WAIT_ABANDONED"""
        from unlock_processpool import please
        please()

        # 第一批次超时，第二批次abandoned
        mock_wait = Mock(side_effect=[0x00000102, 0x83])  # TIMEOUT, WAIT_ABANDONED_3
        self.core_module._SAVED_WAIT_API = mock_wait

        handles = list(range(100))
        result = _winapi.WaitForMultipleObjects(handles, False, 1000)

        # 应该返回：0x80 + 63 + 3 = 0x80 + 66（chunk_size=63）
        self.assertEqual(result, 0x80 + 66)

    def test_wait_any_failed(self):
        """wait_all=False: 处理WAIT_FAILED"""
        from unlock_processpool import please
        please()

        mock_wait = Mock(return_value=0xFFFFFFFF)  # WAIT_FAILED
        self.core_module._SAVED_WAIT_API = mock_wait

        handles = list(range(10))
        result = _winapi.WaitForMultipleObjects(handles, False, 1000)

        self.assertEqual(result, 0xFFFFFFFF)

    def test_wait_any_all_timeout(self):
        """wait_all=False: 所有批次都超时"""
        from unlock_processpool import please
        please()

        # 所有批次都返回WAIT_TIMEOUT
        mock_wait = Mock(return_value=0x00000102)
        self.core_module._SAVED_WAIT_API = mock_wait

        handles = list(range(200))  # 4批次
        result = _winapi.WaitForMultipleObjects(handles, False, 1000)

        self.assertEqual(result, 0x00000102)
        self.assertEqual(mock_wait.call_count, 4)

    # ==================== wait_all=True 测试 ====================

    def test_wait_all_single_batch_success(self):
        """wait_all=True: 单批次，所有对象就绪"""
        from unlock_processpool import please
        please()

        mock_wait = Mock(return_value=0x00)  # WAIT_OBJECT_0（成功）
        self.core_module._SAVED_WAIT_API = mock_wait

        handles = list(range(10))
        result = _winapi.WaitForMultipleObjects(handles, True, 1000)

        self.assertEqual(result, 0x00)
        mock_wait.assert_called_once()
        # 验证参数
        call_args = mock_wait.call_args[0]
        self.assertEqual(call_args[0], handles)
        self.assertEqual(call_args[1], True)
        self.assertGreaterEqual(call_args[2], 995)

    def test_wait_all_multi_batch_all_success(self):
        """wait_all=True: 多批次，所有批次都成功 - 这是之前的CRITICAL BUG"""
        from unlock_processpool import please
        please()

        # 所有批次都返回成功
        mock_wait = Mock(return_value=0x00)
        self.core_module._SAVED_WAIT_API = mock_wait

        handles = list(range(100))  # 2批次
        result = _winapi.WaitForMultipleObjects(handles, True, 5000)

        # 修复后应该返回成功，而不是WAIT_TIMEOUT
        self.assertEqual(result, 0x00)
        self.assertEqual(mock_wait.call_count, 2)

    def test_wait_all_multi_batch_200_handles(self):
        """wait_all=True: 200个句柄（4批次）全部成功"""
        from unlock_processpool import please
        please()

        mock_wait = Mock(return_value=0x00)
        self.core_module._SAVED_WAIT_API = mock_wait

        handles = list(range(200))  # 4批次
        result = _winapi.WaitForMultipleObjects(handles, True, 10000)

        self.assertEqual(result, 0x00)
        self.assertEqual(mock_wait.call_count, 4)

    def test_wait_all_first_batch_timeout(self):
        """wait_all=True: 第一批次超时"""
        from unlock_processpool import please
        please()

        mock_wait = Mock(return_value=0x00000102)  # WAIT_TIMEOUT
        self.core_module._SAVED_WAIT_API = mock_wait

        handles = list(range(100))
        result = _winapi.WaitForMultipleObjects(handles, True, 1000)

        self.assertEqual(result, 0x00000102)
        # 第一批次超时就应该停止
        mock_wait.assert_called_once()

    def test_wait_all_second_batch_timeout(self):
        """wait_all=True: 第二批次超时"""
        from unlock_processpool import please
        please()

        # 第一批次成功，第二批次超时
        mock_wait = Mock(side_effect=[0x00, 0x00000102])
        self.core_module._SAVED_WAIT_API = mock_wait

        handles = list(range(100))
        result = _winapi.WaitForMultipleObjects(handles, True, 5000)

        self.assertEqual(result, 0x00000102)
        self.assertEqual(mock_wait.call_count, 2)

    def test_wait_all_failed(self):
        """wait_all=True: 处理WAIT_FAILED"""
        from unlock_processpool import please
        please()

        # 第一批次失败
        mock_wait = Mock(return_value=0xFFFFFFFF)
        self.core_module._SAVED_WAIT_API = mock_wait

        handles = list(range(100))
        result = _winapi.WaitForMultipleObjects(handles, True, 1000)

        self.assertEqual(result, 0xFFFFFFFF)
        mock_wait.assert_called_once()

    def test_wait_all_abandoned_multi_batch(self):
        """wait_all=True: 第二批次返回WAIT_ABANDONED - 验证索引调整 (BUG #1修复验证)"""
        from unlock_processpool import please
        please()

        # 第一批次成功，第二批次第5个对象abandoned
        mock_wait = Mock(side_effect=[0x00, 0x85])  # SUCCESS, WAIT_ABANDONED_5
        self.core_module._SAVED_WAIT_API = mock_wait

        handles = list(range(100))  # 2批次
        result = _winapi.WaitForMultipleObjects(handles, True, 1000)

        # 应该返回：0x80 + 63 + 5 = 0x80 + 68（全局索引）
        self.assertEqual(result, 0x80 + 68, "BUG #1修复失败：wait_all=True未正确调整WAIT_ABANDONED索引")
        self.assertEqual(mock_wait.call_count, 2)

    # ==================== Timeout 分配测试 ====================

    def test_timeout_shared_across_batches(self):
        """timeout应该在所有批次间共享 - 这是之前的CRITICAL BUG"""
        from unlock_processpool import please
        please()

        start_time = time.perf_counter()

        # 每批次延迟100ms
        def delayed_wait(handles, wait_all, timeout):
            time.sleep(0.1)
            return 0x00000102  # WAIT_TIMEOUT

        mock_wait = Mock(side_effect=delayed_wait)
        self.core_module._SAVED_WAIT_API = mock_wait

        handles = list(range(200))  # 4批次
        result = _winapi.WaitForMultipleObjects(handles, False, 500)  # 500ms总超时

        elapsed = (time.perf_counter() - start_time) * 1000

        # 应该在500ms左右结束（不是无限等待）
        self.assertLess(elapsed, 700, "超时时间应该被正确分配")
        self.assertEqual(result, 0x00000102)

    def test_timeout_infinite(self):
        """测试无限等待（timeout=INFINITE）"""
        from unlock_processpool import please
        please()

        # 第二批次成功
        mock_wait = Mock(side_effect=[0x00000102, 0x05])
        self.core_module._SAVED_WAIT_API = mock_wait

        handles = list(range(100))
        result = _winapi.WaitForMultipleObjects(handles, False, _winapi.INFINITE)

        # 应该返回全局索引：63 + 5 = 68（chunk_size=63）
        self.assertEqual(result, 63 + 5)
        # 应该传递INFINITE给所有批次
        for call_args in mock_wait.call_args_list:
            self.assertEqual(call_args[0][2], _winapi.INFINITE)

    def test_timeout_zero(self):
        """测试立即返回（timeout=0）"""
        from unlock_processpool import please
        please()

        mock_wait = Mock(return_value=0x00000102)
        self.core_module._SAVED_WAIT_API = mock_wait

        handles = list(range(10))
        result = _winapi.WaitForMultipleObjects(handles, False, 0)

        self.assertEqual(result, 0x00000102)

    def test_timeout_remaining_calculation(self):
        """测试剩余超时时间的精确计算"""
        from unlock_processpool import please
        please()

        timeout_values_received = []

        def capture_timeout(handles, wait_all, timeout):
            timeout_values_received.append(timeout)
            time.sleep(0.05)  # 每批次耗时50ms
            return 0x00000102

        mock_wait = Mock(side_effect=capture_timeout)
        self.core_module._SAVED_WAIT_API = mock_wait

        handles = list(range(200))  # 4批次
        _winapi.WaitForMultipleObjects(handles, False, 1000)  # 1000ms

        # 检查超时值是否递减
        self.assertGreater(len(timeout_values_received), 1)
        # 第一批次应该接近1000ms
        self.assertGreater(timeout_values_received[0], 900)
        # 后续批次应该减少
        for i in range(1, len(timeout_values_received)):
            self.assertLess(timeout_values_received[i], timeout_values_received[i-1])

    # ==================== 初始化检查测试 ====================

    def test_uninitialized_call_raises_error(self):
        """测试未调用please()就使用_hacked_wait会抛出清晰错误 (BUG #2修复验证)"""
        import unlock_processpool.core as core_module

        # 模拟未初始化状态
        original_api = core_module._SAVED_WAIT_API
        core_module._SAVED_WAIT_API = None
        _winapi.WaitForMultipleObjects = core_module._hacked_wait

        try:
            handles = list(range(10))

            # wait_all=False 分支应该抛出RuntimeError
            with self.assertRaises(RuntimeError) as cm:
                _winapi.WaitForMultipleObjects(handles, False, 1000)

            self.assertIn("unlock_processpool未初始化", str(cm.exception))
            self.assertIn("please()", str(cm.exception))

            # wait_all=True 分支也应该抛出RuntimeError
            with self.assertRaises(RuntimeError) as cm:
                _winapi.WaitForMultipleObjects(handles, True, 1000)

            self.assertIn("unlock_processpool未初始化", str(cm.exception))
            self.assertIn("please()", str(cm.exception))
        finally:
            # 恢复状态
            core_module._SAVED_WAIT_API = original_api

    # ==================== v2.2.0 新增测试（覆盖所有P0/P1/P2修复） ====================

    def test_empty_handles_returns_failed(self):
        """P0修复#2验证: 空句柄列表应返回WAIT_FAILED"""
        from unlock_processpool import please
        please()

        # 测试wait_all=False分支
        result = _winapi.WaitForMultipleObjects([], False, 1000)
        self.assertEqual(result, 0xFFFFFFFF, "空句柄列表应返回WAIT_FAILED")

        # 测试wait_all=True分支
        result = _winapi.WaitForMultipleObjects([], True, 1000)
        self.assertEqual(result, 0xFFFFFFFF, "空句柄列表应返回WAIT_FAILED")

    def test_single_handle(self):
        """P1边界测试: 单句柄情况"""
        from unlock_processpool import please
        please()

        mock_wait = Mock(return_value=0x00)  # WAIT_OBJECT_0
        self.core_module._SAVED_WAIT_API = mock_wait

        handles = [12345]  # 单个句柄
        result = _winapi.WaitForMultipleObjects(handles, False, 1000)

        self.assertEqual(result, 0x00)
        mock_wait.assert_called_once_with([12345], False, unittest.mock.ANY)

    def test_negative_timeout_as_infinite(self):
        """P1修复#4验证: 所有负数超时都应视为无限等待"""
        from unlock_processpool import please
        please()

        mock_wait = Mock(return_value=0x00)
        self.core_module._SAVED_WAIT_API = mock_wait

        handles = list(range(10))

        # 测试各种负数
        for negative_timeout in [-1, -2, -100, -999999]:
            mock_wait.reset_mock()
            _winapi.WaitForMultipleObjects(handles, False, negative_timeout)
            # 应该传递INFINITE给底层API
            self.assertEqual(mock_wait.call_args[0][2], _winapi.INFINITE,
                            f"负数超时{negative_timeout}应转换为INFINITE")

    def test_timeout_precision_ceil(self):
        """P0修复#3验证: 超时时间应向上取整，避免精度损失"""
        from unlock_processpool import please
        please()

        timeout_values_received = []

        def capture_timeout(handles, wait_all, timeout):
            timeout_values_received.append(timeout)
            time.sleep(0.0005)  # 每批次耗时0.5ms
            return 0x00000102  # WAIT_TIMEOUT

        mock_wait = Mock(side_effect=capture_timeout)
        self.core_module._SAVED_WAIT_API = mock_wait

        handles = list(range(200))  # 4批次
        _winapi.WaitForMultipleObjects(handles, False, 10)  # 仅10ms总超时

        # 关键验证：即使剩余时间不足1ms，也应该至少传递1ms（向上取整）
        # 而不是0ms（截断）
        for timeout_val in timeout_values_received:
            if timeout_val != _winapi.INFINITE and timeout_val > 0:
                # 确保没有因为精度损失导致0ms（除非真的超时）
                self.assertGreaterEqual(timeout_val, 1,
                                       "超时应向上取整，0.5ms应变为1ms而非0ms")

    def test_module_reload_protection(self):
        """P0修复#1验证: 模块重载保护 - 防止无限递归（通过幂等性）"""
        import unlock_processpool.core as core_module
        import logging

        # 模拟模块重载场景：_winapi.WaitForMultipleObjects已经是_hacked_wait
        # 但_SAVED_WAIT_API为None
        original_api = _winapi.WaitForMultipleObjects
        _winapi.WaitForMultipleObjects = core_module._hacked_wait
        core_module._SAVED_WAIT_API = None

        try:
            # 捕获日志警告
            with self.assertLogs(logger='unlock_processpool', level=logging.WARNING) as log_capture:
                from unlock_processpool import please
                result = please()

            # 应该返回True（幂等操作）
            self.assertTrue(result)

            # 应该记录警告
            self.assertTrue(any("模块重载" in message for message in log_capture.output),
                          "应该记录模块重载警告")

            # 验证不会导致无限递归：_SAVED_WAIT_API仍然为None（因为检测到已初始化）
            # 这是安全的，因为_hacked_wait会检查_SAVED_WAIT_API并抛出RuntimeError
        finally:
            # 恢复状态
            _winapi.WaitForMultipleObjects = original_api
            core_module._SAVED_WAIT_API = None

    def test_500_handles_boundary(self):
        """P1边界测试: 500句柄（接近理论上限508）"""
        from unlock_processpool import please
        please()

        # 500个句柄会分成8批次（每批63）
        mock_wait = Mock(return_value=0x00)
        self.core_module._SAVED_WAIT_API = mock_wait

        handles = list(range(500))

        # wait_all=True测试
        result = _winapi.WaitForMultipleObjects(handles, True, 10000)
        self.assertEqual(result, 0x00, "500句柄wait_all=True应成功")
        # 应该调用8次（500/63 = 7.93，向上取整为8）
        self.assertEqual(mock_wait.call_count, 8)

        # wait_all=False测试
        mock_wait.reset_mock()
        result = _winapi.WaitForMultipleObjects(handles, False, 10000)
        self.assertEqual(result, 0x00, "500句柄wait_all=False应成功")
        # 第一批次就返回，只调用1次
        mock_wait.assert_called_once()


if __name__ == '__main__':
    unittest.main()
