# 内网打印调试
def errorMsg(res):
    if res['body']['success'] != 1:
        print(res['body'])
    else:
        print(res)

def dictToList(case_dict):
    list_case = []
    for k, v in case_dict.items():
        list_case.append('Case:{}, 结果:{}'.format(k, v) + '\n')
    return list_case
