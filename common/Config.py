# coding=utf-8
import os

class config:
    #  工程目录
    BASE_PATH = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    #  release域名
    domain_host = {'bb': 'https://api.yinjietd.com/', 'bb_dev_58': 'https://dev.iambanban.com/',
                   'pt': 'https://test.overseaban.com/', }

    # dev域名-（国内qq登陆方式)
    dev_host = domain_host['bb_dev_58']
    qq_login_url = dev_host + 'account/qqlogin'
    # pt域名- （pt登陆方式）
    pt_host = domain_host['pt']
    mobile_login_url = pt_host + 'account/passwordLogin'

    # 被打赏者
    testUid = 105002312
    # 打赏者
    payUid = 103273407
    # 打包结算主播
    pack_cal_uid =105002313

    # PT
    pt_test_uid = {'payUid': 800240376, 'testUid': 800000116}
    pt_payUid = pt_test_uid['payUid']
    pt_testUid = pt_test_uid['testUid']


if __name__ == '__main__':
    print(config.BASE_PATH)
    print(config.qq_login_url)
    print(config.mobile_login_url)