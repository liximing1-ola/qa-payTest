import urllib.parse
import requests
import urllib3
from common.Config import config
from common.Session import Session

urllib3.disable_warnings()
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# 默认请求参数
DEFAULT_PARAMS = {
    'package': 'com.imbb.oversea.android',
    '_ipv': '0',
    '_platform': 'android',
    '_model': 'Pixel 3a',
    '_abi': 'arm64-v8a',
    'format': 'json',
}

# 默认请求头
DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36",
    "Content-Type": "application/x-www-form-urlencoded",
    'Connection': 'close',
}


class CrazySpin:
    """操作类"""

    @staticmethod
    def _build_url(endpoint: str, params: dict) -> str:
        """构建完整URL"""
        base_url = config.pt_host + endpoint
        return f"{base_url}?{urllib.parse.urlencode(params)}"

    @staticmethod
    def _build_headers(token_name: str = 'dev') -> dict:
        """构建请求头"""
        headers = DEFAULT_HEADERS.copy()
        headers["user-token"] = Session.checkUserToken(operate='read', app_name=token_name)
        return headers

    @staticmethod
    def spin_buy_url(uid: int) -> str:
        """获取购买URL"""
        params = {
            **DEFAULT_PARAMS,
            '_index': '218',
            '_timestamp': '1656064223',
            '_sign': '9a790a06ee3fc5da796009f6e4b6b95e',
            '_blid': uid,
        }
        return CrazySpin._build_url('pay/create', params)

    @staticmethod
    def spin_play_url(uid: int) -> str:
        """获取抽奖URL"""
        params = {
            **DEFAULT_PARAMS,
            '_index': '878',
            '_timestamp': '1899475859',
            '_sign': '12c5970528bf21e8aac9586534606432',
            '_blid': uid,
        }
        return CrazySpin._build_url('/go/party/turntable/draw', params)

    @staticmethod
    def get_turntable_list(rid: int, uid: int, token_name: str = 'dev'):
        """获取转盘列表"""
        params = {
            **DEFAULT_PARAMS,
            'rid': rid,
            '_index': '878',
            '_timestamp': '1656067298',
            '_sign': '12c5970528bf21e8aac9586534606432',
            '_blid': uid,
        }
        url = config.pt_host + '/go/party/turntable/list'
        headers = CrazySpin._build_headers(token_name)
        return requests.get(url, params=params, headers=headers)

    @staticmethod
    def get_turntable_horn(uid: int, token_name: str = 'dev'):
        """获取转盘喇叭"""
        params = {
            **DEFAULT_PARAMS,
            'turntable_type': 1,
            '_index': '878',
            '_timestamp': '1656067298',
            '_sign': '12c5970528bf21e8aac9586534606432',
            '_blid': uid,
        }
        url = config.pt_host + '/go/party/turntable/horn'
        headers = CrazySpin._build_headers(token_name)
        headers['Connection'] = ''  # 特殊处理
        return requests.get(url, params=params, headers=headers)
