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

    #  cdn域名
    image_host = {'bb': 'http://xs-image.oss-cn-hangzhou.aliyuncs.com/',
                  'pt': 'http://partying.oss-ap-southeast-1.aliyuncs.com/'}
    oss_host = image_host['bb']
    app_package = {'bb': 'com.imbb.banban.com', 'rpg': ''}

    # roomConfig
    roomConfig_url = release_host + 'room/config/?version=23&from_match=0&package=com.imbb.banban.android'
    # qq_login url
    qq_login_url = dev_host + 'account/qqlogin'
    # 被打赏者
    # testUid = 100050010
    testUid = 105002660
    # 打赏者
    payUid = 103273407


if __name__ == '__main__':
    print(config.BASE_PATH)
    print(config.oss_host)