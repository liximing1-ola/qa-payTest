from time import time, strftime, localtime
import requests
from common import method


# 机器人配置
ROBOT_URLS = {
    'wechat': {},
    'slack': {}
}


def send_request(url, data, headers=None):
    """发送请求"""
    headers = headers or {'Content-Type': 'application/json'}
    try:
        res = requests.post(url=url, headers=headers, json=data)
        res.raise_for_status()
        return res
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None


def send_text(url, content, at_all=False):
    """发送文本消息"""
    data = {"msgtype": "text", "text": {"content": content}}
    res = send_request(url, data)
    if at_all and res and 'ok' in res.text:
        send_request(url, {"msgtype": "text", "text": {"mentioned_mobile_list": ["all"]}})
    return res


def send_markdown(url, content):
    """发送Markdown消息"""
    return send_request(url, {"msgtype": "markdown", "markdown": {"content": content}})


def send_news(url, title, description, picurl, link="https://www.12306.cn/index/"):
    """发送图文消息"""
    data = {
        "msgtype": "news",
        "news": {"articles": [{"title": title, "description": description, "url": link, "picurl": picurl}]}
    }
    res = send_request(url, data)
    if res and 'ok' in res.text:
        send_request(url, {"msgtype": "text", "text": {"mentioned_mobile_list": ["@all"]}})
    return res


def send_slack(url, title, reason, color='danger'):
    """发送Slack消息"""
    data = {
        "attachments": [{
            "fallback": "",
            "pretext": "",
            "color": color,
            "fields": [{"title": title, "value": reason, "short": 0}]
        }]
    }
    return send_request(url, data)


def robot(mode, reason, title='', bot='BB', color="good", to='wx'):
    """机器人入口"""
    url = ROBOT_URLS['slack' if to == 'slack' else 'wechat'].get(bot)
    if not url:
        print('robot over gg')
        return

    handlers = {
        'fail': lambda: send_text(url, f"警告! 失败用例: {title}, 失败原因: {reason}", at_all=True),
        'success': lambda: send_text(url, reason),
        'markdown': lambda: send_markdown(url, reason),
        'icon': lambda: send_news(url, f"{strftime('%m-%d %H:%M', localtime(time()))}, Execution is abnormal.Please check the status!", reason, method.get_image(mode=1)),
        'slack': lambda: send_slack(url, title, reason, color),
        'slack_pt': lambda: send_request(url, {"title": title, "value": reason}),
    }

    handler = handlers.get(mode)
    if handler:
        handler()
    else:
        print('robot over gg')


if __name__ == '__main__':
    robot('slack', reason='commit')
