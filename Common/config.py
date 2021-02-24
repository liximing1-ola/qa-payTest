# coding=utf-8
import os

class config:
    #  工程目录
    BASE_PATH = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    #  release域名
    domain_host = {'bb': 'https://api.yinjietd.com/', 'pt': 'https://api.partying.sg/',
                   'bb_dev': 'https://192.168.11.58/', }
    release_host = domain_host['bb']
    # dev域名
    dev_host = domain_host['bb_dev']
    # qq_login url
    qq_login_url = dev_host + 'account/qqlogin'
    # 被打赏者
    testUid = 105002312
    # testUid = 105002660
    # 打赏者
    payUid = 103273407


if __name__ == '__main__':
    print(config.BASE_PATH)