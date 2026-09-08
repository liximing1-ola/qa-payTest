"""
全局变量
"""
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
