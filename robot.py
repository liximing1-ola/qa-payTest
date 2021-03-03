import time
import requests
import random

def robot(mode, reason, title=''):
    headers = {'Content-Type': 'application/json'}
    robot_dict = {'normal': 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=f9d916cb-6b93-4389-8aa4-f51c755faa0e',
                  'test': 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=0179d8d1-2078-41ba-a8da-0fb11bd51880'}
    url = robot_dict['normal']
    if mode == 'fail':
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
                    "mentioned_mobile_list": ["all"]
                }
            }
            requests.post(url, headers=headers, json=data)
    elif mode == 'success':
        data = {
            "msgtype": "text",
            "text": {
                "content": reason
            }
        }
        requests.post(url, headers=headers, json=data)

    elif mode == 'markdown':
        data = {
            "msgtype": "markdown",
            "markdown": {
                "content": reason
            }
        }
        requests.post(url, headers=headers, json=data)

    elif mode == 'icon':
        now = time.strftime('%H:%M', time.localtime(time.time()))
        title = "{}".format(now)
        des = ' '
        icon = getImage()
        data = {
            "msgtype": "news",
            "news": {
                "articles": [
                    {
                        "title": title,
                        "description": des,
                        "url": "https://meican.com/",
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

    else:
        print('robot over')

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
    pass
