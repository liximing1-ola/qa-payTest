import time

import requests

from common import method


def robot_slack(mode, reason, title='', bot='BB'):
    headers = {'Content-Type': 'application/json'}
    robot_dict = {'BB': '',
                  'test': '',
                  'PT': '',
                  'starify': 'https://hooks.slack.com/services/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',  # todo 机器人key
                  }
    url = robot_dict[bot]
    # url = robot_dict['test']
    # 调试
    if mode == 'fail':
        content = "警告! 失败用例: {}, 失败原因: {}".format(title, reason)
        data = {
            "username": "支付回归",
            "icon_emoji": ":lady_beetle:",
            "text": content,
        }
        r = requests.post(url, headers=headers, json=data)
        # todo @all slack没这个功能
        # if r.status_code == 200 and r.text.find('ok'):
        #     data = {
        #         "msgtype": "text",
        #         "text": {
        #             "mentioned_mobile_list": ["all"]
        #         }
        #     }
        #     requests.post(url, headers=headers, json=data)

    elif mode == 'success':
        data = {
            "username": "支付回归",
            "icon_emoji": ":lady_beetle:",
            "text": reason,
        }
        requests.post(url, headers=headers, json=data)

    elif mode == 'attachments':
        data = {
            "username": "支付回归",
            "icon_emoji": ":lady_beetle:",
            "attachments": [
                {
                    "fallback": f"运行于:{time.strftime('%m-%d %H:%M', time.localtime(time.time()))}",
                    "pretext": f"运行于:{time.strftime('%m-%d %H:%M', time.localtime(time.time()))}",
                    "color": "#11d000",
                    "fields": reason
                }
            ]
        }
        requests.post(url, headers=headers, json=data)

    # elif mode == 'icon':
    #     now = time.strftime('%m-%d %H:%M', time.localtime(time.time()))
    #     title = "{}, Execution is abnormal.Please check the status!".format(now)
    #     des = reason
    #     icon = method.getImage(mode=1)
    #     data = {
    #         "msgtype": "news",
    #         "news": {
    #             "articles": [
    #                 {
    #                     "title": title,
    #                     "description": des,
    #                     "url": "https://www.12306.cn/index/",
    #                     "picurl": icon,
    #                 }
    #             ]
    #         }
    #     }
    #     r = requests.post(url, headers=headers, json=data)
    #     if r.status_code == 200 and r.text.find('ok'):
    #         data = {
    #             "msgtype": "text",
    #             "text": {
    #                 "mentioned_mobile_list": ["@all"]
    #             }
    #         }
    #         requests.post(url, headers=headers, json=data)
    else:
        print('robot over gg')
