import requests
from common.method import dictToList

def robot():
    url1 = 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=e317861a-d1ec-4ac4-af96-9d4b8f12d9d6'
    url= 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=0179d8d1-2078-41ba-a8da-0fb11bd51880'
    headers = {'Content-Type': 'application/json'}
    reason = {'tea-1': 'cake', 'tea-2': 'milky tea', 'tea-3': 'cook', 'tea-4': 'chicken', 'tea-5': 'fruit'}
    data = {
        "msgtype": "markdown",
        "markdown": {
            "content": dictToList(reason)
        }
    }
    requests.post(url, headers=headers, json=data)


if __name__ == '__main__':
    robot()
