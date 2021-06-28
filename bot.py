import requests
import time
import random

def robot(mode):
    url1 = 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=e317861a-d1ec-4ac4-af96-9d4b8f12d9d6'
    url= 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=0179d8d1-2078-41ba-a8da-0fb11bd51880'
    headers = {'Content-Type': 'application/json'}
    now = time.strftime('%H:%M', time.localtime(time.time()))
    reason =' '
    if mode == 'food':
        title = "MVB:当前时间-{},上美食APP/点击图片跳转WEB页面【预约晚餐】".format(now)
        des = '点餐截止到下午17:30，供餐时间19:30-20:00'
        icon = getImage()
        data = {
            "msgtype": "news",
            "news": {
                "articles": [{
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
    elif mode == 'markdown':
        data = {
            "msgtype": "markdown",
            "markdown": {
                "content": reason
            }
        }
        requests.post(url, headers=headers, json=data)



def getImage():
    url = 'https://www.mxnzp.com/api/image/girl/list/random?app_id=kilmc0p2ytsnawyp&app_secret=bnNoWElSVDBYbEhsc1EvYVM2WnVnZz09'
    res = requests.get(url)
    res.raise_for_status()
    res = res.json()
    if res['code'] == 1:
        return res['data'][0]['imageUrl']
    else:
        icon = random.randint(1, 140)
        return 'http://xs-image.oss-cn-hangzhou.aliyuncs.com/static/gift_big/{}.png'.format(icon)


if __name__ == '__main__':
    robot()
