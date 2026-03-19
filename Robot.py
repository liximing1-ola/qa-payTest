from time import time, strftime, localtime
import requests
from common import method


def robot(mode, reason, title='', bot='BB', color="good", to='wx'):
    headers = {'Content-Type': 'application/json'}
    #  wx
    robot_dict_wechat = {
    }
    #  slack
    robot_dict = {
    }

    # Simplified URL selection
    url = robot_dict[bot] if to == 'slack' else robot_dict_wechat[bot]

    # Mode handler mapping - replaces long elif chain
    mode_handlers = {
        'fail': lambda: mode_fail(url, headers, title, reason),
        'success': lambda: mode_success(url, headers, reason),
        'markdown': lambda: mode_markdown(url, headers, reason),
        'icon': lambda: mode_icon(url, headers, reason),
        'slack': lambda: mode_slack(url, headers, title, reason, color),
        'slack_pt': lambda: mode_slack_pt(url, headers, title, reason),
    }

    # Execute handler if mode exists
    handler = mode_handlers.get(mode)
    if handler:
        handler()
    else:
        print('robot over gg')


def send_request(url, data, headers):
    try:
        res = requests.post(url=url, headers=headers, json=data)
        res.raise_for_status()
        return res
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None


def mode_fail(url, headers, title, reason):
    content = "警告! 失败用例: {}, 失败原因: {}".format(title, reason)
    data = {
        "msgtype": "text",
        "text": {"content": content}
    }
    res = send_request(url, headers=headers, data=data)
    if res and 'ok' in res.text:
        data = {
            "msgtype": "text",
            "text": {"mentioned_mobile_list": ["all"]}
        }
        send_request(url, headers=headers, data=data)


def mode_success(url, headers, reason):
    data = {
        "msgtype": "text",
        "text": {"content": reason}
    }
    send_request(url, headers=headers, data=data)


def mode_markdown(url, headers, reason):
    data = {
        "msgtype": "markdown",
        "markdown": {
            "content": reason
        }
    }
    requests.post(url, headers=headers, json=data)


def mode_icon(url, headers, reason):
    now = strftime('%m-%d %H:%M', localtime(time()))
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
    res = send_request(url, headers=headers, data=data)
    if res and 'ok' in res.text:
        data = {
            "msgtype": "text",
            "text": {
                "mentioned_mobile_list": ["@all"]
            }
        }
        send_request(url, headers=headers, data=data)


def mode_slack(url, headers, reason, title, color='danger'):
    data = {
        "attachments": [
            {
                "fallback": "",
                "pretext": "",
                "color": color,
                "fields": [
                    {
                        "title": title,
                        "value": reason,
                        "short": 0
                    }
                ]
            }
        ]
    }
    send_request(url, headers=headers, data=data)


def mode_slack_pt(url, headers, reason, title):
    data = {
        "title": title,
        "value": reason,
    }
    send_request(url, headers=headers, data=data)


if __name__ == '__main__':
    robot('slack', reason='commit')
