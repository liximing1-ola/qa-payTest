import math
import unittest

from caseStarify.deal_data import deal_pay_data
from caseStarify.need_data import *
from caseStarify.tools import deal_num
from common.Assert import *
from common.Consts import case_list, result
# from common.method import reason
from common.Request import post_request_session_starify
from common.conStarifyMysql import conMysql
from common.method import reason_starify
from common.runFailed import Retry


@Retry(max_n=1)
class TestPayCreate(unittest.TestCase):
    def test_contract_001(self, des='原制作人续约，多次竞拍抬价，原制作人竞拍成功'):
        default_money = 100000
        #  sql:购买者A,starify_rewardUid01 修改余额=10000
        conMysql.updateMoneySql(starify_rewardUid01, default_money)
        #  sql:购买者B,starify_rewardUid02 修改余额=10000
        conMysql.updateMoneySql(starify_rewardUid02, default_money)
        #  sql:被购买者C,starify_payUid 修改余额=0
        conMysql.updateMoneySql(starify_payUid, 0)

        # sql:清除C的制作人 todo
        # sql:修改C的身价=100 todo

        # A直接签约C
        cost0 = 200
        data = deal_pay_data("params_contract", starify_rewardUid01, cost0, 1)
        res = post_request_session_starify(config.starify_pay_url, data, tokenName='starify')
        assert_code(res['code'])
        assert_body(res['body'], 'success', True, reason_starify(des, res))
        # A星币扣减100%
        assert_equal(conMysql.selectUserInfoSql('star_coin', starify_rewardUid01), default_money - cost0)
        # A名额占用 todo
        # C分成10%
        assert_equal(conMysql.selectUserInfoSql('star_coin', starify_payUid), cost0 * 0.1)

        # A续约C，第1次报价
        cost1 = 400
        data = deal_pay_data("params_contract", starify_rewardUid01, cost1, 0)
        res = post_request_session_starify(config.starify_pay_url, data, tokenName='starify')
        assert_code(res['code'])
        assert_body(res['body'], 'success', True, reason_starify(des, res))
        # 1次，A星币冻结
        assert_equal(conMysql.selectUserInfoSql('star_coin', starify_rewardUid01), default_money - cost0 - cost1)

        # A续约C，第2次报价
        cost2 = 800
        data = deal_pay_data("params_contract", starify_rewardUid01, cost2, 0)
        res = post_request_session_starify(config.starify_pay_url, data, tokenName='starify')
        assert_code(res['code'])
        assert_body(res['body'], 'success', True, reason_starify(des, res))
        # 1次，A星币退回,2次，A星币冻结
        assert_equal(conMysql.selectUserInfoSql('star_coin', starify_rewardUid01), default_money - cost0 - cost2)

        # 等30+3s结算
        time.sleep(33)
        # A星币扣减100%（2次价格）
        assert_equal(conMysql.selectUserInfoSql('star_coin', starify_rewardUid01), default_money - cost0 - cost2)
        # C分成10%（2次价格）
        assert_equal(conMysql.selectUserInfoSql('star_coin', starify_payUid), cost0 * 0.1 + cost2 * 0.1)
        # A分成60%（2次价格）
        assert_equal(conMysql.selectUserInfoSql('star_coin', starify_payUid),
                     default_money - cost0 - cost2 + cost2 * 0.6)
        # A名额占用 todo
        case_list[des] = result

    def test_contract_002(self, des='新制作人，多次竞拍，新制作人竞拍成功'):
        default_money = 100000
        #  sql:购买者A,starify_rewardUid01 修改余额=10000
        conMysql.updateMoneySql(starify_rewardUid01, default_money)
        #  sql:购买者B,starify_rewardUid02 修改余额=10000
        conMysql.updateMoneySql(starify_rewardUid02, default_money)
        #  sql:被购买者C,starify_payUid 修改余额=0
        conMysql.updateMoneySql(starify_payUid, 0)

        # sql:清除C的制作人 todo
        # sql:修改C的身价=100 todo

        # A直接签约C
        cost0 = 200
        data = deal_pay_data("params_contract", starify_rewardUid01, cost0, 1)
        res = post_request_session_starify(config.starify_pay_url, data, tokenName='starify')
        assert_code(res['code'])
        assert_body(res['body'], 'success', True, reason_starify(des, res))
        # A星币扣减100%
        assert_equal(conMysql.selectUserInfoSql('star_coin', starify_rewardUid01), default_money - cost0)
        # A名额占用 todo
        # C分成10%
        assert_equal(conMysql.selectUserInfoSql('star_coin', starify_payUid), cost0 * 0.1)

        # B竞价C，第1次报价
        cost1 = 400
        data = deal_pay_data("params_contract", starify_rewardUid02, cost1, 0)
        res = post_request_session_starify(config.starify_pay_url, data, tokenName='starify')
        assert_code(res['code'])
        assert_body(res['body'], 'success', True, reason_starify(des, res))
        # 1次，B星币冻结
        assert_equal(conMysql.selectUserInfoSql('star_coin', starify_rewardUid02), default_money - cost1)
        # B名额占用 todo

        # B竞价C，第2次报价
        cost2 = 800
        data = deal_pay_data("params_contract", starify_rewardUid02, cost2, 0)
        res = post_request_session_starify(config.starify_pay_url, data, tokenName='starify')
        assert_code(res['code'])
        assert_body(res['body'], 'success', True, reason_starify(des, res))
        # 1次，B星币退回,2次，B星币冻结
        assert_equal(conMysql.selectUserInfoSql('star_coin', starify_rewardUid02), default_money - cost2)
        # B名额占用 todo

        # 等30+3s结算
        time.sleep(33)
        # B星币扣减100%（2次价格）
        assert_equal(conMysql.selectUserInfoSql('star_coin', starify_rewardUid01), default_money - cost2)
        # C分成10%（2次价格）
        assert_equal(conMysql.selectUserInfoSql('star_coin', starify_payUid), cost0 * 0.1 + cost2 * 0.1)
        # A分成60%（2次价格）
        assert_equal(conMysql.selectUserInfoSql('star_coin', starify_payUid),
                     default_money - cost0 + cost2 * 0.6)
        # A名额释放 todo
        # B名额占用 todo
        case_list[des] = result
