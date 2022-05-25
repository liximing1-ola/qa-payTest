from common.Config import config
from common.method import reason
from common.conMysql import conMysql
import unittest
from common import Consts, Assert, Request, basicData
from common.runFailed import Retry
@Retry
class TestPayCreate(unittest.TestCase):

    # 内网支付接口
    pay_url = config.dev_host + 'pay/create?package=com.who.android'

    def test_01_gamesRoomPayDivide_55(self):
        """
        用例描述：
        验证桌游房间一对一打赏分成比5:5
        脚本步骤：
        1.构造打赏者和被打赏者数据 （更新xs_user_money）
        2.房间内一对一打赏
        3.校验【status code】和返回值【body】状态
        4.检查打赏者余额，预期：0
        5.检查被打赏者余额,预期：50
        """
        des = '桌游房间1V1打赏分成比5:5'
        conMysql.updateMoneySql(config.games_payUid, 1000)
        conMysql.updateMoneySql(config.games_testUid)
        data = basicData.encodeData(payType='package', money=1000, rid=config.games_rid, uid=config.games_testUid)
        res = Request.post_request_session(url=TestPayCreate.pay_url, data=data, tokenName='games')
        Assert.assert_code(res['code'], 200)
        Assert.assert_body(res['body'], 'success', 1, reason(des, res['body']))
        Assert.assert_equal(conMysql.selectUserInfoSql('sum_money', config.payUid), 0)
        Assert.assert_equal(conMysql.selectUserInfoSql('single_money', config.rewardUid), 500)
        Consts.GAME_LIST[des] = Consts.result