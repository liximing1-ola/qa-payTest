# 内网打印调试
import requests
import json
import random

def errorMsg(res):
    if res['body']['success'] != 1:
        print(res['body'])
    else:
        print(res)

def dictToList(result_dict):
    list_case = []
    for k, v in result_dict.items():
        list_case.append('checkPoint:  {},  结果: <font color=\"info\">{}</font>'.format(k, v))
    case = '\n'.join(list_case)
    return case

def getImage():
    url = 'https://www.mxnzp.com/api/image/girl/list/random?app_id=kilmc0p2ytsnawyp&' \
          'app_secret=bnNoWElSVDBYbEhsc1EvYVM2WnVnZz09'
    res = requests.get(url)
    res.raise_for_status()
    res = res.json()
    if res['code'] == 1:
        return res['data'][0]['imageUrl']
    else:
        icon = random.randint(1, 140)
        return 'http://xs-image.oss-cn-hangzhou.aliyuncs.com/static/gift_big/{}.png'.format(icon)


if __name__ == '__main__':
    case_dict = {'验证余额不足时，私聊一对一打赏': 'pass', '验证余额足够时，私聊一对一打赏': 'pass', '验证开通个人守护的收益分成': 'pass',
                 '验证余额不足时，房间一对一打赏': 'pass', '验证余额足够时，直播类型房间一对一打赏': 'pass', '验证余额足够时，非直播类型房间一对一打赏': 'pass',
                 '验证商城购买单个道具时逻辑': 'pass', '验证商城购买多个道具时逻辑': 'pass', '验证商城购买的道具在房间内赠送给其他人逻辑': 'pass',
                 '验证商城购买的道具在房间内赠送给他人不足的逻辑': 'pass', '验证爵位开通及返钱到余额': 'pass', '验证爵位续费及返钱到余额': 'pass'}

    print(dictToList(case_dict))