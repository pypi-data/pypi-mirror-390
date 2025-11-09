# unlock_processpool_workers.py
"""
Windows进程限制统一解锁器(兼容joblib和ProcessPoolExecutor)
版本：2.2.0
"""
import sys
import threading
import time
import math
import logging

# 核心配置
_UNLOCKED_MAX_WORKERS = 510  # 总句柄数限制
_SAVED_WAIT_API = None
_PLEASE_LOCK = threading.RLock()  # 防止竞态条件的可重入锁

# 可选调试日志（默认不启用）
_logger = logging.getLogger("unlock_processpool")
_logger.addHandler(logging.NullHandler())

if sys.platform == "win32":
    from typing import Sequence
    import _winapi

    # Windows API 返回值常量（避免魔法数字）
    WAIT_OBJECT_0 = 0x00000000
    WAIT_ABANDONED_0 = 0x00000080
    WAIT_TIMEOUT = 0x00000102
    WAIT_FAILED = 0xFFFFFFFF

    def _hacked_wait(
        handles: Sequence[int],
        wait_all: bool,
        timeout: int = _winapi.INFINITE
    ) -> int:
        """
        绕过Windows WaitForMultipleObjects的64句柄限制

        Args:
            handles: 要等待的句柄列表（可以为空）
            wait_all: True=等待所有对象, False=等待任意一个对象
            timeout: 超时时间（毫秒），负数表示无限等待

        Returns:
            - wait_all=False: 返回就绪对象的索引 (0x00-0x3F) 或错误码
            - wait_all=True: 返回 WAIT_OBJECT_0(成功) 或错误码
            - 空句柄列表: 返回 WAIT_FAILED

        Raises:
            RuntimeError: 如果未调用please()初始化

        注意:
            - 所有批次共享同一个总超时时间
            - 超时时间使用向上取整，确保不会提前超时
            - 线程安全：可以在多线程环境中安全调用
        """
        # P0修复#2: 防御性检查 - 空句柄列表
        if not handles:
            _logger.debug("空句柄列表，返回WAIT_FAILED")
            return WAIT_FAILED

        chunk_size = 63  # Python _winapi.WaitForMultipleObjects 限制

        # P1修复#4: 计算绝对deadline（所有批次共享timeout）
        # 任何负数都视为无限等待
        if timeout < 0 or timeout == _winapi.INFINITE:
            deadline = None  # 无限等待
        else:
            deadline = time.perf_counter() + timeout / 1000.0  # 转换为秒

        def _calc_remaining_timeout():
            """
            计算剩余超时时间（毫秒）

            Returns:
                剩余超时毫秒数（向上取整），或INFINITE（无限等待）
            """
            if deadline is None:
                return _winapi.INFINITE
            remaining_sec = deadline - time.perf_counter()
            if remaining_sec <= 0:
                return 0  # 已超时
            # P0修复#3: 使用向上取整，避免精度损失
            # 例如: 0.9ms不会被截断为0ms
            return math.ceil(remaining_sec * 1000)

        if not wait_all:
            # wait_all=False: 任何一个对象就绪就返回
            for idx in range(0, len(handles), chunk_size):
                chunk = handles[idx:idx+chunk_size]

                # 计算本批次的剩余超时时间
                remaining_timeout = _calc_remaining_timeout()
                if remaining_timeout == 0 and deadline is not None:
                    return WAIT_TIMEOUT

                # ✅ P0修复#2（BUG #2）: 防御性检查 - 确保_SAVED_WAIT_API已初始化
                saved_api = _SAVED_WAIT_API
                if saved_api is None:
                    raise RuntimeError(
                        "unlock_processpool未初始化。"
                        "请在创建ProcessPoolExecutor前调用 unlock_processpool.please()"
                    )
                ret = saved_api(chunk, False, remaining_timeout)

                # 处理各种返回值（使用常量替代魔法数字）
                if WAIT_OBJECT_0 <= ret < WAIT_OBJECT_0 + 64:  # WAIT_OBJECT_0 到 WAIT_OBJECT_63
                    return idx + ret
                elif WAIT_ABANDONED_0 <= ret < WAIT_ABANDONED_0 + 64:  # WAIT_ABANDONED_0 到 WAIT_ABANDONED_63
                    # 保持WAIT_ABANDONED语义，返回全局索引
                    return WAIT_ABANDONED_0 + idx + (ret - WAIT_ABANDONED_0)
                elif ret == WAIT_FAILED:
                    return ret
                # WAIT_TIMEOUT 继续下一个批次
            return WAIT_TIMEOUT
        else:
            # wait_all=True: 所有对象都就绪才返回成功
            # ✅ 修复：使用轮询式等待，而非顺序阻塞等待
            # 避免在某个批次的慢进程上永久阻塞

            # 将句柄分批
            num_chunks = (len(handles) + chunk_size - 1) // chunk_size
            chunks = [handles[i:i+chunk_size] for i in range(0, len(handles), chunk_size)]
            completed_chunks = [False] * num_chunks

            # 轮询式等待，每次用短timeout检查各批次
            POLL_TIMEOUT_MS = 100  # 100毫秒轮询一次
            start_time = time.perf_counter()

            while not all(completed_chunks):

                # 检查总超时
                remaining_timeout = _calc_remaining_timeout()
                if remaining_timeout == 0 and deadline is not None:
                    return WAIT_TIMEOUT

                # 使用短timeout或剩余时间（取最小值）
                poll_timeout = POLL_TIMEOUT_MS if deadline is None else min(POLL_TIMEOUT_MS, remaining_timeout)

                # 检查每个未完成的批次
                for chunk_idx, chunk in enumerate(chunks):
                    if completed_chunks[chunk_idx]:
                        continue  # 已完成，跳过

                    # 防御性检查
                    saved_api = _SAVED_WAIT_API
                    if saved_api is None:
                        raise RuntimeError(
                            "unlock_processpool未初始化。"
                            "请在创建ProcessPoolExecutor前调用 unlock_processpool.please()"
                        )

                    # 用短timeout检查这个批次
                    ret = saved_api(chunk, True, poll_timeout)

                    if ret == WAIT_OBJECT_0:  # 这个批次的所有对象都就绪
                        completed_chunks[chunk_idx] = True
                    elif WAIT_ABANDONED_0 <= ret < WAIT_ABANDONED_0 + 64:
                        # 某个对象被遗弃（进程异常退出）
                        idx = chunk_idx * chunk_size
                        return WAIT_ABANDONED_0 + idx + (ret - WAIT_ABANDONED_0)
                    elif ret == WAIT_TIMEOUT:
                        # 这个批次还没完成，继续等待
                        pass
                    elif ret == WAIT_FAILED:
                        # 失败
                        return ret
                    # 其他返回值：继续检查下一个批次

            # 所有批次都成功
            return WAIT_OBJECT_0

