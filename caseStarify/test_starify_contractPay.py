import time
import unittest

from caseStarify.deal_data import deal_pay_contract_data
from caseStarify.need_data import a_uid, b_uid, c_uid, contract_ratio
from common.Assert import assert_body, assert_code, assert_equal
from common.Consts import case_list, result
from common.Request import post_starify
from common.conStarifyMysql import conMysql
from common.method import format_reason
from common.runFailed import Retry


@Retry(max_n=1)
class TestPayCreate(unittest.TestCase):
    DEFAULT_MONEY = 100000

    def _contract_setUp(self, clear_b=False):
        """竞拍类用例的公共数据准备"""
        conMysql.updateMoneySql(a_uid, self.DEFAULT_MONEY)
        conMysql.updateMoneySql(b_uid, self.DEFAULT_MONEY)
        conMysql.updateMoneySql(c_uid, 0)
        conMysql.updateWealthSql(a_uid, 0)
        conMysql.updateWealthSql(b_uid, 0)
        conMysql.deleteProducerSinger(c_uid)
        conMysql.updateSingerWorth(c_uid, 100)
        if clear_b:
            conMysql.deleteProducerSinger(b_uid)
            conMysql.updateSingerWorth(b_uid, 100)

    # ---- 竞拍操作 helpers ----

    def _direct_sign(self, uid, cost, des, singer_uid=c_uid, sleep=True):
        """直接签约并断言成功"""
        if sleep:
            time.sleep(0.5)
        data = deal_pay_contract_data("audition_contract", uid, cost, 1, singer_uid=singer_uid)
        res = post_starify(data, uid=uid)
        assert_code(res['code'])
        assert_body(res['body'], 'success', True, format_reason(des, res, slp=True))

    def _bid(self, uid, cost, des):
        """竞价并断言成功"""
        time.sleep(0.5)
        data = deal_pay_contract_data("audition_contract", uid, cost, 0)
        res = post_starify(data, uid=uid)
        assert_code(res['code'])
        assert_body(res['body'], 'success', True, format_reason(des, res, slp=True))

    def _bid_fail(self, uid, cost, msg, des, sign_type=1, singer_uid=c_uid, sleep=True):
        """竞拍并断言失败"""
        if sleep:
            time.sleep(0.5)
        data = deal_pay_contract_data("audition_contract", uid, cost, sign_type, singer_uid=singer_uid)
        res = post_starify(data, uid=uid)
        assert_code(res['code'])
        assert_body(res['body'], 'msg', msg, format_reason(des, res, slp=True))

    # ---- 断言 helpers ----

    def _coin(self, uid, expected):
        """断言星币余额"""
        assert_equal(conMysql.selectUserInfoSql('star_coin', uid), expected)

    def _quota(self, uid, expected):
        """断言名额"""
        assert_equal(conMysql.selectProducerSinger(uid), expected)

    def _settle(self):
        """等待结算"""
        time.sleep(40)

    # ---- 测试用例 ----

    def test_contract_001(self, des='原制作人续约，多次竞拍抬价，原制作人竞拍成功'):
        m = self.DEFAULT_MONEY
        self._contract_setUp()

        cost0 = 200
        self._direct_sign(a_uid, cost0, des)
        self._coin(a_uid, m - cost0)
        self._quota(a_uid, 1)
        self._coin(c_uid, cost0 * contract_ratio['singer'])

        cost1 = 400
        self._bid(a_uid, cost1, des)
        self._coin(a_uid, m - cost0 - cost1)

        cost2 = 800
        self._bid(a_uid, cost2, des)
        self._coin(a_uid, m - cost0 - cost2)

        self._settle()
        self._coin(c_uid, (cost0 + cost2) * contract_ratio['singer'])
        self._coin(a_uid, m - cost0 - cost2 + cost2 * contract_ratio['producer'])
        self._quota(a_uid, 1)
        case_list[des] = result

    def test_contract_002(self, des='新制作人，多次竞拍，新制作人竞拍成功'):
        m = self.DEFAULT_MONEY
        self._contract_setUp()

        cost0 = 200
        self._direct_sign(a_uid, cost0, des)
        self._coin(a_uid, m - cost0)
        self._quota(a_uid, 1)
        self._coin(c_uid, cost0 * contract_ratio['singer'])

        cost1 = 400
        self._bid(b_uid, cost1, des)
        self._coin(b_uid, m - cost1)
        self._quota(b_uid, 1)

        cost2 = 800
        self._bid(b_uid, cost2, des)
        self._coin(b_uid, m - cost2)
        self._quota(b_uid, 1)

        self._settle()
        self._coin(b_uid, m - cost2)
        self._coin(c_uid, (cost0 + cost2) * contract_ratio['singer'])
        self._coin(a_uid, m - cost0 + cost2 * contract_ratio['producer'])
        self._quota(a_uid, 0)
        self._quota(b_uid, 1)
        case_list[des] = result

    def test_contract_003(self, des='原、新制作人，多次竞拍抬价，原制作人竞拍成功'):
        m = self.DEFAULT_MONEY
        self._contract_setUp()

        cost0 = 200
        self._direct_sign(a_uid, cost0, des)
        self._coin(a_uid, m - cost0)
        self._quota(a_uid, 1)
        self._coin(c_uid, cost0 * contract_ratio['singer'])

        cost1 = 400
        self._bid(b_uid, cost1, des)
        self._coin(b_uid, m - cost1)
        self._quota(b_uid, 1)

        cost2 = 800
        self._bid(a_uid, cost2, des)
        self._coin(b_uid, m)
        self._quota(b_uid, 0)
        self._coin(a_uid, m - cost0 - cost2)

        cost3 = 1600
        self._bid(b_uid, cost3, des)
        self._coin(b_uid, m - cost3)
        self._quota(b_uid, 1)
        self._coin(a_uid, m - cost0)

        cost4 = 3200
        self._bid(a_uid, cost4, des)
        self._coin(b_uid, m)
        self._quota(b_uid, 0)
        self._coin(a_uid, m - cost0 - cost4)

        self._settle()
        self._coin(c_uid, (cost0 + cost4) * contract_ratio['singer'])
        self._coin(a_uid, m - cost0 - cost4 + cost4 * contract_ratio['producer'])
        self._quota(a_uid, 1)
        self._quota(b_uid, 0)
        self._coin(b_uid, m)
        case_list[des] = result

    def test_contract_004(self, des='原、新制作人，多次竞拍抬价，新制作人竞拍成功'):
        m = self.DEFAULT_MONEY
        self._contract_setUp()

        cost0 = 200
        self._direct_sign(a_uid, cost0, des)
        self._coin(a_uid, m - cost0)
        self._quota(a_uid, 1)
        self._coin(c_uid, cost0 * contract_ratio['singer'])

        cost1 = 400
        self._bid(a_uid, cost1, des)
        self._coin(a_uid, m - cost0 - cost1)

        cost2 = 800
        self._bid(b_uid, cost2, des)
        self._coin(a_uid, m - cost0)
        self._coin(b_uid, m - cost2)
        self._quota(b_uid, 1)

        cost3 = 1600
        self._bid(a_uid, cost3, des)
        self._coin(a_uid, m - cost0 - cost3)
        self._coin(b_uid, m)
        self._quota(b_uid, 0)

        cost4 = 3200
        self._bid(b_uid, cost4, des)
        self._coin(a_uid, m - cost0)
        self._coin(b_uid, m - cost4)
        self._quota(b_uid, 1)

        self._settle()
        self._coin(b_uid, m - cost4)
        self._coin(c_uid, (cost0 + cost4) * contract_ratio['singer'])
        self._coin(a_uid, m - cost0 + cost4 * contract_ratio['producer'])
        self._quota(a_uid, 0)
        self._quota(b_uid, 1)
        case_list[des] = result

    def test_contract_005(self, des='C无最新报价，A直接签约C，A报价<C身价*1.5'):
        self._contract_setUp()
        self._bid_fail(a_uid, 149, "出价不满足要求", des, sleep=False)
        case_list[des] = result

    def test_contract_006(self, des='C有最新报价(A报价)，B报价<A的最新出价+50'):
        self._contract_setUp()

        cost0 = 200
        self._direct_sign(a_uid, cost0, des)

        # B竞价C, 报价=A身价*1.5, 产生最新报价
        cost1 = 200 * 1.5
        self._bid(b_uid, cost1, des)

        # B竞价C, 报价=A身价*1.5+50-1
        cost2 = 200 * 1.5 + 50 - 1
        self._bid_fail(b_uid, cost2, "出价不满足要求", des, sign_type=0)
        self._settle()  # 等待结算,以免影响其他case
        case_list[des] = result

    def test_contract_007(self, des='A报价>A的余额，星币余额不足'):
        self._contract_setUp()
        self._bid_fail(a_uid, self.DEFAULT_MONEY + 1, "余额不足", des, sleep=False)
        case_list[des] = result

    def test_contract_008(self, des='可签约的歌手数量余额不足'):
        self._contract_setUp(clear_b=True)

        cost0 = 200
        self._direct_sign(a_uid, cost0, des)

        # 再次直接, A签约B, 提示名额不足
        cost1 = 400
        self._bid_fail(a_uid, cost1, '可签约的歌手数量余额不足', des, sign_type=0, singer_uid=b_uid)
        case_list[des] = result
