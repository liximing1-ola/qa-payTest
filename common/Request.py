# coding=utf-8
"""
封装 request
"""
import requests
import urllib3
from requests.packages.urllib3.exceptions import InsecureRequestWarning  # 使用requests库请求HTTPS时,因为忽略证书验证,导致每次运行时都会报错

from common import Session
from common.Session import Session


def post_request_session(url, data, tokenName='dev'):
    """
    post请求
    :param url:
    :param data:
    :param tokenName:
    :return:
    """
    urllib3.disable_warnings()
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    header = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 11; HD1900 Build/RKQ1.201022.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/87.0.4280.141 Mobile Safari/537.36 / Xs android V1.1.0.0 / Js V1.0.0.0 / Login V1658980709",
        "Content-Type": "application/x-www-form-urlencoded",
        'Connection': 'close',
        "user-token": Session.checkUserToken(operate='read', app_name=tokenName)
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
    time_consuming = response.elapsed.microseconds/1000
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


def post_request_session_starify(url, data, tokenName='starify'):
    """
    post请求
    :param url:
    :param data:
    :param tokenName:
    :return:
    """
    urllib3.disable_warnings()
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    header = {
        "user-agent": "Mozilla/5.0 (Linux; Android 12; vivo 1915 Build/SP1A.210812.003; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/103.0.5060.129 Mobile Safari/537.36 / Xs android V1.0.3.0 / Js V1.0.0.0 / Login V0",
        "user-brand": "vivo",
        "user-model": "vivo 1915",
        "user-tag": "f576d6f31f83dea5",
        "user-idfa": "",
        "user-mac":"f576d6f31f83dea5",
        "user-channel": "starify_office",
        "user-oaid": "",
        "user-issimulator": "false",
        "user-did": "DUK0moJCeRgwKU4cjRdpRmRYxtFGanaEZ729RFVLMG1vSkNlUmd3S1U0Y2pSZHBSbVJZeHRGR2FuYUVaNzI5c2h1",
        "user-page": "%2F",
        "user-isroot": "false",
        "user-abi":"arm64-v8a",
        "user-imei":"f576d6f31f83dea5",
        "user-language": "zh_CN",
        'accept-encoding': 'gzip',
        'host': "47.243.83.154",

        'content-type': 'application/x-www-form-urlencoded; charset=utf-8',
        'user-token': Session.checkUserToken(operate='read', app_name=tokenName)

    }
    from common.Basic_starify import query_starify,body_starify
    from caseStarify.tools import create_sign
    from time import time
    from urllib.parse import urlencode, urlunparse, unquote
    from caseStarify.tools import merge_dicts
    deal_query = query_starify.copy()
    deal_query['_timestamp'] = str(int(time()))
    body = body_starify
    sign = create_sign(deal_query)
    deal_query['_sign'] = sign
    deal_query['_blid'] = "124313"#todo
    url = url+"?"+unquote(urlencode(deal_query))

    # if not url.startswith('https://'):
    #     url = '%s%s' % ('https://', url)
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
        response_dicts['body']= response.json()
    except Exception as e:
        print(e)
        response_dicts['body'] = ''
    response_dicts['time_consuming'] = time_consuming
    response_dicts['time_total'] = time_total
    return response_dicts
"""
{'success': True, 'data': {'star_coin': 1002010}}
{'msg': '同一个星币礼物只能打赏同一个作品一次'}
"""