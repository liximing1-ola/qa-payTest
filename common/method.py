import os
import random
import time
import requests
import Robot
from common import Consts
from common.conMysql import conMysql as mysql
from common.Config import config


# ============ 字典转换 ============
def dict_to_slack_fields(result_dict):
    """将字典转换为Slack fields格式"""
    return [
        {"title": f"Scene:{k}", "value": f"执行结果:{v}", "short": False}
        for k, v in result_dict.items()
    ]


def dict_to_markdown(result_dict):
    """将字典转换为Markdown格式"""
    return '\n'.join([f'scene-{k}：{v}' for k, v in result_dict.items()])


# ============ 图片获取 ============
IMAGE_APIS = {
    1: 'https://www.mxnzp.com/api/image/girl/list/random?app_id=kilmc0p2ytsnawyp&app_secret=bnNoWElSVDBYbEhsc1EvYVM2WnVnZz09',
    2: 'https://shibe.online/api/shibes?count=1'
}


def get_image(mode=2):
    """随机获取图片"""
    url = IMAGE_APIS.get(mode)
    if not url:
        return None

    res = requests.get(url)
    res.raise_for_status()
    data = res.json()

    if mode == 1 and data.get('code') == 1:
        return data['data'][0]['imageUrl']
    elif mode == 2:
        return data[0]
    return None


# ============ JSON工具 ============
def is_extend(data, tag):
    """检查字段是否在JSON中存在"""
    if not isinstance(data, dict):
        print('please input a json!')
        return False
    return tag in _get_all_keys(data)


def _get_all_keys(data):
    """递归获取JSON中所有key"""
    keys = []

    def _extract(obj):
        if isinstance(obj, dict):
            for k, v in obj.items():
                keys.append(k)
                _extract(v)
        elif isinstance(obj, list):
            for item in obj:
                _extract(item)

    _extract(data)
    return keys


# ============ 结果处理 ============
def get_value(res):
    """处理响应结果，统计成功/失败"""
    current_time = time.time()

    if 'body' not in res:
        print(f'结果：缺少body字段，时间：{current_time}')
        Consts.fail_num += 1
        return

    body = res['body']
    if body.get('success'):
        print(f'结果：{body["success"]}, 时间：{current_time}')
        Consts.success_num += 1
    else:
        print(f'结果：{body}，时间：{current_time}')
        Consts.fail_num += 1


def format_reason(des, res):
    """格式化失败原因"""
    body = res.get('body', {})
    if body.get('success') == 0 and not is_extend(body, 'msg'):
        print(body)
    return f'Depiction: {des}, failReason: {body}'


def format_reason_slp(des, res):
    """格式化SLP失败原因"""
    body = res.get('body', {})
    if body.get('success') is True and not is_extend(body, 'msg'):
        print(body)
    return f'Depiction: {des}, failReason: {body}'


# ============ 路径检查 ============
def check_path(path):
    """检查路径是否存在"""
    if not os.path.exists(path):
        Robot.robot('icon', f'php代码路径异常: {path}', bot='APP')
        raise EnvironmentError('代码路径异常')


# ============ 爵位等级 ============
TITLE_LEVEL_MAP = {
    10: 1.0,   # 骑士
    20: 1.1,   # 男爵
    30: 1.2,   # 子爵
    40: 1.3,   # 伯爵
    50: 1.4,   # 侯爵
    60: 1.5,   # 公爵
    70: 1.6,   # 亲王
    80: 1.8,   # 国王
    90: 2.0,   # 皇帝
}


def get_user_title(level):
    """根据等级获取爵位系数"""
    return TITLE_LEVEL_MAP.get(level)


def calculate_vip_exp(money_type='money', uid=config.payUid, pay_off=100):
    """计算VIP经验值"""
    if money_type in {'money', 'coin'}:
        title = get_user_title(mysql.selectUserInfoSql('level', uid))
        return int(pay_off * title) if title else 0
    elif money_type == 'bean':
        return int(pay_off * 1.5)
    else:
        raise ValueError(f'Unsupported money_type: {money_type}')
