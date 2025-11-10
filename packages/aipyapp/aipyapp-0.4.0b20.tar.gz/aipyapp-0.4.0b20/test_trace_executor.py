#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试 Trace 方案的超时和中断机制
"""

import sys
import time
import threading
import traceback
from io import StringIO


class StoppableEvent:
    """模拟 Stoppable 的 stop_event"""
    def __init__(self):
        self._event = threading.Event()

    def set(self):
        self._event.set()

    def is_set(self):
        return self._event.is_set()

    def clear(self):
        self._event.clear()


class TraceExecutor:
    """使用 Trace 方案的执行器"""

    def __init__(self, timeout=30):
        self.timeout = timeout
        self.stop_event = StoppableEvent()

    def execute(self, code_str, globals_dict=None):
        """执行代码，支持超时和中断"""
        if globals_dict is None:
            globals_dict = {'__name__': '__main__'}

        # 准备执行环境
        gs = globals_dict.copy()
        captured_stdout = StringIO()
        captured_stderr = StringIO()
        old_stdout, old_stderr = sys.stdout, sys.stderr
        sys.stdout, sys.stderr = captured_stdout, captured_stderr

        # 编译代码
        try:
            code_obj = compile(code_str, '<block>', 'exec')
        except SyntaxError as e:
            sys.stdout, sys.stderr = old_stdout, old_stderr
            return {
                'success': False,
                'error': f"Syntax error: {str(e)}",
                'stdout': '',
                'stderr': ''
            }

        # 设置超时和中断机制
        timeout_event = threading.Event()
        timer = threading.Timer(self.timeout, timeout_event.set)
        timer.daemon = True

        def trace_func(frame, event, arg):
            if event == 'call':  # 仅在函数调用时检查
                if self.stop_event.is_set():
                    raise KeyboardInterrupt("Execution interrupted by user")
                if timeout_event.is_set():
                    raise TimeoutError(f"Execution timed out after {self.timeout}s")
            return trace_func

        # 执行代码
        error = None
        tb = None
        sys.settrace(trace_func)
        timer.start()

        try:
            exec(code_obj, gs)
        except (KeyboardInterrupt, TimeoutError) as e:
            error = str(e)
            tb = traceback.format_exc()
        except Exception as e:
            error = str(e)
            tb = traceback.format_exc()
        finally:
            sys.settrace(None)
            timer.cancel()
            sys.stdout, sys.stderr = old_stdout, old_stderr

        # 收集结果
        stdout = captured_stdout.getvalue().strip()
        stderr = captured_stderr.getvalue().strip()

        return {
            'success': error is None,
            'error': error,
            'traceback': tb,
            'stdout': stdout,
            'stderr': stderr,
            'globals': gs
        }


def test_normal_execution():
    """测试正常执行"""
    print("\n=== Test 1: 正常执行 ===")
    executor = TraceExecutor(timeout=5)

    code = """
x = 10
y = 20
print(f"Result: {x + y}")
z = x * y
"""

    result = executor.execute(code)
    print(f"成功: {result['success']}")
    print(f"输出: {result['stdout']}")
    print(f"z 值: {result['globals'].get('z', 'N/A')}")
    assert result['success'], "正常执行应该成功"
    assert "30" in result['stdout'], "输出应包含 30"
    print("✅ 通过")


def test_timeout_with_function_calls():
    """测试有函数调用的超时"""
    print("\n=== Test 2: 有函数调用的无限循环（应该超时）===")
    executor = TraceExecutor(timeout=1)

    code = """
import time
count = 0
while True:
    time.sleep(0.05)  # 函数调用，会触发 trace
    count += 1
    # 移除安全阈值，让它真正无限循环
print(f"Completed {count} iterations")
"""

    result = executor.execute(code)
    print(f"成功: {result['success']}")
    print(f"错误: {result['error']}")
    assert not result['success'], "应该超时失败"
    assert "timeout" in result['error'].lower(), "错误信息应包含 timeout"
    print("✅ 通过")


def test_timeout_without_function_calls():
    """测试没有函数调用的死循环（延迟响应）"""
    print("\n=== Test 3: 纯死循环（没有函数调用）===")
    executor = TraceExecutor(timeout=2)

    code = """
count = 0
start = __import__('time').time()
while True:
    count += 1
    # 没有函数调用，trace 不会被触发
    # 只能靠 timer 中断
