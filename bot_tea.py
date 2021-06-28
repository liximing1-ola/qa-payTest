import requests
import time

def robot():
    url1 = 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=e317861a-d1ec-4ac4-af96-9d4b8f12d9d6'
    url= 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=0179d8d1-2078-41ba-a8da-0fb11bd51880'
    headers = {'Content-Type': 'application/json'}
    reason = {'HighTea-1': 'cake（手快有手慢无）', 'HighTea-2': 'milky tea（手快有手慢无）', 'HighTea-3': 'cook（无图）', 'HighTea-4': 'chicken（无图）', 'HighTea-5': 'fruit（无图）'}
    now = time.strftime('%H:%M', time.localtime(time.time()))
    title = "广告位招租:当前时间-{}, 放松下，自取下午茶".format(now)
    des = '手快有手慢无'
    data = {
        "msgtype": "news",
        "news": {
            "articles": [{
                "title": title,
                "description": des,
                "url": "https://meican.com/",
                "picurl": '/home/banban-1/payTest/001.jpg', }
            ]
        }
    }
    r = requests.post(
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


if __name__ == '__main__':
    robot()
