# coding=utf-8
"""
点餐提醒机器人

定时发送点餐通知，支持节假日自动跳过。
"""
from typing import Optional
import datetime
import time
import requests
from chinese_calendar import is_holiday


# 配置
WEBHOOK_URL: str = 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=e317861a-d1ec-4ac4-af96-9d4b8f12d9d6'
IMAGE_APIS: dict = {
    1: 'https://www.mxnzp.com/api/image/girl/list/random?app_id=kilmc0p2ytsnawyp&app_secret=bnNoWElSVDBYbEhsc1EvYVM2WnVnZz09',
    2: 'https://shibe.online/api/shibes?count=1'
}


def is_holiday_today() -> bool:
    """检查今天是否是节假日
    
    Returns:
        是否为节假日
    """
    today = datetime.date.today()
    print(today)
    print(is_holiday(today))
    return is_holiday(today)


def get_image(mode: int = 2) -> Optional[str]:
    """随机获取图片
    
    Args:
        mode: 图片模式（1=女生，2=狗狗）
        
    Returns:
        图片 URL，失败返回 None
    """
    url = IMAGE_APIS.get(mode)
    if not url:
        return None
    
    try:
        res = requests.get(url)
        res.raise_for_status()
        data = res.json()
        
        if mode == 1 and data.get('code') == 1:
            return data['data'][0]['imageUrl']
        elif mode == 2:
            return data[0]
    except Exception as e:
        print(f'get_image error: {e}')
    
    return None


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