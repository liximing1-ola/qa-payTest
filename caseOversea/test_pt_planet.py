from common.Config import config
from common.method import reason
from common.conPtMysql import conMysql
import unittest
from common.Request import post_request_session
from common.Assert import assert_code, assert_body, assert_equal
from common.basicData import encodePtData
from common.Consts import result, case_list
from common.runFailed import Retry
@Retry
class TestPayCreate(unittest.TestCase):

    def test_01_journey_planet(self, des='星球之旅扣钻石获取礼物玩法'):
        """
        用例描述：
        验证钻石扣除正常，调用星球之旅正常，背包正常得到对应礼物
        脚本步骤：
        1.构造数据（更新xs_user_money，清空xs_user_commodity，清空xs_user_journey_planet_draw_record,xs_user_journey_planet_record）
            * 清空用户money数据
            * 清空用户背包内所有物品
            * 清空用户星球之旅玩法数据
            * 修改用户钱包余额 2000
        2.请求星球之旅接口，校验接口状态和返回值数据
        3.检查账户余额，预期值为：2000 - 1500= 500,一轮一关扣款150钻石
        4.检查背包内下发物品，预期值应为1（cid物品得到1个）
        """
        conMysql.deleteUserAccountSql('user_commodity', config.pt_payUid)
        conMysql.deleteUserAccountSql ('user_journey_planet_record', config.pt_payUid)
        conMysql.deleteUserAccountSql ('user_journey_planet_draw_record', config.pt_payUid)
        conMysql.updateMoneySql(config.pt_payUid, money=2000)
        data = encodePtData(payType='journey_planet_draw')
        res = post_request_session(url=config.pt_pay_url, data=data, tokenName='pt')
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.pt_payUid), 500)
        assert_equal(conMysql.selectUserInfoSql('sum_commodity', config.pt_payUid), 1)
        case_list[des] = result

