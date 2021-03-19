# coding=utf-8
"""
封装 request
"""
import requests
from common import Session
from requests.packages.urllib3.exceptions import InsecureRequestWarning  # 使用requests库请求HTTPS时,因为忽略证书验证,导致每次运行时都会报错

def post_request_session(url, data):
    """
    post请求
    :param url:
    :param data:
    :return:
    """
    session = Session.Session()
    get_session = session.get_session('dev')
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    header = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko)\
                            Chrome/67.0.3396.99 Safari/537.36",
        "Content-Type": "application/x-www-form-urlencoded",
        'Connection': 'close',
        "user-token": get_session['token']
    }
    if not url.startswith('https://'):
        url = '%s%s' % ('https://', url)
    try:
        if data is None:
            response = requests.post(url=url, headers=header, verify=False)
        else:
            response = requests.post(url=url, data=data, headers=header, verify=False)
    except requests.RequestException as e:
        print(e)
        return ()
    except Exception as e:
        print(e)
        return ()
    time_consuming = response.elapsed.microseconds / 1000
    time_total = response.elapsed.total_seconds()
    response_dicts = dict()
    response_dicts['code'] = response.status_code
    try:
        response_dicts['body'] = response.json()
    except Exception as e:
        print(e)
        response_dicts['body'] = ''
    response_dicts['time_consuming'] = time_consuming
    response_dicts['time_total'] = time_total
    return response_dicts

def pt_post_request_session(url, data):
    session = Session.Session()
    get_session = session.get_session('pt')
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    header = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko)\
                            Chrome/67.0.3396.99 Safari/537.36",
        "Content-Type": "application/x-www-form-urlencoded",
        "user-token": get_session['token']
    }
    if not url.startswith('https://'):
        url = '%s%s' % ('https://', url)
    try:
        if data is None:
            response = requests.post(url=url, headers=header, verify=False)
        else:
            response = requests.post(url=url, data=data, headers=header, verify=False)
    except requests.RequestException as e:
        print(e)
        return ()
    except Exception as e:
        print(e)
        return ()
    time_consuming = response.elapsed.microseconds / 1000
    time_total = response.elapsed.total_seconds()
    response_dicts = dict()
    response_dicts['code'] = response.status_code
    try:
        response_dicts['body'] = response.json()
    except Exception as e:
        print(e)
        response_dicts['body'] = ''
    response_dicts['time_consuming'] = time_consuming
    response_dicts['time_total'] = time_total
    return response_dicts


if __name__ == '__main__':
    pass
