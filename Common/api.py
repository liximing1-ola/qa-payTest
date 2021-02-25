

def errorMsg(res):
    if res['body']['success'] != 1:
        print(res)