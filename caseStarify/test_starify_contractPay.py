import unittest

from caseStarify.deal_data import deal_pay_contract_data
from caseStarify.need_data import *
from common.Assert import *
from common.Consts import case_list, result
from common.Request import post_request_session_starify
from common.conStarifyMysql import conMysql
from common.method import reason_starify
from common.runFailed import Retry


@Retry(max_n=1)
class TestPayCreate(unittest.TestCase):
    def test_contract_001(self, des='原制作人续约，多次竞拍抬价，原制作人竞拍成功'):
        default_money = 100000
        #  sql:购买者A,a_uid 修改余额=10000
        conMysql.updateMoneySql(a_uid, default_money)
        #  sql:购买者B,b_uid 修改余额=10000
        conMysql.updateMoneySql(b_uid, default_money)
        #  sql:被购买者C,c_uid 修改余额=0
        conMysql.updateMoneySql(c_uid, 0)
        #  sql:购买者A,a_uid 修改财富值=0,控制签约人数=1
        conMysql.updateWealthSql(a_uid, 0)
        #  sql:购买者B,b_uid 修改财富值=0,控制签约人数=1
        conMysql.updateWealthSql(b_uid, 0)

        # sql:清除C的制作人
        conMysql.deleteProducerSinger(c_uid)
        # sql:修改C的身价=100
        conMysql.updateSingerWorth(c_uid, 100)

        # A直接签约C
        cost0 = 200
        time.sleep(0.5)
        data = deal_pay_contract_data("audition_contract", a_uid, cost0, 1)
        res = post_request_session_starify(config.starify_pay_url, data, token_name='starify', uid=a_uid)
        assert_code(res['code'])
        assert_body(res['body'], 'success', True, reason_starify(des, res))
        # A星币扣减100%
        assert_equal(conMysql.selectUserInfoSql('star_coin', a_uid), default_money - cost0)
        # A名额占用
        assert_equal(conMysql.selectProducerSinger(a_uid), 1)
        # C分成10%
        assert_equal(conMysql.selectUserInfoSql('star_coin', c_uid), cost0 * contract_ratio['singer'])

        # A续约C，第1次报价
        cost1 = 400
        time.sleep(0.5)
        data = deal_pay_contract_data("audition_contract", a_uid, cost1, 0)
        res = post_request_session_starify(config.starify_pay_url, data, token_name='starify', uid=a_uid)
        assert_code(res['code'])
        assert_body(res['body'], 'success', True, reason_starify(des, res))
        # 1次，A星币冻结
        assert_equal(conMysql.selectUserInfoSql('star_coin', a_uid), default_money - cost0 - cost1)

        # A续约C，第2次报价
        cost2 = 800
        time.sleep(0.5)
        data = deal_pay_contract_data("audition_contract", a_uid, cost2, 0)
        res = post_request_session_starify(config.starify_pay_url, data, token_name='starify', uid=a_uid)
        assert_code(res['code'])
        assert_body(res['body'], 'success', True, reason_starify(des, res))
        # 1次，A星币退回,2次，A星币冻结
        assert_equal(conMysql.selectUserInfoSql('star_coin', a_uid), default_money - cost0 - cost2)

        # 等30+3s结算
        time.sleep(40)
        # # A星币扣减100%（2次价格）
        # assert_equal(conMysql.selectUserInfoSql('star_coin', a_uid),
        #              default_money - cost0 - cost2 + cost2 * contract_ratio['producer'])
        # C分成10%（2次价格）
        assert_equal(conMysql.selectUserInfoSql('star_coin', c_uid),
                     cost0 * contract_ratio['singer'] + cost2 * contract_ratio['singer'])
        # A分成60%（2次价格）
        assert_equal(conMysql.selectUserInfoSql('star_coin', a_uid),
                     default_money - cost0 - cost2 + cost2 * contract_ratio['producer'])
        # A名额占用
        assert_equal(conMysql.selectProducerSinger(a_uid), 1)
        case_list[des] = result

    def test_contract_002(self, des='新制作人，多次竞拍，新制作人竞拍成功'):
        default_money = 100000
        #  sql:购买者A,a_uid 修改余额=10000
        conMysql.updateMoneySql(a_uid, default_money)
        #  sql:购买者B,b_uid 修改余额=10000
        conMysql.updateMoneySql(b_uid, default_money)
        #  sql:被购买者C,c_uid 修改余额=0
        conMysql.updateMoneySql(c_uid, 0)
        #  sql:购买者A,a_uid 修改财富值=0,控制签约人数=1
        conMysql.updateWealthSql(a_uid, 0)
        #  sql:购买者B,b_uid 修改财富值=0,控制签约人数=1
        conMysql.updateWealthSql(b_uid, 0)
        # sql:清除C的制作人
        conMysql.deleteProducerSinger(c_uid)
        # sql:修改C的身价=100
        conMysql.updateSingerWorth(c_uid, 100)

        # A直接签约C
        cost0 = 200
        time.sleep(0.5)
        data = deal_pay_contract_data("audition_contract", a_uid, cost0, 1)
        res = post_request_session_starify(config.starify_pay_url, data, token_name='starify', uid=a_uid)
        assert_code(res['code'])
        assert_body(res['body'], 'success', True, reason_starify(des, res))
        # A星币扣减100%
        assert_equal(conMysql.selectUserInfoSql('star_coin', a_uid), default_money - cost0)
        # A名额占用
        assert_equal(conMysql.selectProducerSinger(a_uid), 1)
        # C分成10%
        assert_equal(conMysql.selectUserInfoSql('star_coin', c_uid), cost0 * contract_ratio['singer'])

        # B竞价C，第1次报价
        cost1 = 400
        time.sleep(0.5)
        data = deal_pay_contract_data("audition_contract", b_uid, cost1, 0)
        res = post_request_session_starify(config.starify_pay_url, data, token_name='starify', uid=b_uid)
        assert_code(res['code'])
        assert_body(res['body'], 'success', True, reason_starify(des, res))
        # 1次，B星币冻结
        assert_equal(conMysql.selectUserInfoSql('star_coin', b_uid), default_money - cost1)
        # B名额占用
        assert_equal(conMysql.selectProducerSinger(b_uid), 1)

        # B竞价C，第2次报价
        cost2 = 800
        time.sleep(0.5)
        data = deal_pay_contract_data("audition_contract", b_uid, cost2, 0)
        res = post_request_session_starify(config.starify_pay_url, data, token_name='starify', uid=b_uid)
        assert_code(res['code'])
        assert_body(res['body'], 'success', True, reason_starify(des, res))
        # 1次，B星币退回,2次，B星币冻结
        assert_equal(conMysql.selectUserInfoSql('star_coin', b_uid), default_money - cost2)
        # B名额占用
        assert_equal(conMysql.selectProducerSinger(b_uid), 1)

        # 等30+3s结算
        time.sleep(40)
        # B星币扣减100%（2次价格）
        assert_equal(conMysql.selectUserInfoSql('star_coin', b_uid), default_money - cost2)
        # C分成10%（2次价格）
        assert_equal(conMysql.selectUserInfoSql('star_coin', c_uid),
                     cost0 * contract_ratio['singer'] + cost2 * contract_ratio['singer'])
        # A分成60%（2次价格）
        assert_equal(conMysql.selectUserInfoSql('star_coin', a_uid),
                     default_money - cost0 + cost2 * contract_ratio['producer'])
        # A名额释放
        assert_equal(conMysql.selectProducerSinger(a_uid), 0)
        # B名额占用
        assert_equal(conMysql.selectProducerSinger(b_uid), 1)
        case_list[des] = result

    def test_contract_003(self, des='原、新制作人，多次竞拍抬价，原制作人竞拍成功'):
        default_money = 100000
        #  sql:购买者A,a_uid 修改余额=10000
        conMysql.updateMoneySql(a_uid, default_money)
        #  sql:购买者B,b_uid 修改余额=10000
        conMysql.updateMoneySql(b_uid, default_money)
        #  sql:被购买者C,c_uid 修改余额=0
        conMysql.updateMoneySql(c_uid, 0)
        #  sql:购买者A,a_uid 修改财富值=0,控制签约人数=1
        conMysql.updateWealthSql(a_uid, 0)
        #  sql:购买者B,b_uid 修改财富值=0,控制签约人数=1
        conMysql.updateWealthSql(b_uid, 0)
        # sql:清除C的制作人
        conMysql.deleteProducerSinger(c_uid)
        # sql:修改C的身价=100
        conMysql.updateSingerWorth(c_uid, 100)

        # A直接签约C
        cost0 = 200
        time.sleep(0.5)
        data = deal_pay_contract_data("audition_contract", a_uid, cost0, 1)
        res = post_request_session_starify(config.starify_pay_url, data, token_name='starify', uid=a_uid)
        assert_code(res['code'])
        assert_body(res['body'], 'success', True, reason_starify(des, res))
        # A星币扣减100%
        assert_equal(conMysql.selectUserInfoSql('star_coin', a_uid), default_money - cost0)
        # A名额占用
        assert_equal(conMysql.selectProducerSinger(a_uid), 1)
        # C分成10%
        assert_equal(conMysql.selectUserInfoSql('star_coin', c_uid), cost0 * contract_ratio['singer'])

        # B竞价C，第1次报价
        cost1 = 400
        time.sleep(0.5)
        data = deal_pay_contract_data("audition_contract", b_uid, cost1, 0)
        res = post_request_session_starify(config.starify_pay_url, data, token_name='starify', uid=b_uid)
        assert_code(res['code'])
        assert_body(res['body'], 'success', True, reason_starify(des, res))
        # 1次，B星币冻结
        assert_equal(conMysql.selectUserInfoSql('star_coin', b_uid), default_money - cost1)
        # B名额占用
        assert_equal(conMysql.selectProducerSinger(b_uid), 1)

        # A竞价C，第2次报价
        cost2 = 800
        time.sleep(0.5)
        data = deal_pay_contract_data("audition_contract", a_uid, cost2, 0)
        res = post_request_session_starify(config.starify_pay_url, data, token_name='starify', uid=a_uid)
        assert_code(res['code'])
        assert_body(res['body'], 'success', True, reason_starify(des, res))
        # 1次，B星币退回
        assert_equal(conMysql.selectUserInfoSql('star_coin', b_uid), default_money)
        # B名额释放
        assert_equal(conMysql.selectProducerSinger(b_uid), 0)
        # 2次，A星币冻结
        assert_equal(conMysql.selectUserInfoSql('star_coin', a_uid), default_money - cost0 - cost2)

        # B竞价C，第3次报价
        cost3 = 1600
        time.sleep(0.5)
        data = deal_pay_contract_data("audition_contract", b_uid, cost3, 0)
        res = post_request_session_starify(config.starify_pay_url, data, token_name='starify', uid=b_uid)
        assert_code(res['code'])
        assert_body(res['body'], 'success', True, reason_starify(des, res))
        # 3次，B星币冻结
        assert_equal(conMysql.selectUserInfoSql('star_coin', b_uid), default_money - cost3)
        # B名额占用
        assert_equal(conMysql.selectProducerSinger(b_uid), 1)
        # 2次，A星币退回
        assert_equal(conMysql.selectUserInfoSql('star_coin', a_uid), default_money - cost0)

        # A竞价C，第4次报价
        cost4 = 3200
        time.sleep(0.5)
        data = deal_pay_contract_data("audition_contract", a_uid, cost4, 0)
        res = post_request_session_starify(config.starify_pay_url, data, token_name='starify', uid=a_uid)
        assert_code(res['code'])
        assert_body(res['body'], 'success', True, reason_starify(des, res))
        # 3次，B星币退回
        assert_equal(conMysql.selectUserInfoSql('star_coin', b_uid), default_money)
        # B名额释放
        assert_equal(conMysql.selectProducerSinger(b_uid), 0)
        # 4次，A星币冻结
        assert_equal(conMysql.selectUserInfoSql('star_coin', a_uid), default_money - cost0 - cost4)

        # 等30+3s结算
        time.sleep(40)
        # # A星币扣减100%（4次价格）
        # assert_equal(conMysql.selectUserInfoSql('star_coin', a_uid), default_money - cost0 - cost4)
        # C分成10%（4次价格）
        assert_equal(conMysql.selectUserInfoSql('star_coin', c_uid),
                     cost0 * contract_ratio['singer'] + cost4 * contract_ratio['singer'])
        # A分成60%（4次价格）
        assert_equal(conMysql.selectUserInfoSql('star_coin', a_uid),
                     default_money - cost0 - cost4 + cost4 * contract_ratio['producer'])
        # A名额占用
        assert_equal(conMysql.selectProducerSinger(a_uid), 1)
        # B名额释放
        assert_equal(conMysql.selectProducerSinger(b_uid), 0)
        # B星币不扣减
        assert_equal(conMysql.selectUserInfoSql('star_coin', b_uid), default_money)
        case_list[des] = result

    def test_contract_004(self, des='原、新制作人，多次竞拍抬价，新制作人竞拍成功'):
        default_money = 100000
        #  sql:购买者A,a_uid 修改余额=10000
        conMysql.updateMoneySql(a_uid, default_money)
        #  sql:购买者B,b_uid 修改余额=10000
        conMysql.updateMoneySql(b_uid, default_money)
        #  sql:被购买者C,c_uid 修改余额=0
        conMysql.updateMoneySql(c_uid, 0)
        #  sql:购买者A,a_uid 修改财富值=0,控制签约人数=1
        conMysql.updateWealthSql(a_uid, 0)
        #  sql:购买者B,b_uid 修改财富值=0,控制签约人数=1
        conMysql.updateWealthSql(b_uid, 0)
        # sql:清除C的制作人
        conMysql.deleteProducerSinger(c_uid)
        # sql:修改C的身价=100
        conMysql.updateSingerWorth(c_uid, 100)

        # A直接签约C
        cost0 = 200
        time.sleep(0.5)
        data = deal_pay_contract_data("audition_contract", a_uid, cost0, 1)
        res = post_request_session_starify(config.starify_pay_url, data, token_name='starify', uid=a_uid)
        assert_code(res['code'])
        assert_body(res['body'], 'success', True, reason_starify(des, res))
        # A星币扣减100%
        assert_equal(conMysql.selectUserInfoSql('star_coin', a_uid), default_money - cost0)
        # A名额占用
        assert_equal(conMysql.selectProducerSinger(a_uid), 1)
        # C分成10%
        assert_equal(conMysql.selectUserInfoSql('star_coin', c_uid), cost0 * contract_ratio['singer'])

        # A竞价C，第1次报价
        cost1 = 400
        time.sleep(0.5)
        data = deal_pay_contract_data("audition_contract", a_uid, cost1, 0)
        res = post_request_session_starify(config.starify_pay_url, data, token_name='starify', uid=a_uid)
        assert_code(res['code'])
        assert_body(res['body'], 'success', True, reason_starify(des, res))
        # 1次，A星币冻结
        assert_equal(conMysql.selectUserInfoSql('star_coin', a_uid), default_money - cost0 - cost1)

        # B竞价C，第2次报价
        cost2 = 800
        time.sleep(0.5)
        data = deal_pay_contract_data("audition_contract", b_uid, cost2, 0)
        res = post_request_session_starify(config.starify_pay_url, data, token_name='starify', uid=b_uid)
        assert_code(res['code'])
        assert_body(res['body'], 'success', True, reason_starify(des, res))
        # 1次，A星币退回
        assert_equal(conMysql.selectUserInfoSql('star_coin', a_uid), default_money - cost0)
        # 2次，B星币冻结
        assert_equal(conMysql.selectUserInfoSql('star_coin', b_uid), default_money - cost2)
        # B名额占用
        assert_equal(conMysql.selectProducerSinger(b_uid), 1)


        # A竞价C，第3次报价
        cost3 = 1600
        time.sleep(0.5)
        data = deal_pay_contract_data("audition_contract", a_uid, cost3, 0)
        res = post_request_session_starify(config.starify_pay_url, data, token_name='starify', uid=a_uid)
        assert_code(res['code'])
        assert_body(res['body'], 'success', True, reason_starify(des, res))
        # 3次，A星币冻结
        assert_equal(conMysql.selectUserInfoSql('star_coin', a_uid), default_money - cost0 - cost3)
        # 2次，B星币退回
        assert_equal(conMysql.selectUserInfoSql('star_coin', b_uid), default_money)
        # B名额释放
        assert_equal(conMysql.selectProducerSinger(b_uid), 0)

        # B竞价C，第4次报价
        cost4 = 3200
        time.sleep(0.5)
        data = deal_pay_contract_data("audition_contract", b_uid, cost4, 0)
        res = post_request_session_starify(config.starify_pay_url, data, token_name='starify', uid=b_uid)
        assert_code(res['code'])
        assert_body(res['body'], 'success', True, reason_starify(des, res))
        # 3次，A星币退回
        assert_equal(conMysql.selectUserInfoSql('star_coin', a_uid), default_money - cost0)
        # 4次，B星币冻结
        assert_equal(conMysql.selectUserInfoSql('star_coin', b_uid), default_money - cost4)
        # B名额冻结
        assert_equal(conMysql.selectProducerSinger(b_uid), 1)

        # 等30+3s结算
        time.sleep(40)
        # B星币扣减100%（4次价格）
        assert_equal(conMysql.selectUserInfoSql('star_coin', b_uid), default_money - cost4)
        # C分成10%（4次价格）
        assert_equal(conMysql.selectUserInfoSql('star_coin', c_uid),
                     cost0 * contract_ratio['singer'] + cost4 * contract_ratio['singer'])
        # A分成60%（4次价格）
        assert_equal(conMysql.selectUserInfoSql('star_coin', a_uid),
                     default_money - cost0 + cost4 * contract_ratio['producer'])
        # A名额释放
        assert_equal(conMysql.selectProducerSinger(a_uid), 0)
        # B名额占用
        assert_equal(conMysql.selectProducerSinger(b_uid), 1)
        case_list[des] = result

    def test_contract_005(self, des='C无最新报价，A直接签约C，A报价<C身价*1.5'):
        default_money = 100000
        #  sql:购买者A,a_uid 修改余额=10000
        conMysql.updateMoneySql(a_uid, default_money)
        #  sql:购买者B,b_uid 修改余额=10000
        conMysql.updateMoneySql(b_uid, default_money)
        #  sql:被购买者C,c_uid 修改余额=0
        conMysql.updateMoneySql(c_uid, 0)
        #  sql:购买者A,a_uid 修改财富值=0,控制签约人数=1
        conMysql.updateWealthSql(a_uid, 0)
        #  sql:购买者B,b_uid 修改财富值=0,控制签约人数=1
        conMysql.updateWealthSql(b_uid, 0)
        # sql:清除C的制作人
        conMysql.deleteProducerSinger(c_uid)
        # sql:修改C的身价=100
        conMysql.updateSingerWorth(c_uid, 100)

        # A竞价C,报价=身价*1.5-1
        cost0 = 149
        data = deal_pay_contract_data("audition_contract", a_uid, cost0, 1)
        res = post_request_session_starify(config.starify_pay_url, data, token_name='starify', uid=a_uid)
        assert_code(res['code'])
        assert_body(res['body'], 'msg', "出价不满足要求", reason_starify(des, res))

        case_list[des] = result

    def test_contract_006(self, des='C有最新报价(A报价)，B报价<A的最新出价+50'):
        default_money = 100000
        #  sql:购买者A,a_uid 修改余额=10000
        conMysql.updateMoneySql(a_uid, default_money)
        #  sql:购买者B,b_uid 修改余额=10000
        conMysql.updateMoneySql(b_uid, default_money)
        #  sql:被购买者C,c_uid 修改余额=0
        conMysql.updateMoneySql(c_uid, 0)
        #  sql:购买者A,a_uid 修改财富值=0,控制签约人数=1
        conMysql.updateWealthSql(a_uid, 0)
        #  sql:购买者B,b_uid 修改财富值=0,控制签约人数=1
        conMysql.updateWealthSql(b_uid, 0)
        # sql:清除C的制作人
        conMysql.deleteProducerSinger(c_uid)
        # sql:修改C的身价=100
        conMysql.updateSingerWorth(c_uid, 100)

        # A直接签约C
        cost0 = 200
        time.sleep(0.5)
        data = deal_pay_contract_data("audition_contract", a_uid, cost0, 1)
        res = post_request_session_starify(config.starify_pay_url, data, token_name='starify', uid=a_uid)
        assert_code(res['code'])
        assert_body(res['body'], 'success', True, reason_starify(des, res))

        # B竞价C,报价=A身价*1.5，产生最新报价
        cost1 = 200 * 1.5
        time.sleep(0.5)
        data = deal_pay_contract_data("audition_contract", b_uid, cost1, 0)
        res = post_request_session_starify(config.starify_pay_url, data, token_name='starify', uid=b_uid)
        assert_code(res['code'])
        assert_body(res['body'], 'success', True, reason_starify(des, res))

        # B竞价C,报价=A身价*1.5+50-1
        cost2 = 200 * 1.5 + 50 - 1
        time.sleep(0.5)
        data = deal_pay_contract_data("audition_contract", b_uid, cost2, 0)
        res = post_request_session_starify(config.starify_pay_url, data, token_name='starify', uid=b_uid)
        assert_code(res['code'])
        assert_body(res['body'], 'msg', "出价不满足要求", reason_starify(des, res))
        time.sleep(40)  # 等待结算,以免影响其他case
        case_list[des] = result

    def test_contract_007(self, des='A报价>A的余额，星币余额不足'):
        default_money = 100000
        #  sql:购买者A,a_uid 修改余额=10000
        conMysql.updateMoneySql(a_uid, default_money)
        #  sql:购买者B,b_uid 修改余额=10000
        conMysql.updateMoneySql(b_uid, default_money)
        #  sql:被购买者C,c_uid 修改余额=0
        conMysql.updateMoneySql(c_uid, 0)
        #  sql:购买者A,a_uid 修改财富值=0,控制签约人数=1
        conMysql.updateWealthSql(a_uid, 0)
        #  sql:购买者B,b_uid 修改财富值=0,控制签约人数=1
        conMysql.updateWealthSql(b_uid, 0)
        # sql:清除C的制作人
        conMysql.deleteProducerSinger(c_uid)
        # sql:修改C的身价=100
        conMysql.updateSingerWorth(c_uid, 100)

        # A直接签约C，A报价>A的余额
        cost0 = default_money + 1
        data = deal_pay_contract_data("audition_contract", a_uid, cost0, 1)
        res = post_request_session_starify(config.starify_pay_url, data, token_name='starify', uid=a_uid)
        assert_code(res['code'])
        assert_body(res['body'], 'msg', "余额不足", reason_starify(des, res))
        case_list[des] = result

    def test_contract_008(self, des='可签约的歌手数量余额不足'):
        default_money = 100000
        #  sql:购买者A,a_uid 修改余额=10000
        conMysql.updateMoneySql(a_uid, default_money)
        #  sql:购买者B,b_uid 修改余额=10000
        conMysql.updateMoneySql(b_uid, default_money)
        #  sql:被购买者C,c_uid 修改余额=0
        conMysql.updateMoneySql(c_uid, 0)
        #  sql:购买者A,a_uid 修改财富值=0,控制签约人数=1
        conMysql.updateWealthSql(a_uid, 0)
        #  sql:购买者B,b_uid 修改财富值=0,控制签约人数=1
        conMysql.updateWealthSql(b_uid, 0)
        # sql:清除C的制作人
        conMysql.deleteProducerSinger(c_uid)
        # sql:清除B的制作人
        conMysql.deleteProducerSinger(b_uid)
        # sql:修改C的身价=100
        conMysql.updateSingerWorth(c_uid, 100)
        # sql:修改B的身价=100
        conMysql.updateSingerWorth(b_uid, 100)

        # A直接签约C
        cost0 = 200
        time.sleep(0.5)
        data = deal_pay_contract_data("audition_contract", a_uid, cost0, 1)
        res = post_request_session_starify(config.starify_pay_url, data, token_name='starify', uid=a_uid)
        assert_code(res['code'])
        assert_body(res['body'], 'success', True, reason_starify(des, res))

        # 再次直接，A直接签约B,提示名额不足
        cost1 = 400
        time.sleep(0.5)
        data = deal_pay_contract_data("audition_contract", a_uid, cost1, 0, singer_uid=b_uid)
        res = post_request_session_starify(config.starify_pay_url, data, token_name='starify', uid=a_uid)
        assert_code(res['code'])
        assert_body(res['body'], 'msg', '可签约的歌手数量余额不足', reason_starify(des, res))
        case_list[des] = result
