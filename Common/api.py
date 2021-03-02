# 内网打印调试
def errorMsg(res):
    if res['body']['success'] != 1:
        print(res['body'])
    else:
        print(res)

def dictToList(dict):
    for k, v in dict.items():
        return k, v