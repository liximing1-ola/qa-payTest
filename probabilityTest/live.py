# coding=utf-8
import time
import urllib.parse

import requests


# 个人房幸运蛋概率测试
def postPayCreate():
    url = "http://192.168.11.46/rooms/broadcastercontent/giveStar?package=com.imbb.banban.android"
    headers = {
        'Content-Type': "application/x-www-form-urlencoded",
        'cache-control': "no-cache",
        'Postman-Token': "f7d705b2-cf29-4a4a-81ba-2c8c8d0f5ed5",
        "user-token": 'd3ccnXDBWkTkXLbr8PuGJegJdEPc6x9Sc__2BW32yxxuOWuNEfsEaHU1o4oKXtPNH9tylxUBv4Tt855126jdSUuZQ0eLMp__2BVLyltuTqHGSas20dOBF6__2FxPn7hc6'}
    data = {
        "program_id": 2,
    }
    d = urllib.parse.urlencode(data)
    data = d.replace('+', '').replace('%27', '%22')
    res = requests.post(url, data=data, headers=headers)
    res = res.json()
    if res['success'] == 1:
        pass
    else:
        raise EnvironmentError(res)

def main():
    i = 1
    while i < 10000:
        print('第{}次'.format(i))
        postPayCreate()
        time.sleep(0.1)
        i += 1


if __name__=='__main__':
    main()