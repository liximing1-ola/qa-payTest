# coding=utf-8
"""
HTTP 请求封装模块

提供统一的 HTTP POST 请求功能，支持 Token 管理、HTTPS 转换和响应解析。
"""
import time
from typing import Dict, Any, Optional
import requests
import urllib3
from common.Session import Session

urllib3.disable_warnings()
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 默认请求头
DEFAULT_HEADERS: Dict[str, str] = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 11; HD1900 Build/RKQ1.201022.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/87.0.4280.141 Mobile Safari/537.36 / Xs android V1.1.0.0 / Js V1.0.0.0 / Login V1658980709",
    "Content-Type": "application/x-www-form-urlencoded",
    'Connection': 'close'
}

# 请求超时配置
DEFAULT_TIMEOUT: float = 30.0


def _build_headers(token_name: str = 'dev') -> Dict[str, str]:
    """构建请求头
    
    Args:
        token_name: Token 名称
        
    Returns:
        请求头字典
    """
    headers = DEFAULT_HEADERS.copy()
    headers["user-token"] = Session.checkUserToken(operate='read', app_name=token_name)
    return headers


def _ensure_https(url: str) -> str:
    """确保 URL 使用 HTTPS
    
    Args:
        url: 原始 URL
        
    Returns:
        转换后的 HTTPS URL
    """
    return url if url.startswith('https://') else f'https://{url}'


def _parse_response(response: requests.Response) -> Dict[str, Any]:
    """解析响应结果
    
    Args:
        response: requests 响应对象
        
    Returns:
        解析后的结果字典
    """
    print(response.json())
    return {
        'code': response.status_code,
        'time_consuming': response.elapsed.microseconds / 1000,
        'time_total': response.elapsed.total_seconds(),
        'body': response.json() if response.ok else ''
    }


def post_request_session(url: str, data: Optional[Any], 
                         token_name: str = 'dev',
                         timeout: float = DEFAULT_TIMEOUT) -> Dict[str, Any]:
    """
    POST 请求
    
    Args:
        url: 请求 URL
        data: 请求数据
        token_name: Token 名称，默认为 'dev'
        timeout: 请求超时时间，默认 30 秒
        
    Returns:
        包含 code、body、time_consuming、time_total 的响应字典
    """
    headers = _build_headers(token_name)
    url = _ensure_https(url)

    try:
        response = requests.post(
            url=url, 
            data=data, 
            headers=headers, 
            verify=False,
            timeout=timeout
        )
        return _parse_response(response)
    except requests.Timeout:
        print(f"Request timeout: {url}")
        return {'code': -1, 'body': '', 'error': 'timeout'}
    except requests.RequestException as e:
        print(f"Request error: {e}")
        return {'code': -1, 'body': '', 'error': str(e)}
    except Exception as e:
        print(f"Unexpected error: {e}")
        return {'code': -1, 'body': '', 'error': str(e)}


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