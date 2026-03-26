import requests
import datetime
import time
import random
from chinese_calendar import is_holiday


# 配置
WEBHOOK_URL = 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=e317861a-d1ec-4ac4-af96-9d4b8f12d9d6'
HEADERS = {'Content-Type': 'application/json'}

REASON_LIST = [
    '恭喜您成为尊贵的梅赛德斯奔驰车主，愿三叉星辉照亮您的事业与前程。',
    '恭喜您成为尊贵的保时捷车主，愿黑马金盾守护您高贵的人生。',
    '恭喜您成为尊贵的奥迪车主，愿四环星辉照亮您的事业前程，愿世间美好从此与你环环相扣。',
    '恭喜您成为尊贵的宝马车主，愿浩瀚的蓝天白云，承载您的美好征程。',
    '恭喜您成为尊贵的红旗车主，愿红旗与您一起乘风破浪，蒸蒸日上，目光所致，皆是华夏，五星闪耀，皆是信仰。',
    '恭喜您成为尊贵的大众车主，愿VW星辉照耀您未来的事业前程，愿您以后踏遍大好河山，众拥天下。',
    '恭喜您成为尊贵的凯迪拉克车主，愿七彩圣盾保佑您的事业前程，所有的伟大都源于一次勇敢的开始，愿世间每一次泡澡都能拥有新的感悟。',
    '恭喜您成为尊贵的五菱宏光车主，愿红鹰展翅，照亮你加班的路程，愿更大的后备箱，能够帮你拉更多的货。'
]

PIC_URL = 'http://m.qpic.cn/psc?/V52hTYBe40XQKg3ty77Y0YPE4S2QKHbM/45NBuzDIW489QBoVep5mcQaIr2wdYcoru7B8IOrLeR*gjHWKrpX7LOWfaiWcuAUwnnq6krlUuO9y3GqBQ66w4ErgZebDqBgP21AmXFz0erE!/b&bo=OARUBgAAAAABJ24!&rf=viewer_4'


def is_holiday_today():
    """检查今天是否是节假日"""
    today = datetime.date.today()
    print(today)
    print(is_holiday(today))
    return is_holiday(today)


def dict_to_markdown(data):
    """字典转Markdown格式"""
    return '\n'.join([f'<font color="comment">{k}</font> : <font color="info">{v}</font>' for k, v in data.items()])


def send_news(url, title, description, picurl, link="http://iambanban.com/recharge/"):
    """发送图文消息"""
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
    return requests.post(url, headers=HEADERS, json=data)


def send_markdown(url, content):
    """发送Markdown消息"""
    return requests.post(url, headers=HEADERS, json={"msgtype": "markdown", "markdown": {"content": content}})


def send_at_all(url):
    """发送@所有人消息"""
    return requests.post(url, headers=HEADERS, json={"msgtype": "text", "text": {"mentioned_mobile_list": ["@all"]}})


def robot():
    """下午茶机器人"""
    if is_holiday_today():
        return False
    
    now = time.strftime('%H:%M')
    reason = {'【】': random.choice(REASON_LIST)}
    
    # 发送图文消息
    send_news(WEBHOOK_URL, now, '', PIC_URL)
    
    # 发送Markdown消息
    res = send_markdown(WEBHOOK_URL, dict_to_markdown(reason))
    
    # 发送@所有人
    if res.status_code == 200 and 'ok' in res.text:
        send_at_all(WEBHOOK_URL)
    return True


if __name__ == '__main__':
    robot()
