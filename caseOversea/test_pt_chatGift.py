from common.Config import config
from common.conPtMysql import conMysql
from common.Request import pt_post_request_session
import unittest
from common.Assert import assert_code, assert_equal, assert_body
from common.method import reason
from common import basicData
from common.Consts import case_list, result
from common.runFailed import Retry
@Retry(max_n=2)
class TestPayCreate(unittest.TestCase):

    def test_01_IMPayNoMoney(self, des='私聊打赏余额不足的场景'):
        """
        用例描述：
        检查账户余额不足时，私聊一对一打赏
        脚本步骤：
        1.构造打赏者和被打赏者数据
        2.私聊一对一打赏流程(礼物:棒棒糖)
        3.校验接口和返回值数据
        4.检查预期返回msg，预期：支付失败，提示Toast
        5.检查被打赏者余额,预期：0
        """
        conMysql.updateUserMoneyClearSql(config.pt_payUid, config.pt_testUid)
        conMysql.deleteUserAccountSql('broker_user', config.pt_testUid)
        conMysql.deleteUserAccountSql('chatroom', config.pt_testUid)
        data = basicData.encodePtData(payType='chat-gift', uid=config.pt_testUid, giftId=config.pt_giftId['10'], money=600)
        res = pt_post_request_session(config.pay_url, data)
        assert_code(res['code'])
        assert_body(res['body'], 'success', 0, reason(des, res))
        assert_body(res['body'], 'msg', '餘額不足，無法支付', reason(des, res))
        assert_equal(conMysql.selectUserMoneySql('sum_money', config.rewardUid), 0)
        case_list[des] = result

    def test_02_ImPayChangeMoney(self):
        """
        用例描述：
        验证余额足够时，私聊一对一打赏,打赏分成满足师徒收益的基础上为：80:20
        步骤：
        1.清理打赏者和被打赏者数据 （更新xs_user_money）
        2.私聊一对一打赏(余额400分，打赏100分)
        3.校验【status code】和【body】状态
        4.检查被打赏者余额，预期为：80
        5.检查打赏者剩余余额，预期为：300
        """
        pass