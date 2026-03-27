# coding=utf-8
"""
机器人通知模块

提供多种消息通知方式（微信/Slack），支持文本、Markdown、图文等格式。
"""
from time import time, strftime, localtime
from typing import Optional, Dict, Any, Callable
import requests
from common import method


# 机器人配置
ROBOT_URLS: Dict[str, Dict[str, str]] = {
    'wechat': {},
    'slack': {}
}


def send_request(url: str, data: Dict[str, Any], 
                headers: Optional[Dict[str, str]] = None) -> Optional[requests.Response]:
    """发送 HTTP 请求
    
    Args:
        url: 请求 URL
        data: 请求数据
        headers: 请求头
        
    Returns:
        响应对象，失败返回 None
    """
    headers = headers or {'Content-Type': 'application/json'}
    try:
        res = requests.post(url=url, headers=headers, json=data)
        res.raise_for_status()
        return res
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None


def send_text(url: str, content: str, at_all: bool = False) -> Optional[requests.Response]:
    """发送文本消息
    
    Args:
        url: 机器人 URL
        content: 消息内容
        at_all: 是否@所有人
        
    Returns:
        响应对象
    """
    data = {"msgtype": "text", "text": {"content": content}}
    res = send_request(url, data)
    if at_all and res and 'ok' in res.text:
        send_request(url, {"msgtype": "text", "text": {"mentioned_mobile_list": ["all"]}})
    return res


def send_markdown(url: str, content: str) -> Optional[requests.Response]:
    """发送 Markdown 消息
    
    Args:
        url: 机器人 URL
        content: Markdown 内容
        
    Returns:
        响应对象
    """
    return send_request(url, {"msgtype": "markdown", "markdown": {"content": content}})


def send_news(url: str, title: str, description: str, picurl: str, 
             link: str = "https://www.12306.cn/index/") -> Optional[requests.Response]:
    """发送图文消息
    
    Args:
        url: 机器人 URL
        title: 标题
        description: 描述
        picurl: 图片 URL
        link: 链接地址
        
    Returns:
        响应对象
    """
    data = {
        "msgtype": "news",
        "news": {
            "articles": [{
                "title": title,
                "description": description,
                "url": link,
                "picurl": picurl
            }]
        }
    }
    res = send_request(url, data)
    if res and 'ok' in res.text:
        send_request(url, {"msgtype": "text", "text": {"mentioned_mobile_list": ["@all"]}})
    return res


def send_slack(url: str, title: str, reason: str, 
              color: str = 'danger') -> Optional[requests.Response]:
    """发送 Slack 消息
    
    Args:
        url: Slack Webhook URL
        title: 标题
        reason: 原因
        color: 颜色标记
        
    Returns:
        响应对象
    """
    data = {
        "attachments": [{
            "fallback": "",
            "pretext": "",
            "color": color,
            "fields": [{"title": title, "value": reason, "short": 0}]
        }]
    }
    return send_request(url, data)


def robot(mode: str, reason: str, title: str = '', bot: str = 'BB', 
         color: str = "good", to: str = 'wx') -> None:
    """机器人入口
    
    Args:
        mode: 消息模式（fail/success/markdown/icon/slack/slack_pt）
        reason: 消息内容
        title: 标题
        bot: 机器人标识（BB/PT/slp）
        color: 颜色标记
        to: 目标平台（wx/slack）
    """
    url = ROBOT_URLS['slack' if to == 'slack' else 'wechat'].get(bot)
    if not url:
        print('robot over gg')
        return

    # 消息处理器映射
    handlers: Dict[str, Callable] = {
        'fail': lambda: send_text(
            url, f"警告！失败用例：{title}, 失败原因：{reason}", at_all=True
        ),
        'success': lambda: send_text(url, reason),
        'markdown': lambda: send_markdown(url, reason),
        'icon': lambda: send_news(
            url, 
            f"{strftime('%m-%d %H:%M', localtime(time()))}, Execution is abnormal.Please check the status!", 
            reason, 
            method.get_image(mode=1)
        ),
        'slack': lambda: send_slack(url, title, reason, color),
        'slack_pt': lambda: send_request(url, {"title": title, "value": reason}),
    }

    handler: Optional[Callable] = handlers.get(mode)
    if handler:
        handler()
    else:
        print('robot over gg')


if __name__ == '__main__':
    robot('slack', reason='commit')