"""

    start_time = time.time()
    result = executor.execute(code)
    elapsed = time.time() - start_time

    print(f"成功: {result['success']}")
    print(f"错误: {result['error']}")
    print(f"耗时: {elapsed:.2f} 秒")

    assert not result['success'], "应该超时失败"
    assert "timeout" in result['error'].lower(), "错误信息应包含 timeout"
    # 这种情况下延迟较大（大约 2 秒），但仍然被中断
    print(f"✅ 通过（延迟 ~{elapsed:.1f}s，预期 ~2s）")


def test_user_interrupt():
    """测试用户中断"""
    print("\n=== Test 4: 用户中断 ===")
    executor = TraceExecutor(timeout=10)

    code = """
import time
count = 0
while True:
    time.sleep(0.1)
    count += 1
    print(f"Iteration {count}")
"""

    # 在后台线程中执行，等待 0.5 秒后中断
    result_container = [None]

    def run_in_thread():
        result_container[0] = executor.execute(code)

    thread = threading.Thread(target=run_in_thread)
    thread.start()

    # 等待一些迭代后中断
    time.sleep(0.5)
    executor.stop_event.set()

    thread.join(timeout=2)
    result = result_container[0]

    print(f"成功: {result['success']}")
    print(f"错误: {result['error']}")
    print(f"输出行数: {len(result['stdout'].split(chr(10)))}")

    assert not result['success'], "应该被中断"
    assert "interrupted" in result['error'].lower(), "错误信息应包含 interrupted"
    print("✅ 通过")


def test_exception_handling():
    """测试异常捕获"""
    print("\n=== Test 5: 异常捕获 ===")
    executor = TraceExecutor(timeout=5)

    code = """
x = 10
y = 0
result = x / y  # 会抛出 ZeroDivisionError
"""

    result = executor.execute(code)
    print(f"成功: {result['success']}")
    print(f"错误: {result['error']}")

    assert not result['success'], "应该捕获异常"
    assert "ZeroDivisionError" in result['error'], "应该检测到 ZeroDivisionError"
    print("✅ 通过")


def test_stdout_capture():
    """测试输出捕获"""
    print("\n=== Test 6: 输出捕获 ===")
    executor = TraceExecutor(timeout=5)

    code = """
print("Line 1")
print("Line 2")
import sys
sys.stderr.write("Error message\\n")
"""

    result = executor.execute(code)
    print(f"成功: {result['success']}")
    print(f"stdout: {result['stdout']}")
    print(f"stderr: {result['stderr']}")

    assert result['success'], "应该成功执行"
    assert "Line 1" in result['stdout'], "应该捕获 stdout"
    assert "Line 2" in result['stdout'], "应该捕获 stdout"
    assert "Error message" in result['stderr'], "应该捕获 stderr"
    print("✅ 通过")


def test_global_state():
    """测试全局变量保存"""
    print("\n=== Test 7: 全局变量状态 ===")
    executor = TraceExecutor(timeout=5)

    initial_globals = {'x': 5}

    code = """
x = x + 10
y = x * 2
z = [1, 2, 3]
d = {'key': 'value'}
"""

    result = executor.execute(code, initial_globals)
    print(f"成功: {result['success']}")
    print(f"x: {result['globals'].get('x')}")
    print(f"y: {result['globals'].get('y')}")
    print(f"z: {result['globals'].get('z')}")
    print(f"d: {result['globals'].get('d')}")

    assert result['success'], "应该成功执行"
    assert result['globals']['x'] == 15, "x 应该是 15"
    assert result['globals']['y'] == 30, "y 应该是 30"
    assert result['globals']['z'] == [1, 2, 3], "z 应该是列表"
    assert result['globals']['d'] == {'key': 'value'}, "d 应该是字典"
    print("✅ 通过")


if __name__ == '__main__':
    print("=" * 50)
    print("Trace 执行器测试套件")
    print("=" * 50)

    try:
        test_normal_execution()
        test_timeout_with_function_calls()
        test_timeout_without_function_calls()
        test_user_interrupt()
        test_exception_handling()
        test_stdout_capture()
        test_global_state()

        print("\n" + "=" * 50)
        print("✅ 所有测试通过！")
        print("=" * 50)
    except AssertionError as e:
        print(f"\n❌ 测试失败: {e}")
        traceback.print_exc()
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 异常: {e}")
        traceback.print_exc()
        sys.exit(1)
