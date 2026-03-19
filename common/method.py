import os
import random
import time
import requests
import Robot
from common import Consts
from common.conMysql import conMysql as mysql
from common.Config import config


def dictToListSlack(result_dict):
    """slack机器人使用"""
    case = []
    for k, v in result_dict.items():
        field = {
            "title": f"Scene:{k}",
            "value": f"执行结果:{v}",
            "short": False
        }
        case.append(field)
        # case.index(1)
    return case


# 将列表生成支持markdown的形式
def dictToList(result_dict):
    list_case = []
    for k, v in result_dict.items():
        # list_case.append('<font color="comment">{}-</font>,<font color=\"info\">{}</font>'.format(v, k))
        list_case.append('scene-{}：{}'.format(k, v))
    case = '\n'.join(list_case)
    # 注释生成md文件
    # path = config.BASE_PATH + '/markdown2Html/'
    # if not os.path.exists(path):
    #    os.mkdir(path)
    # with open(path + 'result.md', 'a', encoding='utf-8') as r:
    #    r.writelines(case)
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

    def getKey(json_data):  # 遍历json里面所有key
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
    # if res['body']['success'] is True:
    #   print('结果：{}, 时间：{}'.format(res['body']['success'], time.time()))
    #   Consts.success_num += 1
    # else:
    #   print('结果：{}， 时间：{}'.format(res['body'], time.time()))
    #     Consts.fail_num += 1
    current_time = time.time()
    if 'body' not in res:
        print(f'结果：缺少body字段，时间：{current_time}')
        Consts.fail_num += 1
        return
    body = res['body']
    if 'success' in body and body['success']:
        print(f'结果：{body["success"]}, 时间：{current_time}')
        Consts.success_num += 1
    else:
        print(f'结果：{body}，时间：{current_time}')
        Consts.fail_num += 1


def reason(des, res):
    # Safely get body with default empty dict to prevent KeyError
    body = res.get('body', {})
    # Check if success is 0 and 'msg' key doesn't exist in body (including nested)
    if body.get('success') == 0 and not isExtend(body, 'msg'):
        print(body)
    # Use f-string for more readable formatting
    return f'Depiction: {des},  failReason: {body}'


def reason_slp(des, res):
    if res['body'].get("success", None) is True and not isExtend(res['body'], 'msg'):
        print(res['body'])
    return 'Depiction: {},  failReason: {}'.format(des, res['body'])


def checkPath(path):
    if not os.path.exists(path):
        Robot.robot('icon', 'php代码路径异常: {}'.format(path), bot='PT')
        raise EnvironmentError('代码路径异常')


def getUserTitle(level):
    """
    UserNewTitleSrv::TITLE_QI_SHI => 1.0,
    UserNewTitleSrv::TITLE_NAN_JUE => 1.1,
    UserNewTitleSrv::TITLE_ZI_JUE => 1.2,
    UserNewTitleSrv::TITLE_BO_JUE => 1.3,
    UserNewTitleSrv::TITLE_HOU_JUE => 1.4,
    UserNewTitleSrv::TITLE_GONG_JUE => 1.5,
    UserNewTitleSrv::TITLE_QIN_KING => 1.6,
    UserNewTitleSrv::TITLE_GUO_KING => 1.8,
    UserNewTitleSrv::TITLE_HUANG_DI => 2.0,
    """
    level_map = {
        10: 1.0,
        20: 1.1,
        30: 1.2,
        40: 1.3,
        50: 1.4,
        60: 1.5,
        70: 1.6,
        80: 1.8,
        90: 2.0,
    }
    return level_map.get(level)


def checkUserVipExp(money_type='money', uid=config.payUid, pay_off=100):
    if money_type in {'money', 'coin'}:
        title = getUserTitle(mysql.selectUserInfoSql('level', uid))
        return int(pay_off * title) if title is not None else 0
    elif money_type == 'bean':
        return int(pay_off * 1.5)
    else:
        return ValueError
