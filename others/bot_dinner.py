# coding=utf-8
"""
点餐提醒机器人

定时发送点餐通知，支持节假日自动跳过。
"""
import datetime
import time
import requests
from chinese_calendar import is_holiday
from common.method import get_image


# 配置
WEBHOOK_URL: str = 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=e317861a-d1ec-4ac4-af96-9d4b8f12d9d6'


def is_holiday_today() -> bool:
    """检查今天是否是节假日"""
    today = datetime.date.today()
    return is_holiday(today)


def send_news(url: str, title: str, description: str, 
              picurl: str, link: str = "http://iambanban.com/recharge/") -> requests.Response:
    """发送图文消息
    
    Args:
        url: Webhook URL
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
    return requests.post(url, headers={'Content-Type': 'application/json'}, json=data)


def send_at_all(url: str) -> requests.Response:
    """发送@所有人消息
    
    Args:
        url: Webhook URL
        
    Returns:
        响应对象
    """
    data = {"msgtype": "text", "text": {"mentioned_mobile_list": ["@all"]}}
    return requests.post(url, headers={'Content-Type': 'application/json'}, json=data)


def robot() -> bool:
    """点餐机器人主入口
    
    Returns:
        执行是否成功
    """
    if is_holiday_today():
        return False
    
    now = time.strftime('%H:%M')
    title = f"{now}-点餐时间到，上微信【丰食】预约晚餐"
    description = '点餐截止到下午17:00，供餐时间19:30'
    
    res = send_news(WEBHOOK_URL, title, description, get_image(mode=2))
    if res.status_code == 200 and 'ok' in res.text:
        send_at_all(WEBHOOK_URL)
    return True


if __name__ == '__main__':
    robot()