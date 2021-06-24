# coding=utf-8
import os
class config:
    #  工程目录
    BASE_PATH = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    #  release域名
    domain_host = {'bb_dev_58': 'https://dev.iambanban.com/',
                   'pt': 'https://test.overseaban.com/', }

    # 伴伴
    bb_test = {'payUid': 103273407, 'testUid': 105002312, 'pack_cal_uid': 105002313, 'bb_git_branch': 'alpha-for-vpc'}
    # dev域名（qq登陆方式)
    dev_host = domain_host['bb_dev_58']
    qq_login_url = dev_host + 'account/qqlogin'
    # 被打赏者
    testUid =bb_test['testUid']
    testUid_2 = 100500205
    # 打赏者
    payUid = bb_test['payUid']
    # 打包结算主播
    pack_cal_uid = bb_test['pack_cal_uid']
    # git branch
    banban_git_branch = bb_test['bb_git_branch']

    # PT
    pt_test= {'payUid': 800240376, 'testUid': 800000116, 'pt_git_branch': 'release_for_php7'}
    # pt域名-（PT登陆方式）
    pt_host = domain_host['pt']
    mobile_login_url = pt_host + 'account/passwordLogin'
    pt_payUid = pt_test['payUid']
    pt_testUid = pt_test['testUid']
    # git branch
    pt_git_branch = pt_test['pt_git_branch']


if __name__ == '__main__':
    print(config.BASE_PATH)
    print(config.qq_login_url)
    print(config.mobile_login_url)
    print(config.banban_git_branch)