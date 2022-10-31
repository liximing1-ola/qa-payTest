from common.Config import config
from common.method import reason
from common.conMysql import conMysql
from common.Request import post_request_session
import unittest
from common.Assert import assert_code, assert_body, assert_equal
from common.basicData import encodeData
from common.Consts import case_list, result
from common.runFailed import Retry
@Retry
class TestPayCreate(unittest.TestCase):

    liveRid = config.live_role.copy()['liveRid']
    union_rid = conMysql.selectUserInfoSql(accountType='union')

    def test_01_RoomPayNoMoney(self, des='房间1V1打赏但余额不足的场景'):
        """
        用例描述：
        验证余额不足时，房间一对一打赏
        脚本步骤：
        1.构造打赏者和被打赏者数据
        2.房间内一对一打赏流程
        3.校验接口状态和返回值数据
        4.检查预期返回msg，预期：支付失败
        5.检查被打赏者余额,预期：0
        """
        conMysql.updateUserMoneyClearSql(config.payUid, config.rewardUid)
        data = encodeData(payType='package',
                          money=100,
                          rid=self.liveRid,
                          uid=config.rewardUid,
                          giftId=config.giftId['5'])
        res = post_request_session(config.pay_url, data)
        assert_code(res['code'])
        assert_body(res['body'], 'success', 0, reason(des, res))
        assert_body(res['body'], 'msg', '余额不足，无法支付', reason(des, res))
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.rewardUid), 0)
        case_list[des] = result

    def test_02_RoomPayChangeMoney(self, des='非直播1V1打赏场景'):
        """
        用例描述：
        验证余额足够时，非直播类型房间一对一打赏,打赏分成满足师徒收益的基础上为：62:38
        脚本步骤：
        1.构造打赏者和被打赏者数据
        2.房间内一对一打赏（打赏100分）
        3.校验接口状态和返回值数据
        4.检查被打赏者余额，预期为：100 * 0.62 = 62
        """
        conMysql.updateMoneySql(config.payUid, money=30, money_cash=30, money_cash_b=30, money_b=10)
        conMysql.updateMoneySql(config.rewardUid)
        data = encodeData(payType='package',
                          money=100,
                          rid=config.star_role['auto_rid'],
                          uid=config.rewardUid,
                          giftId=config.giftId['5'])
        res = post_request_session(config.pay_url, data)
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(conMysql.selectUserInfoSql('single_money', config.rewardUid), 62)
        case_list[des] = result

    def test_03_couponNoStatePayChange(self, des='打赏礼物使用未激活券的场景', gift_cid=54):
        """
        用例描述：
        有未激活券(state=0)的情况下，验证打赏
        脚本步骤：
        1.构造打赏者和被打赏者数据(gift_cid=54 老司机券)
        2.房间内打赏（券可抵扣500分）
        3.校验接口状态和返回值数据
        4.预期结果： "msg": "余额不足，无法支付"
        5.检查被打赏者余额和账户，预期为：0
        6.检查打赏者余额,预期为：3000
        """
        conMysql.deleteUserAccountSql('user_commodity', config.payUid)
        conMysql.insertXsUserCommodity(config.payUid, gift_cid, num=1)
        conMysql.updateMoneySql(config.payUid, money=3000)
        conMysql.updateMoneySql(config.rewardUid)
        cid = conMysql.selectUserInfoSql('id_commodity', config.payUid, cid=gift_cid)
        data = encodeData(payType='package',
                          rid=config.live_role['auto_rid'],
                          uid=config.rewardUid,
                          giftId=config.giftId['11'],
                          money=3000,
                          package_cid=cid,
                          ctype='coupon',
                          duction_money=500)
        res = post_request_session(config.pay_url, data)
        assert_code(res['code'])
        assert_body(res['body'], 'success', 0, reason(des, res))
        assert_body(res['body'], 'msg', '余额不足，无法支付', reason(des, res))
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.rewardUid), 0)
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.payUid), 3000)
        case_list[des] = result

    def test_04_couponStatePayChange(self, des='打赏礼物时有激活券的场景', gift_cid=54):
        """
        用例描述：
        有激活券(state=1)的情况下，验证打赏流程
        脚本步骤：
        1.构造打赏者和被打赏者数据
        2.房间内打赏（券可抵扣500分）
        3.校验接口状态和返回值数据
        4.检查被打赏者余额和账户，预期为：3000 * 0.62 = 1860
        5.检查打赏者余额,预期为：3000 -2500 = 500
        """
        conMysql.deleteUserAccountSql('user_commodity', config.payUid)
        conMysql.insertXsUserCommodity(config.payUid, gift_cid, num=1, state=1)
        conMysql.updateMoneySql(config.payUid, money=3000)
        conMysql.updateMoneySql(config.rewardUid)
        cid = conMysql.selectUserInfoSql('id_commodity', config.payUid, cid=gift_cid)
        data = encodeData(payType='package',
                          rid=config.live_role['auto_rid'],
                          uid=config.rewardUid,
                          giftId=config.giftId['11'],
                          money=3000,
                          package_cid=cid,
                          ctype='coupon',
                          duction_money=500)
        res = post_request_session(config.pay_url, data)
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.rewardUid), 1860)
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.payUid), 500)
        case_list[des] = result

    def test_05_RoomToMorePayChange(self, des='房间内打赏多人场景'):
        """
        用例描述：
        验证非直播类型房间内一对多打赏场景
        脚本步骤：
        1.构造打赏者和被打赏者数据
        2.房间内一对多打赏流程
        3.校验接口状态和返回值数据
        4.检查打赏者余额,预期为：20000-1000*6*3 = 2000
        5.检查被打赏者余额，预期为：1000*6*0.62 = 3720(非一代宗师)
        """
        conMysql.updateMoneySql(config.payUid, money=5000, money_cash=5000, money_cash_b=5000, money_b=5000)
        conMysql.updateUserMoneyClearSql(config.rewardUid2, config.rewardUid)
        data = encodeData(payType='package-more',
                          num=6,
                          uids=('105002312', '100500131', '100500205'))
        res = post_request_session(config.pay_url, data)
        assert_code(res['code'], 200)
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.rewardUid), 3720)
        assert_equal(conMysql.selectUserInfoSql('single_money', config.payUid, money_type='money_cash'), 2000)
        case_list[des] = result

    def test_06_packCalInUnionRoomPayCreate(self, des='打包结算用户联盟房分成'):
        """
        用例描述：
        验证联盟房间内打包结算用户成员打赏分成为60%（工会魅力值）
        脚本步骤：
        1.构造打赏者和被打赏者数据
        2.联盟房间内打赏直播工会成员
        3.校验接口状态和返回值数据
        4.检查打赏者余额,预期为：1000-1000 = 0
        5.检查被打赏者余额，预期为：1000 * 0.6 = 600
        """
        conMysql.updateMoneySql(config.payUid, money=1000)
        conMysql.updateMoneySql(config.pack_cal_uid)
        data = encodeData(payType='package',
                          rid=self.union_rid,
                          uid=config.pack_cal_uid)  # 联盟房rid，error先检查联盟房在不在
        res = post_request_session(config.pay_url, data)
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.payUid), 0)
        assert_equal(conMysql.selectUserInfoSql('single_money', config.pack_cal_uid, money_type='money_cash'), 600)
        case_list[des] = result

    def test_07_normalUserInUnionRoomPayCreate(self, des='普通用户联盟房分成'):
        """
        用例描述：
        验证联盟房间内普通用户打赏分成为62%（个人魅力值，非一代宗师）
        脚本步骤：
        1.构造打赏者和被打赏者数据
        2.联盟房间内打赏直播工会成员
        3.校验接口状态和返回值数据
        4.检查打赏者余额,预期为：1000-1000 = 0
        5.检查被打赏者余额，预期为：1000 * 0.62 = 620（个人魅力值）
        """
        conMysql.updateMoneySql(config.payUid, money=1000)
        conMysql.updateMoneySql(config.rewardUid)
        data = encodeData(payType='package',
                          rid=self.union_rid,
                          uid=config.rewardUid)  # 联盟房rid
        res = post_request_session(config.pay_url, data)
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.payUid), 0)
        assert_equal(conMysql.selectUserInfoSql('single_money', config.rewardUid), 620)
        case_list[des] = result

    def test_08_couponNoStatePayChange(self, des='电台使用青铜体验券', gift_cid=21980):
        """
        用例描述：
        在电台房使用24小时体验青铜坑位券，不分成
        脚本步骤：
        1.构造打赏者和被打赏者数据(commodity_cid=21981 青铜物品)
        2.房间内开通坑位
        3.校验接口状态和返回值数据
        4.预期结果：开通青铜坑位成功
        5.检查被打赏者余额和账户，预期为：0
        6.检查打赏者余额,预期为：0
        """
        conMysql.deleteUserAccountSql('user_commodity', config.payUid)
        conMysql.insertXsUserCommodity(config.payUid, gift_cid, num=1)
        conMysql.updateUserMoneyClearSql(config.payUid, config.rewardUid)
        cid = conMysql.selectUserInfoSql('id_commodity', config.payUid, cid=gift_cid)
        data = encodeData(payType='package-radioDefend',
                          rid=200022566,  # rid=200022566， error先检查电台房在不在
                          uid=config.rewardUid,
                          money=520,
                          package_cid=cid)
        res = post_request_session(config.pay_url, data)
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.rewardUid), 0)
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.payUid), 0)
        assert_equal(conMysql.selectUserInfoSql('num_commodity', config.payUid, cid=gift_cid), 0)
        case_list[des] = result