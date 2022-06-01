import requests
import datetime
import time
import random
from chinese_calendar import is_holiday

def getHoliday():
    now_year = int(time.strftime('%Y', time.localtime(time.time())))
    now_month = int(time.strftime('%m', time.localtime(time.time())))
    now_day = int(time.strftime('%d', time.localtime(time.time())))
    holiday = datetime.date(now_year, now_month, now_day)
    print(holiday)
    print(is_holiday(holiday))
    return is_holiday(holiday)

def robot():
    url = 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=e317861a-d1ec-4ac4-af96-9d4b8f12d9d6'
    # url1= 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=0179d8d1-2078-41ba-a8da-0fb11bd51880'
    headers = {'Content-Type': 'application/json'}
    now = time.strftime('%H:%M', time.localtime(time.time()))
    title = "{}-点餐时间到,上微信【丰食】预约晚餐".format(now)
    des = '点餐截止到下午17:00，供餐时间19:30'
    icon = getImage(mode=2)
    data = {
        "msgtype": "news",
        "news": {
            "articles": [{
                "title": title,
                "description": des,
                "url": "http://iambanban.com/recharge/",
                "picurl": icon, }
            ]
        }
    }
    if getHoliday():
        return False
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
        icon = random.randint(1, 600)
        return 'http://xs-image.oss-cn-hangzhou.aliyuncs.com/static/gift_big/{}.png'.format(icon)


if __name__ == '__main__':
    robot()
