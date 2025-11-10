#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
简化的 Trace 方案测试 - 重点测试超时和中断
"""

import sys
import time
import threading
import traceback
from io import StringIO


print("=== Test 1: 基础 Trace 功能 ===")

timeout_flag = False
stop_flag = False

def trace_func(frame, event, arg):
    global timeout_flag, stop_flag
    if event == 'call':
        if stop_flag:
            raise KeyboardInterrupt("User interrupted")
        if timeout_flag:
            raise TimeoutError("Timeout!")
    return trace_func

# 测试 1：正常执行
print("\n1. 正常执行")
code = "x = 1 + 1\nprint(x)"
gs = {}
sys.settrace(trace_func)
exec(code, gs)
sys.settrace(None)
print("✅ 正常执行")

# 测试 2：通过设置 timeout_flag 触发超时
print("\n2. 触发超时")
code = """
def loop():
    for i in range(1000000):
        pass

loop()
"""

gs = {}
timeout_flag = False
sys.settrace(trace_func)

try:
    timeout_flag = True  # 设置超时标志
    exec(code, gs)
    print("❌ 没有超时")
except TimeoutError as e:
    print(f"✅ 捕获到超时: {e}")
finally:
    sys.settrace(None)
    timeout_flag = False

# 测试 3：通过设置 stop_flag 触发中断
print("\n3. 触发中断")
code = """
def loop():
    for i in range(1000000):
        pass

loop()
"""

gs = {}
stop_flag = False
sys.settrace(trace_func)

try:
    stop_flag = True  # 设置中断标志
    exec(code, gs)
    print("❌ 没有中断")
except KeyboardInterrupt as e:
    print(f"✅ 捕获到中断: {e}")
finally:
    sys.settrace(None)
    stop_flag = False

# 测试 4：测试死循环（没有函数调用）
print("\n4. 纯死循环（无函数调用的 trace 不会被触发）")
code = """
count = 0
for i in range(10000000):
    count += 1
print(count)
"""

gs = {}
sys.settrace(trace_func)
start = time.time()

try:
    exec(code, gs)
    elapsed = time.time() - start
    print(f"✅ 纯死循环没有被 trace 中断，耗时: {elapsed:.2f}s")
except Exception as e:
    print(f"❌ 异常: {e}")
finally:
    sys.settrace(None)

print("\n=== 测试完成 ===")
print("\n关键发现:")
print("- Trace 的 'call' 事件能有效拦截中断信号")
print("- 纯死循环（无函数调用）无法通过 trace 中断")
print("- 需要配合 Timer 或其他机制来处理纯死循环")
