import time
import requests
from Common.Api import getImage

def robot(mode, reason, title=''):
    headers = {'Content-Type': 'application/json'}
    robot_dict = {'normal': 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=f9d916cb-6b93-4389-8aa4-f51c755faa0e',
                  'test': 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=0179d8d1-2078-41ba-a8da-0fb11bd51880'}
    url = robot_dict['test']
    if mode == 'fail':
        content = "警告! 失败用例: {}, 失败原因: {}".format(title, reason)
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
                        "url": "",
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


if __name__ == '__main__':
    pass
