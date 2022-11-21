import requests
import time


def robot():
    url = 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=ddf98ffd-fd35-42be-8362-5e485b08226a'  # 质量周报机器人
    headers = {'Content-Type': 'application/json'}
    # reason = {'【雷鸟】': '所有的不甘,都是因为还心存梦想,在你放弃之前,好好拼一把,只怕心老,不怕路长'}
    now = time.strftime('%m-%d', time.localtime(time.time()))
    title = "质量周报_{}".format(now)
    des = '点击图片查看本周质量文档统计'
    data = {
        "msgtype": "news",
        "news": {
            "articles": [{
                "title": title,
                "description": des,
                "url": "https://doc.weixin.qq.com/sheet/e3_AHEAsAZ-AB0kquttATbRHC7ipzUTg?scode=ACkAfQfVAAg4ke8jKPAHEAsAZ-AB0",
                "picurl": 'http://m.qpic.cn/psc?/V52hTYBe40XQKg3ty77Y0YPE4S2QKHbM/ruAMsa53pVQWN7FLK88i5rUbx260PN7cBpa3cHGXHLPsLOcPmWzR41DBbV7JpWN4k7XVVmnnuDdrGo5K*E.oqFOPsoJVxFY6xP9uhukeB1o!/b&bo=0ALzAQAAAAADBwI!&rf=viewer_4', }
            ]
        }
    }
    requests.post(
        url,
        headers=headers, json=data)


def dictToList(result_dict):
    list_case = []
    for k, v in result_dict.items():
        list_case.append(
            '<font color="comment">{}</font> : <font color=\"info\">{}</font>'.format(k, v))
    case = '\n'.join(list_case)
    return case


if __name__ == '__main__':
    robot()
