import time
import requests
import random

def robot_fail(title, reason):
    #url = 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=0179d8d1-2078-41ba-a8da-0fb11bd51880'
    url = 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=f9d916cb-6b93-4389-8aa4-f51c755faa0e'
    headers = {'Content-Type': 'application/json'}
    content = "警告!-失败用例: {}, 失败原因: {}".format(title, reason)
    data = {
        "msgtype": "text",
        "text": {
            "content": content
        }
    }
    r = requests.post(
        url,
        headers=headers, json=data)
    if r.status_code == 200 and r.text.find('ok'):
        data = {
            "msgtype": "text",
            "text": {
                "mentioned_mobile_list": [""]
            }
        }
        requests.post(url, headers=headers, json=data)

def robot_success(content):
    #url = 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=0179d8d1-2078-41ba-a8da-0fb11bd51880'
    url = 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=f9d916cb-6b93-4389-8aa4-f51c755faa0e'
    headers = {'Content-Type': 'application/json'}
    data = {
        "msgtype": "text",
        "text": {
                "content": content
        }
    }
    requests.post(url, headers=headers, json=data)

def robot_markdown(content):
    #url = 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=0179d8d1-2078-41ba-a8da-0fb11bd51880'
    url = 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=f9d916cb-6b93-4389-8aa4-f51c755faa0e'
    headers = {'Content-Type': 'application/json'}
    data = {
        "msgtype": "markdown",
        "markdown": {
                "content": content
        }
    }
    requests.post(url, headers=headers, json=data)

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

def dictToList(case_dict):
    list_case = []
    for k, v in case_dict.items():
        list_case.append('用例说明: {},  结果: <font color=\"info\">{}</font>'.format(k, v))
    case = '\n'.join(list_case)
    print(case)
    return case


if __name__ == '__main__':
    con={'验证余额不足时，私聊一对一打赏': 'pass', '验证余额足够时，私聊一对一打赏': 'pass', '验证开通个人守护的收益分成': 'pass',
         '验证余额不足时，房间一对一打赏': 'pass', '验证余额足够时，直播类型房间一对一打赏': 'pass', '验证余额足够时，非直播类型房间一对一打赏': 'pass',
         '验证商城购买单个道具时逻辑': 'pass', '验证商城购买多个道具时逻辑': 'pass', '验证商城购买的道具在房间内赠送给其他人逻辑': 'pass',
         '验证商城购买的道具在房间内赠送给他人不足的逻辑': 'pass', '验证爵位开通及返钱到余额': 'pass', '验证爵位续费及返钱到余额': 'pass'}
    robot_markdown(dictToList(con))