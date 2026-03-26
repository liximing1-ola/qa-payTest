# coding=utf-8
"""
封装 request
"""
import requests
import urllib3
from common.Session import Session

urllib3.disable_warnings()
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# 默认请求头
DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 11; HD1900 Build/RKQ1.201022.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/87.0.4280.141 Mobile Safari/537.36 / Xs android V1.1.0.0 / Js V1.0.0.0 / Login V1658980709",
    "Content-Type": "application/x-www-form-urlencoded",
    'Connection': 'close'
}


def _build_headers(token_name='dev'):
    """构建请求头"""
    headers = DEFAULT_HEADERS.copy()
    headers["user-token"] = Session.checkUserToken(operate='read', app_name=token_name)
    return headers


def _ensure_https(url):
    """确保URL使用HTTPS"""
    return url if url.startswith('https://') else f'https://{url}'


def _parse_response(response):
    """解析响应结果"""
    print(response.json())
    result = {
        'code': response.status_code,
        'time_consuming': response.elapsed.microseconds / 1000,
        'time_total': response.elapsed.total_seconds()
    }
    try:
        result['body'] = response.json()
    except Exception as e:
        print(e)
        result['body'] = ''
    return result


def post_request_session(url, data, token_name='dev'):
    """
    POST请求
    
    Args:
        url: 请求URL
        data: 请求数据
        token_name: token名称，默认为'dev'
    
    Returns:
        dict: 包含code、body、time_consuming、time_total的响应字典
    """
    headers = _build_headers(token_name)
    url = _ensure_https(url)

    try:
        response = requests.post(url=url, data=data, headers=headers, verify=False)
        return _parse_response(response)
    except requests.RequestException as e:
        print(f"Request error: {e}")
        return {}
    except Exception as e:
        print(f"Unexpected error: {e}")
        return {}


if __name__ == '__main__':
    # 测试代码
    test_headers = {
        'user-agent': 'Mozilla/5.0 (Linux; Android 11; CPH1969 Build/RP1A.200720.011; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/115.0.5790.138 Mobile Safari/537.36 / Xs android V5.0.31.0 / Js V1.0.0.0 / Login V1691131402',
        'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8',
        'Connection': 'close',
        'user-token': 'a4d3klcO2pbZg0__2BvGlU7jGTRCAPyfVdQ7nySzDPs0PZEi7rbX8VC__2BZ0QoEz2auiTnhYEWu1kYG7s7F7G__2BinZ7ZIT9QxfQ2MFc0LrVe12GOBdiICefxz82aloSw'
    }
    test_url = 'https://116.62.125.230/pay/create?package=com.yhl.sleepless.android'
    test_data = 'platform=available&type=chat-gift&money=1000&params=%7B%22notify_group_id%22%3A0%2C%22to%22%3A%22105002312%22%2C%22giftId%22%3A5%2C%22giftNum%22%3A10%2C%22cid%22%3A0%2C%22ctype%22%3A%22%22%2C%22duction_money%22%3A0%2C%22version%22%3A2%2C%22num%22%3A10%2C%22gift_type%22%3A%22normal%22%2C%22star%22%3A0%2C%22show_pac_man_guide%22%3A1%2C%22all_mic%22%3A0%2C%22useCoin%22%3A-1%7D'
    print(requests.post(url=test_url, data=test_data, headers=test_headers, verify=False).json())
