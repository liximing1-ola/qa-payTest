import requests
import time
from common.method import getImage

def robot():
    url = 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=e317861a-d1ec-4ac4-af96-9d4b8f12d9d6'
    url1= 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=0179d8d1-2078-41ba-a8da-0fb11bd51880'
    headers = {'Content-Type': 'application/json'}
    now = time.strftime('%H:%M', time.localtime(time.time()))
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
                "picurl": icon, }
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


if __name__ == '__main__':
    robot()
