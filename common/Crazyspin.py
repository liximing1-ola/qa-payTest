import urllib.parse
import requests
from common.Config import config
from common.Session import Session
import urllib3


class crazySpin:
    @staticmethod
    def spinBuy(uid):
        url1 = config.pt_host
        params = {
            'package': 'com.imbb.oversea.android',
            '_ipv': '0',
            '_platform': 'android',
            '_index': '218',
            '_model': 'Pixel 3a',
            '_timestamp': '1656064223',
            '_abi': 'arm64-v8a',
            'format': 'json',
            '_sign': '9a790a06ee3fc5da796009f6e4b6b95e',
            '_blid': uid,
        }
        url2 = url1 + 'pay/create' + '?' + urllib.parse.urlencode(params)
        return url2

    @staticmethod
    def spinPlay(uid):
        url3 = config.pt_host + '/go/party/turntable/draw'
        params = {
            'package': 'com.imbb.oversea.android',
            '_ipv': '0',
            '_platform': 'android',
            '_index': '878',
            '_model': 'Pixel 3a',
            '_timestamp': '1656067298',
            '_abi': 'arm64-v8a',
            'format': 'json',
            '_sign': '12c5970528bf21e8aac9586534606432',
            '_blid': uid,
        }
        url4 = url3 + '?' + urllib.parse.urlencode(params)
        return url4

    @staticmethod
    def turntablelist(rid, uid, tokenName='dev'):
        url5 = config.pt_host + '/go/party/turntable/list'
        params = {
            'rid': rid,
            'package': 'com.imbb.oversea.android',
            '_ipv': '0',
            '_platform': 'android',
            '_index': '878',
            '_model': 'Pixel 3a',
            '_timestamp': '1656067298',
            '_abi': 'arm64-v8a',
            'format': 'json',
            '_sign': '12c5970528bf21e8aac9586534606432',
            '_blid': uid,
        }
        url6 = url5 + '?' + urllib.parse.urlencode(params)
        urllib3.disable_warnings()
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        header = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko)\
                                Chrome/67.0.3396.99 Safari/537.36",
            "Content-Type": "application/x-www-form-urlencoded",
            'Connection': 'close',
            "user-token": Session.checkUserToken(operate='read', app_name=tokenName)
        }
        return requests.get(url5, params=params, headers=header)

    @staticmethod
    def turntablehorn(uid, tokenName='dev'):
        url7 = config.pt_host + '/go/party/turntable/horn'
        params = {
            'turntable_type': 1,
            'package': 'com.imbb.oversea.android',
            '_ipv': '0',
            '_platform': 'android',
            '_index': '878',
            '_model': 'Pixel 3a',
            '_timestamp': '1656067298',
            '_abi': 'arm64-v8a',
            'format': 'json',
            '_sign': '12c5970528bf21e8aac9586534606432',
            '_blid': uid,
        }
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        header = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko)\
                                Chrome/67.0.3396.99 Safari/537.36",
            "Content-Type": "application/x-www-form-urlencoded",
            'Connection': 'close',
            "user-token": Session.checkUserToken(operate='read', app_name=tokenName)
        }
        return requests.get(url7, params=params, headers=header)
