# coding=utf-8
import requests
import urllib.parse
import time
# PK房
def postPayCreate():
    url = "https://dev.iambanban.com/pay/create?package=com.imbb.banban.android"
    headers = {
        'Content-Type': "application/x-www-form-urlencoded",
        'cache-control': "no-cache",
        'Postman-Token': "f7d705b2-cf29-4a4a-81ba-2c8c8d0f5ed5",
        "user-token": '9ac0G5NSwy3X1u__2BVZ3xRaQjj3xvPWpSR__2Ba1wRYf67VkpGeLLmtqtZ8Ypd6mFRI2csntc5jS7XZovP__2F6gq__2BcuZIM__2BPVs__2B12HCGU1O3am375FRUr4fX__2BZ4OWIA'}
    data = {
        "platform": "available",
        "type": "package",
        "money": 80,
        "params":
            {"rid": 193185405,
             "uids": "100010055,100010056,100010059,100010060,100010057,100010058,100010061,100010068",
             "positions": "1,2,3,4,5,6,7,8",
             "position": 0,
             "giftId": 545,
             "giftNum": 1,
             "price": 10,
             "cid": 0,
             "ctype": "",
             "duction_money": 0,
             "version": 2,
             "num": 8,
             "gift_type": 'normal',
             "useCoin": -1,
             "star": 0,
             "show_pac_man_guide": 1,
             "refer": "",
             "all_mic": 0,
             }
    }
    d = urllib.parse.urlencode(data)
    data = d.replace('+', '').replace('%27', '%22')
    res = requests.post(url, data=data, headers=headers)
    print(res.text)
    res = res.json()
    if res['success'] == 1:
        pass
    else:
        raise EnvironmentError('error')

def postPayCreate_ktv():
    url = "https://dev.iambanban.com/pay/create?package=com.imbb.banban.android"
    headers = {
        'Content-Type': "application/x-www-form-urlencoded",
        'cache-control': "no-cache",
        'Postman-Token': "f7d705b2-cf29-4a4a-81ba-2c8c8d0f5ed5",
        "user-token": '9ac0G5NSwy3X1u__2BVZ3xRaQjj3xvPWpSR__2Ba1wRYf67VkpGeLLmtqtZ8Ypd6mFRI2csntc5jS7XZovP__2F6gq__2BcuZIM__2BPVs__2B12HCGU1O3am375FRUr4fX__2BZ4OWIA'}
    data = {
        "platform": "available",
        "type": "package",
        "money": 80,
        "params":
            {"rid": 193185405,
             "uids": "100010055,100010056,100010059,100010060,100010057,100010058,100010061,100010068",
             "positions": "1,2,3,4,5,6,7,8",
             "position": 0,
             "giftId": 545,
             "giftNum": 1,
             "price": 10,
             "cid": 0,
             "ctype": "",
             "duction_money": 0,
             "version": 2,
             "num": 8,
             "gift_type": 'normal',
             "useCoin": -1,
             "star": 0,
             "show_pac_man_guide": 1,
             "refer": "",
             "all_mic": 0,
             }
    }
    d = urllib.parse.urlencode(data)
    data = d.replace('+', '').replace('%27', '%22')
    res = requests.post(url, data=data, headers=headers)
    print(res.text)
    res = res.json()
    if res['success'] == 1:
        pass
    else:
        raise EnvironmentError('error')


def main():
    num = 1
    while num < 10000:
        num += 1
        postPayCreate()
        time.sleep(1)
        print(num)


if __name__=='__main__':
    main()