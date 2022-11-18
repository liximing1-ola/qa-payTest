# coding=utf-8
"""
封装 request
"""
from time import time
from urllib.parse import urlencode, unquote
import requests
import urllib3
from caseStarify.need_data import starify_payUid
from caseStarify.tools import create_sign
from common import Session
from common.Basic_starify import header_starify
from common.Basic_starify import query_starify
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
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
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
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    # 处理header
    header = header_starify.copy()
    header['user-token'] = Session.checkUserToken(operate='read', app_name=tokenName)

    # 处理query
    deal_query = query_starify.copy()
    deal_query['_timestamp'] = str(int(time()))
    sign = create_sign(deal_query)
    deal_query['_sign'] = sign
    deal_query['_blid'] = starify_payUid
    url = url + "?" + unquote(urlencode(deal_query))

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
    print(response.json())
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