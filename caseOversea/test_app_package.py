# coding=utf-8
"""
APP 海外版支付测试 - 房间打赏验证

验证房间场景下的打赏功能，包括余额不足和正常打赏。
"""
from common.Config import config
from common.method import format_reason
from common.conPtMysql import conMysql
from common.Request import post_request_session
from common.Assert import assert_code, assert_body, assert_equal
from common.basicData import encodeOverseaData
from common.Consts import case_list, result
from common.runFailed import Retry
from caseOversea.base import OverseaAreaTestBase


@Retry
class TestPayCreate(OverseaAreaTestBase):
    """APP 房间打赏测试类"""

    bigarea_id = 2
    room_type = 'vip'
    room_rid = config.oversea_room['vip_rid']
    room_area = 'cn'

    def test_01_RoomPayNoMoney(self, des: str = '房间打赏但余额不足的场景'):
        """
        房间打赏余额不足验证
        
        用例描述：
        验证余额不足时，房间一对一打赏
        
        脚本步骤：
        1. 构造打赏者和被打赏者数据
        2. 房间内一对一打赏流程
        3. 校验接口状态和返回值数据
        4. 检查预期返回 msg，预期：支付失败
        5. 检查被打赏者余额，预期：0
        
        Args:
            des: 测试描述
        """
        # 1. 清空用户余额
        conMysql.updateUserMoneyClearSql(config.oversea_payUid, config.oversea_testUid)
        
        # 2. 尝试房间打赏
        data = encodeOverseaData(payType='package')
        res = post_request_session(config.oversea_pay_url, data, token_name='app')
        
        # 3. 校验接口
        assert_code(res['code'])
        assert_body(res['body'], 'success', 0, format_reason(des, res))
        assert_body(res['body'], 'msg', '餘額不足，無法支付', format_reason(des, res))
        
        # 4. 检查余额
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.oversea_testUid), 0)
        
        case_list[des] = result

    def test_02_RoomPayChangeMoney(self, des: str = '商业房 1V1 打赏非主播 70% 场景'):
        """
        房间打赏正常场景验证
        
        用例描述：
        验证余额足够时，非直播类型房间一对一打赏非主播，打赏分成满足师徒收益 (一代宗师) 的基础上为：70:30
        
        脚本步骤：
        1. 构造打赏者和被打赏者数据
        2. 房间内一对一打赏（打赏 600 分）
        3. 校验接口状态和返回值数据
        4. 检查被打赏者余额，预期为：600 * 0.7 = 420
        
        Args:
            des: 测试描述
        """
        # 1. 构造用户数据
        conMysql.updateMoneySql(config.oversea_payUid, 700)
        conMysql.updateMoneySql(config.oversea_testUid)
        conMysql.updateUserextendMoneyClearSql(config.oversea_testUid)  # 非主播钱包附加表账户余额清空
        
        # 2. 房间打赏
        rid = conMysql.select_user_chatroom('business', bigarea_id=2)
        data = encodeOverseaData(payType='package', rid=rid)
        res = post_request_session(config.oversea_pay_url, data, token_name='app')
        
        # 3. 校验接口
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, format_reason(des, res))
        
        # 4. 检查被打赏者收益
        assert_equal(conMysql.selectUserInfoSql('money_cash_personal', config.oversea_testUid, money_type='money_cash_personal'), 420)
        
        case_list[des] = result
