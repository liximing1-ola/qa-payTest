import requests
import datetime
import time
import random
from chinese_calendar import is_holiday


def getHoliday():
    now_year = int(time.strftime('%Y', time.localtime(time.time())))
    now_month = int(time.strftime('%m', time.localtime(time.time())))
    now_day = int(time.strftime('%d', time.localtime(time.time())))
    holiday = datetime.date(now_year, now_month, now_day)
    print(holiday)
    print(is_holiday(holiday))
    return is_holiday(holiday)


def robot():
    url = 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=e317861a-d1ec-4ac4-af96-9d4b8f12d9d6'
    # url= 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=ddf98ffd-fd35-42be-8362-5e485b08226a'  # 测试用
    headers = {'Content-Type': 'application/json'}
    reason = {'【】': '{}'.format(random.choice(reason_list))}
    now = time.strftime('%H:%M', time.localtime(time.time()))
    title = "".format(now)
    des = ''
    data = {
        "msgtype": "news",
        "news": {
            "articles": [{
                "title": title,
                "description": des,
                "url": "http://iambanban.com/recharge/",
                "picurl": 'http://m.qpic.cn/psc?/V52hTYBe40XQKg3ty77Y0YPE4S2QKHbM/45NBuzDIW489QBoVep5mcQaIr2wdYcoru7B8IOrLeR*gjHWKrpX7LOWfaiWcuAUwnnq6krlUuO9y3GqBQ66w4ErgZebDqBgP21AmXFz0erE!/b&bo=OARUBgAAAAABJ24!&rf=viewer_4', }
            ]
        }
    }
    if getHoliday():
        return False
    requests.post(
        url,
        headers=headers, json=data)
    data = {
        "msgtype": "markdown",
        "markdown": {
            "content": dictToList(reason)
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


def dictToList(result_dict):
    list_case = []
    for k, v in result_dict.items():
        list_case.append(
            '<font color="comment">{}</font> : <font color=\"info\">{}</font>'.format(k, v))
    case = '\n'.join(list_case)
    return case


reason_list = ['恭喜您成为尊贵的梅赛德斯奔驰车主，愿三叉星辉照亮您的事业与前程。',
               '恭喜您成为尊贵的保时捷车主，愿黑马金盾守护您高贵的人生。',
               '恭喜您成为尊贵的奥迪车主，愿四环星辉照亮您的事业前程，愿世间美好从此与你环环相扣。',
               '恭喜您成为尊贵的宝马车主，愿浩瀚的蓝天白云，承载您的美好征程。',
               '恭喜您成为尊贵的红旗车主，愿红旗与您一起乘风破浪，蒸蒸日上，目光所致，皆是华夏，五星闪耀，皆是信仰。',
               '恭喜您成为尊贵的大众车主，愿VW星辉照耀您未来的事业前程，愿您以后踏遍大好河山，众拥天下。',
               '恭喜您成为尊贵的凯迪拉克车主，愿七彩圣盾保佑您的事业前程，所有的伟大都源于一次勇敢的开始，愿世间每一次泡澡都能拥有新的感悟。',
               '恭喜您成为尊贵的五菱宏光车主，愿红鹰展翅，照亮你加班的路程，愿更大的后备箱，能够帮你拉更多的货。']

if __name__ == '__main__':
    robot()
