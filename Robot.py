# coding=utf-8
"""
机器人通知模块
提供多种消息通知方式（微信/Slack），支持文本、Markdown、图文等格式。
"""
import logging
from time import time, strftime, localtime
from typing import Optional, Dict, Any
import requests
from common import method

logger = logging.getLogger(__name__)

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
        logger.error("Request failed: %s", e)
        return None


def _send_at_all(url: str, res: Optional[requests.Response]) -> None:
    """检查响应成功后发送 @所有人 消息"""
    if res and 'ok' in res.text:
        send_request(url, {"msgtype": "text", "text": {"mentioned_mobile_list": ["all"]}})


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
    if at_all:
        _send_at_all(url, res)
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
    _send_at_all(url, res)
    return res


def send_slack(url: str, title: str, reason: str, 
              color: str = 'danger') -> Optional[requests.Response]:
    """发送 Slack 消息
    Args:
        url: Slack Webhook URL
        title: title
        reason: 原因
        color: 颜色标记
        
    Returns:
        响应对象
    """
    data = {
        "attachments": [{
            "color": color,
            "fields": [{"title": title, "value": reason, "short": 0}]
        }]
    }
    return send_request(url, data)


def robot(mode: str, reason: str, title: str = '', bot: str = 'BB', 
         color: str = "good", to: str = 'wx') -> None:
    """机器人入口
    Args:
        mode: 消息模式（fail/success/markdown/icon/slack/slack_oversea）
        reason: 消息内容
        title: 标题
        bot: 机器人标识（BB/oversea/slp）
        color: 颜色标记
        to: 目标平台（wx/slack）
    """
    url = ROBOT_URLS['slack' if to == 'slack' else 'wechat'].get(bot)
    if not url:
        logger.warning('未配置机器人 URL，跳过通知：platform=%s, bot=%s', to, bot)
        return

    if mode == 'fail':
        send_text(url, f"警告！！！失败用例：{title}, 失败原因：{reason}", at_all=True)
    elif mode == 'success':
        send_text(url, reason)
    elif mode == 'markdown':
        send_markdown(url, reason)
    elif mode == 'icon':
        send_news(url, f"{strftime('%m-%d %H:%M', localtime(time()))}, Execution is abnormal. Please check the status!",
                  reason, method.get_image(mode=1))
    elif mode == 'slack':
        send_slack(url, title, reason, color)
    elif mode == 'slack_oversea':
        send_request(url, {"title": title, "value": reason})
    else:
        logger.warning('不支持的消息模式，跳过通知：mode=%s', mode)


if __name__ == '__main__':
    robot('slack', reason='commit')