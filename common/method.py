import requests
import random
import time
import os
from common import Consts

# 将列表生成支持markdown的形式
def dictToList(result_dict):
    list_case = []
    for k, v in result_dict.items():
        list_case.append(
            'Scene: <font color="comment">{}</font>,  结果: <font color=\"info\">{}</font>'.format(k, v))
    case = '\n'.join(list_case)
    return case

# 随机获取图片
def getImage(mode=2):
    url = 'https://www.mxnzp.com/api/image/girl/list/random?app_id=kilmc0p2ytsnawyp&app_secret=bnNoWElSVDBYbEhsc1EvYVM2WnVnZz09'
    url_dog = 'https://shibe.online/api/shibes?count=1'
    if mode == 1:
        res = requests.get(url)
        res.raise_for_status()
        res = res.json()
        if res['code'] == 1:
            return res['data'][0]['imageUrl']
    elif mode == 2:
        res = requests.get(url_dog)
        res = res.json()
        return res[0]
    elif mode == 3:
        icon = random.randint(1, 200)
        return 'http://xs-image.oss-cn-hangzhou.aliyuncs.com/static/gift_big/{}.png'.format(icon)

# 检查当前字段是否在Json中存在
def isExtend(data, tag):
    if type(data) != type({}):
        print('please input a json!')
    else:
        key_list = getKeys(data)
        for key in key_list:
            if key == tag:
                return True
    return False

def getKeys(data):
    keysAll_list = []

    def getKey(json_data):  # 遍历json所有key
        if type(json_data) == type({}):
            keys = json_data.keys()
            for key in keys:
                value = json_data.get(key)
                if type(value) != type({}) and type(value) != type([]):
                    keysAll_list.append(key)
                elif type(value) == type({}):
                    keysAll_list.append(key)
                    getKey(value)
                elif type(value) == type([]):
                    keysAll_list.append(key)
                    for para in value:
                        if type(para) == type({}) or type(para) == type([]):
                            getKey(para)
                        else:
                            keysAll_list.append(para)

    getKey(data)
    return keysAll_list

def getValue(res):
    if res['body']['success'] is True:
        print('结果：{}, 时间：{}'.format(res['body']['success'], time.time()))
        Consts.success_num += 1
    else:
        print('结果：{}， 时间：{}'.format(res['body'], time.time()))
        Consts.fail_num += 1

def reason(des, res):
    if res['body']['success'] == 0 and not isExtend(res['body'], 'msg'):
        print(res['body'])
    return 'Depiction: {},  failReason: {}'.format(des, res['body'])

def checkPath(path):
    if not os.path.exists(path):
        print(1)
        raise EnvironmentError('代码路径异常')