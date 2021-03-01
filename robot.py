import time
import requests
import random

def robot_fail(des):
    url = 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=f9d916cb-6b93-4389-8aa4-f51c755faa0e'
    headers = {'Content-Type': 'application/json'}
    now = time.strftime('%F:%H:%M', time.localtime(time.time()))
    title = "警告!-{}".format(now)
    des = des
    icon = getImage()
    data = {
        "msgtype": "news",
        "news": {
            "articles": [
                {
                    "title": title,
                    "description": des,
                    "url": "http://114.55.7.123:3000/ees/banban/commits/alpha-for-vpc",
                    "picurl": icon,
                }
            ]
        }
    }
    r = requests.post(
        url,
        headers=headers, json=data)
    if r.status_code == 200 and r.text.find('ok'):
        data = {
            "msgtype": "text",
            "text": {
                "mentioned_mobile_list": ["@all"]
            }
        }
        requests.post(url, headers=headers, json=data)

def robot_success(content):
    url = 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=f9d916cb-6b93-4389-8aa4-f51c755faa0e'
    headers = {'Content-Type': 'application/json'}
    now = time.strftime('%F:%H:%M', time.localtime(time.time()))
    #content = '{}'.format()
    data = {
        "msgtype": "text",
        "text": {
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


if __name__ == '__main__':
    robot_success('执行用例总数: 14, 失败用例总数: 0, 异常用例总数: 1')