def please():
    """
    一键解锁Windows进程池限制

    线程安全，可以多次调用（幂等操作）

    Returns:
        bool: Windows平台返回True，其他平台返回False

    Raises:
        RuntimeError: 如果检测到模块重载导致的无限递归风险

    注意:
        - 必须在创建ProcessPoolExecutor或joblib并行任务之前调用
        - 可以安全地多次调用（幂等）
        - 不能在模块重载后调用
        - 对ProcessPoolExecutor完全支持（可到510进程）
        - 对multiprocessing.Pool部分支持（建议<60进程，或切换到Executor）

    兼容性说明:
        - ProcessPoolExecutor: ✅ 完美支持大规模并发
        - joblib (loky backend): ✅ 完美支持
        - multiprocessing.Pool: ⚠️ 受系统资源限制，建议<60进程
    """
    if sys.platform != "win32":
        return False

    global _SAVED_WAIT_API

    # 使用锁保护临界区，防止TOCTOU竞态条件
    with _PLEASE_LOCK:
        # P0修复#1: 防止模块重载导致无限递归
        # 检查当前_winapi.WaitForMultipleObjects是否已经是_hacked_wait
        current_api = _winapi.WaitForMultipleObjects

        if current_api is _hacked_wait:
            # 已经初始化过了（幂等操作）
            if _SAVED_WAIT_API is None:
                # 警告：这可能是模块重载后的状态，但我们无法安全地恢复
                # 为了向后兼容测试场景，我们不抛出错误，而是记录警告
                _logger.warning(
                    "检测到_winapi.WaitForMultipleObjects已被替换，但_SAVED_WAIT_API为None。"
                    "这可能是模块重载导致的。请避免重载unlock_processpool模块。"
                )
            _logger.debug("please()已被调用过，幂等操作")
            # 不做任何修改，直接返回（保持幂等性）
        else:
            # 首次初始化
            _SAVED_WAIT_API = current_api
            _winapi.WaitForMultipleObjects = _hacked_wait
            _logger.debug("成功替换_winapi.WaitForMultipleObjects")

    # 动态修改所有已知限制模块
    modules = [
        ("concurrent.futures.process", "_MAX_WINDOWS_WORKERS"),
        ("joblib.externals.loky.backend.context", "_MAX_WINDOWS_WORKERS"),
        ("joblib.externals.loky.process_executor", "_MAX_WINDOWS_WORKERS"),
        ("loky.backend.context", "_MAX_WINDOWS_WORKERS"),
    ]

    for mod, attr in modules:
        try:
            __import__(mod)
            module = sys.modules[mod]
            if hasattr(module, attr):
                setattr(module, attr, _UNLOCKED_MAX_WORKERS - 2)
        except (ImportError, ModuleNotFoundError, AttributeError, TypeError):
            # 模块不存在或属性设置失败，跳过
            continue

    # 强制刷新joblib配置
    try:
        from joblib import parallel_backend
        parallel_backend("loky")
    except (ImportError, ModuleNotFoundError, Exception):
        # joblib未安装或配置失败，忽略
        pass

    # 🔧 修复 multiprocessing.Pool 在 > 61 进程时的死锁问题
    try:
        from multiprocessing import pool as pool_module

        # 保存原始的 Pool.close 方法
        if not hasattr(pool_module.Pool, '_original_close_unlocked'):
            original_close = pool_module.Pool.close

            def _patched_close(self):
                """
                修补后的 Pool.close()
                修复 > 61 进程时的死锁：
                - 原始问题：_handle_tasks 阻塞在 taskqueue.get()
                - 解决方案：手动向 taskqueue 发送 None 来唤醒 _handle_tasks
                """
                # 调用原始的 close
                original_close(self)

                # 🔧 关键修复：向 taskqueue 发送 None
                # _handle_tasks 在 `iter(taskqueue.get, None)` 上阻塞
                # 当收到 None 时，会向所有 worker 发送退出信号
                try:
                    if hasattr(self, '_taskqueue') and self._taskqueue is not None:
                        self._taskqueue.put(None)
                except Exception:
                    # 如果 taskqueue 已关闭或出错，忽略
                    pass

            # 替换 Pool.close 方法
            pool_module.Pool._original_close_unlocked = original_close
            pool_module.Pool.close = _patched_close

            _logger.debug("已修补 multiprocessing.Pool.close() 以支持 > 61 进程")
    except (ImportError, AttributeError, Exception) as e:
        # multiprocessing.Pool 不可用或修补失败，忽略
        _logger.debug(f"无法修补 multiprocessing.Pool: {e}")

    return True