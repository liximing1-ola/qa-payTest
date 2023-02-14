import time

from common.Config import config
from common.conPtMysql import conMysql
from common.Request import post_request_session
import unittest
from common.Assert import assert_code, assert_equal, assert_body
from common.method import reason
from common.basicData import encodePtData
from common.Consts import case_list, result
from common.runFailed import Retry


@Retry(max_n=3, func_prefix='test_01_payRoomgiftVip')
class TestPayCreate(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        conMysql.checkXsGiftConfig()

    def test_01_payRoomgiftVip(self, des='房间打赏礼物校验人气值&自身的vip等级'):
        """
        用例描述：
        验证房间打赏赠送600分=60钻
        脚本步骤：
        1.构造用户数据
        2.房间内A打赏B礼物，礼物价值60钻石
        3.校验接口状态和返回值数据
        4.检查A账户VIP等级数据：pay_room_money数据需要新增 600 有显示逻辑，显示取1%
        5.检查B账户数据库人气增加值：人气值需要增加数值: 600
        备注：A、B需要无贵族爵位关系等加速升级逻辑,vip值xs_user_profile,人气值xs_user_popularity
        """
        conMysql.updateMoneySql(config.pt_payUid, money=600)
        conMysql.updateXsUserprofile_pay_room_money(config.pt_payUid)
        conMysql.updateXsUserpopularity(config.pt_testUid)
        data = encodePtData(payType='package')
        res = post_request_session(config.pt_pay_url, data, tokenName='pt')
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.pt_payUid), 0)
        assert_equal(conMysql.sqlXsUserprofile_pay_room_money(config.pt_payUid), 600)
        time.sleep(2)  # 人气值需要task更新处理
        assert_equal(conMysql.sqlXsUserpopularity(config.pt_testUid), 600)
        case_list[des] = result

    def test_02_payChatgiftVip(self, des='私聊打赏礼物校验人气值&自身的vip等级'):
        """
        用例描述：
        验证私聊打赏赠送600分=60钻
        脚本步骤：
        1.构造用户数据
        2.私聊界面内A打赏B礼物，礼物价值60钻石
        3.校验接口状态和返回值数据
        4.检查B账户数据库人气增加值：人气值需要增加数值: 600
        5.检查A账户VIP等级数据：pay_room_money数据需要新增 600 有显示逻辑，显示取1%
        备注：A、B需要无贵族爵位关系等加速升级逻辑,vip值xs_user_profile,人气值xs_user_popularity
        """
        conMysql.updateMoneySql(config.pt_payUid, money=600)
        conMysql.updateXsUserprofile_pay_room_money(config.pt_payUid)
        conMysql.updateXsUserpopularity(config.pt_testUid)
        data = encodePtData(payType='chat-gift')
        res = post_request_session(config.pt_pay_url, data, tokenName='pt')
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.pt_payUid), 0)
        assert_equal(conMysql.sqlXsUserprofile_pay_room_money(config.pt_payUid), 600)
        time.sleep(2)  # 人气值需要task更新处理
        assert_equal(conMysql.sqlXsUserpopularity(config.pt_testUid), 600)
        case_list[des] = result
