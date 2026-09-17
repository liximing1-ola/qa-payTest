"""
全局变量
"""
import threading

case_list = {}
case_list_b = {}
case_list_c = {}
# 失败结果列表
fail_case_reason = []
# pass
result = '✅'
# 记录时间
startTime = 0
endTime = 0
# 并发结果
success_num = 0
fail_num = 0

# 并发计数器保护锁（gevent 协作式调度下暂安全，面向 threading 预留）
_counter_lock = threading.Lock()


def increment_success():
    """线程安全地递增成功计数"""
    with _counter_lock:
        global success_num
        success_num += 1


def increment_fail():
    """线程安全地递增失败计数"""
    with _counter_lock:
        global fail_num
        fail_num += 1


def reset():
    """重置所有全局可变状态"""
    global success_num, fail_num, startTime, endTime, result
    case_list.clear()
    case_list_b.clear()
    case_list_c.clear()
    fail_case_reason.clear()
    result = '✅'
    startTime = 0
    endTime = 0
    success_num = 0
    fail_num = 0
