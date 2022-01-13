# coding=utf-8
import os
class config:
    #  工程目录
    BASE_PATH = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    #  release域名
    domain_host = {'bb_dev_58': 'https://dev.iambanban.com/', 'pt': 'https://test.overseaban.com/', }
    dev_host = domain_host['bb_dev_58']
    pay_url = dev_host + 'pay/create?package=com.imbb.banban.android'  # 内网支付接口
    # 标准配置
    bb_user = {
        'payUid': 103273407,  # god
        'testUid': 105002312,  # 非一代宗师
        'pack_cal_uid': 105002313,  # 打包结算签约主播
        'bb_git_branch': 'chenbin/ft_go_consume',  # 线上代码分支
    }
    # 直播间角色配置
    live_role = {
        'pack_ceo': 105002314,  # 直播公会公会长
        'pack_master_NoPack': 105002319,  # 非公会一代宗师主播
        'pack_cal_uid': 105002313,  # 公会签约主播（打包结算），宗师等级可设置为一代和非一代
        'testUid': 105002312,  # 非公会非一代宗师主播
        'live_rid': 193185577,  # 直播间
        'auto_rid': 193185484,  # 商业8坑位房间
        'cp_link_rid': 193185538  # 商业连连看房间
    }
    # 网赚房角色配置
    star_role = {
        'testUid': 105002312,  # 非公会用户
        'auto_rid': 193185484,  # 商业8坑位房间
        'super_star_uid': 105002325,  # 指定工会艺人
        'super_agent_uid': 105002323,  # 指定工会经纪人
        'agent_star_uid': 105002331,  # 指定工会内有经纪人(105002323)的艺人
        'super_broker': 136594717,  # 指定工会bid
        'super-voice-fresh': 200000287,  # 网赚房间
        'pack_cal_uid': 105002313,  # 公会签约主播（打包结算）
        'white_uid': 105002338,  # 白名单用户
    }
    #  礼物配置
    giftId = {
        "5": 5,  # 棒棒糖*1币
        "7": 7,  # 大宝剑*10币
        "11": 11,  # 老司机*30币(券-5)
        "46": 46,  # 幸运星*6币
        "47": 47,  # 五色星*21币
        "54": 54,  # 小天使*99币（商城购买）
        "62": 62,  # 人气券*20（金币）
        "362": 362,  # 啵啵奶茶*1000（金豆）
    }
    qq_login_url = dev_host + 'account/qqlogin'  # dev域名（qq登陆方式)
    rewardUid = bb_user['testUid']  # 被打赏者
    rewardUid2 = 100500205  # 被打赏者
    payUid = bb_user['payUid']  # 打赏者
    pack_cal_uid = bb_user['pack_cal_uid']  # 打包结算主播
    banban_git_branch = bb_user['bb_git_branch']  # git branch

    # PT
    pt_user = {
        'payUid': 800240376,
        'testUid': 800000116,
        'pt_git_branch': 'main'}
    # pt域名-（PT登陆方式）
    pt_host = domain_host['pt']
    mobile_login_url = pt_host + 'account/passwordLogin'
    pt_payUid = pt_user['payUid']
    pt_testUid = pt_user['testUid']
    # git branch
    pt_git_branch = pt_user['pt_git_branch']

    # 谁是凶手
    games_user = {
        'payUid': 105000291,
        'testUid': 128440025,
        'gameRid': 200000799,
        'games_git_branch': 'release-for-vpc',  # 线上代码分支
    }
    games_payUid = games_user['payUid']
    games_testUid = games_user['testUid']
    games_rid = games_user['gameRid']


if __name__ == '__main__':
    print(config.BASE_PATH)
    print(config.pay_url)
    print(config.mobile_login_url)
    print(config.banban_git_branch)