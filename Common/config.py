# coding=utf-8
import os

class config:
    #  工程目录
    BASE_PATH = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    #  release域名
    domain_host = {'bb': 'https://api.yinjietd.com/', 'pt': 'https://api.partying.sg/',
                   'bb_dev': 'https://dev.iambanban.com/', }
    release_host = domain_host['bb']
    # dev域名
    dev_host = domain_host['bb_dev']
    # qq_login url
    qq_login_url = dev_host + 'account/qqlogin'


    # 被打赏者
    testUid = 105002312
    # 打赏者
    payUid = 103273407
    # 打包结算主播
    pack_cal_uid =105002313


if __name__ == '__main__':
    print(config.BASE_PATH)
    print(config.qq_login_url)