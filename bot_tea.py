import requests
import time

def robot():
    url = 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=e317861a-d1ec-4ac4-af96-9d4b8f12d9d6'
    url1= 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=0179d8d1-2078-41ba-a8da-0fb11bd51880'
    headers = {'Content-Type': 'application/json'}
    reason = {'广告位招租': '霸气牛油果生椰斑斓（手快有手慢无）'}
    now = time.strftime('%H:%M', time.localtime(time.time()))
    title = "下午茶时间到:当前时间-{}, 放松一下，马上回来".format(now)
    des = '谢谢榜一大哥：下午茶大作战'
    data = {
        "msgtype": "news",
        "news": {
            "articles": [{
                "title": title,
                "description": des,
                "url": "https://meican.com/",
                "picurl": 'http://m.qpic.cn/psc?/V52hTYBe40XQKg3ty77Y0YPE4S2QKHbM/45NBuzDIW489QBoVep5mcQaIr2wdYcoru7B8IOrLeR*gjHWKrpX7LOWfaiWcuAUwnnq6krlUuO9y3GqBQ66w4ErgZebDqBgP21AmXFz0erE!/b&bo=OARUBgAAAAABJ24!&rf=viewer_4', }
            ]
        }
    }
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


if __name__ == '__main__':
    robot()
