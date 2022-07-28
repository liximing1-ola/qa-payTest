import time
import requests
from common import method
def robot(mode, reason, title='', bot='BB'):
    headers = {'Content-Type': 'application/json'}
    robot_dict = {'BB': 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=f9d916cb-6b93-4389-8aa4-f51c755faa0e',
                  'test': 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=0179d8d1-2078-41ba-a8da-0fb11bd51880',
                  'PT': 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=b05a239e-3cc3-4faf-a3cc-c77e200ae1e6'}
    url = robot_dict[bot]
    url = robot_dict['test']  # 调试
    if mode == 'fail':
        content = "警告! 失败用例: {}, 失败原因: {}".format(title, reason)
        data = {
            "msgtype": "text",
            "text": {
                "content": content
            }
        }
        r = requests.post(url, headers=headers, json=data)
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
        now = time.strftime('%m-%d %H:%M', time.localtime(time.time()))
        title = "{}, Execution is abnormal.Please check the status!".format(now)
        des = reason
        icon = method.getImage(mode=1)
        data = {
            "msgtype": "news",
            "news": {
                "articles": [
                    {
                        "title": title,
                        "description": des,
                        "url": "https://www.12306.cn/index/",
                        "picurl": icon,
                    }
                ]
            }
        }
        r = requests.post(url, headers=headers, json=data)
        if r.status_code == 200 and r.text.find('ok'):
            data = {
                "msgtype": "text",
                "text": {
                    "mentioned_mobile_list": ["@all"]
                }
            }
            requests.post(url, headers=headers, json=data)
    else:
        print('robot over gg')


if __name__ == '__main__':
    robot('', '')