import time
import unittest

from caseStarify.deal_data import deal_pay_contract_data
from caseStarify.need_data import a_uid, b_uid, c_uid, contract_ratio
from common.Assert import assert_body, assert_code, assert_equal
from common.Consts import case_list, result
from common.Request import post_starify
from common.conStarifyMysql import conMysql
from common.method import format_reason
from common.runFailed import Retry


@Retry(max_n=1)
class TestPayCreate(unittest.TestCase):
    DEFAULT_MONEY = 100000

    def _contract_setUp(self, clear_b=False):
        """竞拍类用例的公共数据准备"""
        conMysql.updateMoneySql(a_uid, self.DEFAULT_MONEY)
        conMysql.updateMoneySql(b_uid, self.DEFAULT_MONEY)
        conMysql.updateMoneySql(c_uid, 0)
        conMysql.updateWealthSql(a_uid, 0)
        conMysql.updateWealthSql(b_uid, 0)
        conMysql.deleteProducerSinger(c_uid)
        conMysql.updateSingerWorth(c_uid, 100)
        if clear_b:
            conMysql.deleteProducerSinger(b_uid)
            conMysql.updateSingerWorth(b_uid, 100)

    def test_contract_001(self, des='原制作人续约，多次竞拍抬价，原制作人竞拍成功'):
        default_money = self.DEFAULT_MONEY
        self._contract_setUp()

        # A直接签约C
        cost0 = 200
        time.sleep(0.5)
        data = deal_pay_contract_data("audition_contract", a_uid, cost0, 1)
        res = post_starify(data, uid=a_uid)
        assert_code(res['code'])
        assert_body(res['body'], 'success', True, format_reason(des, res, slp=True))
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
        res = post_starify(data, uid=a_uid)
        assert_code(res['code'])
        assert_body(res['body'], 'success', True, format_reason(des, res, slp=True))
        # 1次，A星币冻结
        assert_equal(conMysql.selectUserInfoSql('star_coin', a_uid), default_money - cost0 - cost1)

        # A续约C，第2次报价
        cost2 = 800
        time.sleep(0.5)
        data = deal_pay_contract_data("audition_contract", a_uid, cost2, 0)
        res = post_starify(data, uid=a_uid)
        assert_code(res['code'])
        assert_body(res['body'], 'success', True, format_reason(des, res, slp=True))
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
        default_money = self.DEFAULT_MONEY
        self._contract_setUp()

        # A直接签约C
        cost0 = 200
        time.sleep(0.5)
        data = deal_pay_contract_data("audition_contract", a_uid, cost0, 1)
        res = post_starify(data, uid=a_uid)
        assert_code(res['code'])
        assert_body(res['body'], 'success', True, format_reason(des, res, slp=True))
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
        res = post_starify(data, uid=b_uid)
        assert_code(res['code'])
        assert_body(res['body'], 'success', True, format_reason(des, res, slp=True))
        # 1次，B星币冻结
        assert_equal(conMysql.selectUserInfoSql('star_coin', b_uid), default_money - cost1)
        # B名额占用
        assert_equal(conMysql.selectProducerSinger(b_uid), 1)

        # B竞价C，第2次报价
        cost2 = 800
        time.sleep(0.5)
        data = deal_pay_contract_data("audition_contract", b_uid, cost2, 0)
        res = post_starify(data, uid=b_uid)
        assert_code(res['code'])
        assert_body(res['body'], 'success', True, format_reason(des, res, slp=True))
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
        default_money = self.DEFAULT_MONEY
        self._contract_setUp()

        # A直接签约C
        cost0 = 200
        time.sleep(0.5)
        data = deal_pay_contract_data("audition_contract", a_uid, cost0, 1)
        res = post_starify(data, uid=a_uid)
        assert_code(res['code'])
        assert_body(res['body'], 'success', True, format_reason(des, res, slp=True))
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
        res = post_starify(data, uid=b_uid)
        assert_code(res['code'])
        assert_body(res['body'], 'success', True, format_reason(des, res, slp=True))
        # 1次，B星币冻结
        assert_equal(conMysql.selectUserInfoSql('star_coin', b_uid), default_money - cost1)
        # B名额占用
        assert_equal(conMysql.selectProducerSinger(b_uid), 1)

        # A竞价C，第2次报价
        cost2 = 800
        time.sleep(0.5)
        data = deal_pay_contract_data("audition_contract", a_uid, cost2, 0)
        res = post_starify(data, uid=a_uid)
        assert_code(res['code'])
        assert_body(res['body'], 'success', True, format_reason(des, res, slp=True))
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
        res = post_starify(data, uid=b_uid)
        assert_code(res['code'])
        assert_body(res['body'], 'success', True, format_reason(des, res, slp=True))
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
        res = post_starify(data, uid=a_uid)
        assert_code(res['code'])
        assert_body(res['body'], 'success', True, format_reason(des, res, slp=True))
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
        default_money = self.DEFAULT_MONEY
        self._contract_setUp()

        # A直接签约C
        cost0 = 200
        time.sleep(0.5)
        data = deal_pay_contract_data("audition_contract", a_uid, cost0, 1)
        res = post_starify(data, uid=a_uid)
        assert_code(res['code'])
        assert_body(res['body'], 'success', True, format_reason(des, res, slp=True))
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
        res = post_starify(data, uid=a_uid)
        assert_code(res['code'])
        assert_body(res['body'], 'success', True, format_reason(des, res, slp=True))
        # 1次，A星币冻结
        assert_equal(conMysql.selectUserInfoSql('star_coin', a_uid), default_money - cost0 - cost1)

        # B竞价C，第2次报价
        cost2 = 800
        time.sleep(0.5)
        data = deal_pay_contract_data("audition_contract", b_uid, cost2, 0)
        res = post_starify(data, uid=b_uid)
        assert_code(res['code'])
        assert_body(res['body'], 'success', True, format_reason(des, res, slp=True))
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
        res = post_starify(data, uid=a_uid)
        assert_code(res['code'])
        assert_body(res['body'], 'success', True, format_reason(des, res, slp=True))
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
        res = post_starify(data, uid=b_uid)
        assert_code(res['code'])
        assert_body(res['body'], 'success', True, format_reason(des, res, slp=True))
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
        default_money = self.DEFAULT_MONEY
        self._contract_setUp()

        # A竞价C,报价=身价*1.5-1
        cost0 = 149
        data = deal_pay_contract_data("audition_contract", a_uid, cost0, 1)
        res = post_starify(data, uid=a_uid)
        assert_code(res['code'])
        assert_body(res['body'], 'msg', "出价不满足要求", format_reason(des, res, slp=True))

        case_list[des] = result

    def test_contract_006(self, des='C有最新报价(A报价)，B报价<A的最新出价+50'):
        default_money = self.DEFAULT_MONEY
        self._contract_setUp()

        # A直接签约C
        cost0 = 200
        time.sleep(0.5)
        data = deal_pay_contract_data("audition_contract", a_uid, cost0, 1)
        res = post_starify(data, uid=a_uid)
        assert_code(res['code'])
        assert_body(res['body'], 'success', True, format_reason(des, res, slp=True))

        # B竞价C,报价=A身价*1.5，产生最新报价
        cost1 = 200 * 1.5
        time.sleep(0.5)
        data = deal_pay_contract_data("audition_contract", b_uid, cost1, 0)
        res = post_starify(data, uid=b_uid)
        assert_code(res['code'])
        assert_body(res['body'], 'success', True, format_reason(des, res, slp=True))

        # B竞价C,报价=A身价*1.5+50-1
        cost2 = 200 * 1.5 + 50 - 1
        time.sleep(0.5)
        data = deal_pay_contract_data("audition_contract", b_uid, cost2, 0)
        res = post_starify(data, uid=b_uid)
        assert_code(res['code'])
        assert_body(res['body'], 'msg', "出价不满足要求", format_reason(des, res, slp=True))
        time.sleep(40)  # 等待结算,以免影响其他case
        case_list[des] = result

    def test_contract_007(self, des='A报价>A的余额，星币余额不足'):
        default_money = self.DEFAULT_MONEY
        self._contract_setUp()

        # A直接签约C，A报价>A的余额
        cost0 = default_money + 1
        data = deal_pay_contract_data("audition_contract", a_uid, cost0, 1)
        res = post_starify(data, uid=a_uid)
        assert_code(res['code'])
        assert_body(res['body'], 'msg', "余额不足", format_reason(des, res, slp=True))
        case_list[des] = result

    def test_contract_008(self, des='可签约的歌手数量余额不足'):
        default_money = self.DEFAULT_MONEY
        self._contract_setUp(clear_b=True)

        # A直接签约C
        cost0 = 200
        time.sleep(0.5)
        data = deal_pay_contract_data("audition_contract", a_uid, cost0, 1)
        res = post_starify(data, uid=a_uid)
        assert_code(res['code'])
        assert_body(res['body'], 'success', True, format_reason(des, res, slp=True))

        # 再次直接，A直接签约B,提示名额不足
        cost1 = 400
        time.sleep(0.5)
        data = deal_pay_contract_data("audition_contract", a_uid, cost1, 0, singer_uid=b_uid)
        res = post_starify(data, uid=a_uid)
        assert_code(res['code'])
        assert_body(res['body'], 'msg', '可签约的歌手数量余额不足', format_reason(des, res, slp=True))
        case_list[des] = result
