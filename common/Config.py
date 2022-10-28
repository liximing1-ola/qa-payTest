# coding=utf-8
import os


class config:
    # 工程目录
    BASE_PATH = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    appInfo = {'bb_dev_58': 'https://dev.iambanban.com/',
               'pt_ali': 'https://test.overseaban.com/',
               'banban': 'com.imbb.banban.android',
               'pt': 'com.ola.chat',
               'starify': 'http://47.243.83.154/',
               "rush": 'https://192.168.11.55/',
               }
    codeInfo = {'bb_php_path': '/home/webroot/banban',
                'bb_go_path': '/home/webroot/bb-consume',
                'pt_php_path': '/home/webroot/release_oversea/banban',
                'bb_git_branch': 'release-for-vpc',
                'bb_go_git_branch': 'master',
                'pt_git_branch': 'main',
                'starify_go_path': r"/var/www/sta-go",
                # todo 调试用 r"/home/spirit/code/qa-payTest" / dev r"/var/www/sta-go"
                'starify_room_path': r"/var/www/sta-room",
                # todo 调试 用 r"/home/spirit/code/qa-payTest" / dev r"/var/www/sta-room"
                'starify_git_branch': "dev",  # todo 调试用 "wzx" / dev分支  dev
                }
    appName = {
        "伴伴": 'banban',
        "Partying": 'pt',
        "谁是凶手": 'games',
        "嗨歌": 'havefun',
        "starify": 'starify',
        "冲鸭": 'rush',
    }
    # 测试域名
    bb_host = appInfo['bb_dev_58']
    pt_host = appInfo['pt_ali']
    starify_host = appInfo['starify']
    rush_host = appInfo['rush']
    # 内网支付接口
    pay_url = bb_host + 'pay/create?package=com.imbb.banban.android'
    pt_pay_url = pt_host + 'pay/create?package=com.ola.chat'
    starify_pay_url = starify_host + 'go/starify/pay/create'
    rush_pay_url = bb_host + "pay/create?package=com.im.duck.android"

    # 服务器标识
    linux_node = {
        'ali': 'iZj6c7cxmmtvxr9kuetoizZ',
        'ali-starify': 'iZj6cig35upuwmdws5sec2Z',  # todo 修改 调试用 ubuntu / dev=iZj6cig35upuwmdws5sec2Z
    }
    # app登录方式
    bb_qqLogin_url = bb_host + 'account/qqlogin'
    pt_mobile_login_url = pt_host + 'account/passwordLogin'
    starify_mobile_login_url = starify_host + 'go/starify/login/mobileLogin'

    # banban用户配置
    bb_user = {
        'payUid': 103273407,  # god
        'testUid': 105002312,  # 非一代宗师
        'pack_cal_uid': 105002313,  # 打包结算签约主播
    }
    # 直播间角色配置
    live_role = {
        'pack_ceo': 105002314,  # 直播公会公会长
        'pack_master_NoPack': 105002319,  # 非公会一代宗师主播
        'pack_cal_uid': 105002313,  # 公会签约主播（打包结算），宗师等级可设置为一代和非一代
        'testUid': 105002312,  # 非公会非一代宗师主播
        'live_rid': 193185577,  # 直播间，房主:105002313
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
    # 礼物配置
    giftId = {
        "5": 5,  # 棒棒糖*1币
        "7": 7,  # 大宝剑*10币
        "11": 11,  # 老司机*30币(券-5)
        "46": 46,  # 幸运星*6币
        "47": 47,  # 五色星*21币
        "54": 54,  # 小天使*99币（商城购买）
        "62": 62,  # 人气券*20（金币）
        "362": 362,  # 啵啵奶茶*1000（金豆）
        "773": 773,  # 小飞机盲盒
        "774": 774,  # 飞马盲盒
    }
    rewardUid = bb_user['testUid']  # 被打赏者
    rewardUid2 = 100500205  # 被打赏者
    payUid = bb_user['payUid']  # 打赏者
    pack_cal_uid = bb_user['pack_cal_uid']  # 打包结算主播

    # PT
    pt_user = {'payUid': 800240376,
               'testUid': 800022872,
               'brokerUid': 800018895,
               'fleet_uid': 800041062}
    pt_payUid = pt_user['payUid']
    pt_testUid = pt_user['testUid']  # 非公会成员，是一代宗师
    pt_brokerUid = pt_user['brokerUid']  # 公会成员
    pt_fleetUid = pt_user['fleet_uid']
    # 房间类型41
    pt_room = {
        'business_joy': 105697423,  # 商业房
        'th_union': 105708881,  # 泰区联盟房
        'en_fleet': 105717544,  # 英语大区家族房
        'id_fleet': 105711999,  # 印尼大区家族房
        'ms_fleet': 105725790,  # 马来大区家族房
        'vip_rid': 105698376,  # 个人房
    }
    # 礼物配置
    pt_giftId = {
        "10": 10,  # 么么哒*6币
        "46": 46,  # 幸运星*6币
        "47": 47,  # 五色星*21币
    }


if __name__ == '__main__':
    print(config.appInfo.items())
    print(config.appInfo.get('banban'))
    print(config.appName['谁是凶手'])
    print(config.pt_giftId.values())
    print(tuple(i for i in config.pt_giftId.values()))
    print(config.pt_user.values())
