import urllib.parse
from common.Config import config

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
        url2 = url1+'pay/create'+'?'+urllib.parse.urlencode(params)
        return url2
        print(crazySpin.spinBuy())

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
        url4 = url3+'?'+urllib.parse.urlencode(params)
        return url4
        print(crazySpin.spinPlay(uid))

