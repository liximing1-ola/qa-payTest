# coding=utf-8
import os


class config:
    # 工程目录
    BASE_PATH = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    appInfo = {
        'bb_dev': 'https://dev.iambanban.com/',
        'pt_ali_dev': 'https://pt-dev.iambanban.com/',              # 指向dev服务
        'pt_ali_main':'https://pt-dev.iambanban.com/_testcase/',     # 指向线上拉取的main分支服务，go的还需要新启一个
        'starify': 'http://116.62.125.230/',
        "rush": 'https://192.168.11.55/',
    }
    codeInfo = {
        'bb_php_path': '/home/webroot/banban',
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
        "starify": 'starify',
        "冲鸭": 'rush',
    }
    # 服务器标识
    linux_node = {
        'ali': 'iZbp1fveowr7j693hrwb48Z',
        'ali-starify': 'iZbp15ildwog86lw08ptpnZ',  # todo 修改 调试用 ubuntu / dev=iZj6cig35upuwmdws5sec2Z
    }
    # 测试域名
    pt_host = appInfo['pt_ali_main']
    # 内网支付接口
    pay_url = appInfo['bb_dev'] + 'pay/create?package=com.imbb.banban.android'
    pt_pay_url = pt_host + 'pay/create?package=com.imbb.oversea.android'
    starify_pay_url = appInfo['starify'] + 'go/starify/pay/create'
    rush_pay_url = appInfo['bb_dev'] + "pay/create?package=com.im.duck.android"
    # app登录方式
    bb_qqLogin_url = appInfo['bb_dev'] + 'account/qqlogin'
    pt_mobile_login_url = pt_host + 'account/passwordLogin' + '?package=com.imbb.oversea.android'  # 加包名限制
    starify_mobile_login_url = appInfo['starify'] + 'go/starify/login/mobileLogin'

    rate = 0.62  # GS商业房分成比，公会长和商业房房主不参与降点逻辑（公会长/房主仅作为被打赏者不扣）

    # 用户配置
    bb_user = {
        'payUid': 103273407,  # boss
        'testUid': 105002312,  # 非一代宗师
        'pack_cal_uid': 105002313,  # 打包结算签约主播
        'vipRoomRid': 200089706,  # 个人房，房主uid=103273407
        'gsUid': 105002325,  # GS用户,直播公会未签约打包结算等同于普通公会（一代宗师，徒弟：105002312）
        'prettyRid': 200089942,  # 靓号房, 房主uid=105002325
        'fleetRid': 200091067,  # 家族房，家主uid=103273407，成员105002325/100500205/100500338
    }
    # 角色配置
    live_role = {
        'pack_ceo': 105002314,  # 直播公会公会长
        'pack_master_NoPack': 105002319,  # 非公会一代宗师主播
        'pack_cal_uid': 105002313,  # 公会签约主播（打包结算），宗师等级可设置为一代和非一代
        'live_rid': 193185577,  # 直播间(types=live)，房主:105002313
        'auto_rid': 193185484,  # business | types: auto | room_factory_type: business-content | settlement_channel: cp-women
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
    }

    payUid = bb_user['payUid']  # 打赏者
    rewardUid = bb_user['testUid']  # 被打赏者(非一代宗师)
    masterUid = 100500338  # 被打赏者（一代宗师）
    gsUid = bb_user['gsUid']  # 公会用户

    # PT
    pt_user = {
        'payUid': 800240376,
        'testUid': 800022872,
        'brokerUid': 800018895,
        'fleet_uid': 800041062
    }
    pt_payUid = pt_user['payUid']
    pt_testUid = pt_user['testUid']  # 非公会成员，是一代宗师
    pt_brokerUid = pt_user['brokerUid']  # 公会成员
    pt_fleetUid = pt_user['fleet_uid']
    # 房间类型41
    pt_room = {
        'business_joy': 105699329,  # 商业房
        'vip_rid': 105698376,  # 个人房
        'th_union': 105708881,  # 泰区联盟房
        'en_fleet': 105717544,  # 英语大区家族房
        'id_fleet': 105711999,  # 印尼大区家族房
        'ms_fleet': 105725790,  # 马来大区家族房
        'business_joy_ar': 105726673,  # 阿语商业房
        'union_ar': 105713367,  # 阿语联盟房
        'business_joy_vi': 105726676,  # 越南商业房
        'union_vi': 105718889,  # 越南联盟房

    }
    # 礼物配置
    pt_giftId = {
        "10": 10,  # 么么哒*6币
        "46": 46,  # 幸运星*6币
        "47": 47,  # 五色星*21币
        "773": 773,  # 小飞机盲盒
        "774": 774,  # 飞马盲盒
    }

