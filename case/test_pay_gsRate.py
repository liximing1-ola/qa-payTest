import hashlib
import time
import unittest
from common import basicData
from common.Assert import assert_body, assert_code, assert_equal
from common.Config import config
from common.Consts import case_list_b, result
from common.Request import post_request_session
from common.conMysql import conMysql
from common.method import reason
from common.runFailed import Retry


@Retry
class TestPayCreate(unittest.TestCase):
    rate_role = {
        "bid": 100011021,  # 公会的bid
        'rewardUid': 131554725,  # 打赏者
        'rewardedUid': 131564968,  # 被打赏者
    }

    # 刷新url的加密数据
    @staticmethod
    def get_url(url0):
        second = str(int(time.time()))
        pms = {
            "_index": 302,
            "_ipv": 0,
            "_model": "iPhone",
            "_platform": "ios",
            "_timestamp": second,
            "format": "json",
            "package": "com.im.teammate.ios",
        }
        url = ""
        for k, v in pms.items():
            url = url + k + "=" + str(v) + "&"
        url = url.rstrip('&')
        md5 = hashlib.md5()
        _sign0 = url + '!rilegoule#'
        md5.update(_sign0.encode('utf-8'))
        _sign = md5.hexdigest()
        url = url + "&_sign=" + _sign
        url = url0 + url
        return url

    # 查询uid是否在分成白名单并更新或者插入
    @staticmethod
    def join_white_name(uid):
        sql = 'select id from config.xsst_ktv_uid_white where uid={}'.format(uid)
        try:
            conMysql.cur.execute(sql)
            res = conMysql.cur.fetchone()
            if res is None:
                sql = "insert into config.xsst_ktv_uid_white (uid,app_id,`type`) values ({},2,127);".format(uid)
                try:
                    conMysql.cur.execute(sql)
                except Exception as error:
                    conMysql.con.rollback()
                    print('insert fail', error)
                finally:
                    conMysql.con.commit()
            else:
                sql = 'update config.xsst_ktv_uid_white set app_id={},`type`={} where id={}'.format(2, 127, res[0])
                try:
                    conMysql.cur.execute(sql)
                except Exception as error:
                    conMysql.con.rollback()
                    print('update fail', error)
                finally:
                    conMysql.con.commit()
        except Exception as error:
            print(error)

    def test_01_roomPayCustomRate_60(self, des='商业房打赏自定义分成:60'):
        """
        用例描述：
        tdr:后台自定义分成比例为60%
        脚本步骤：
        1.构造打赏者，被打赏者数据
        2.房间内打赏（打赏100分）
        3.校验接口状态和返回值数据
        4.检查打赏者余额，预期为：100 - 100 = 0
        5.检查被打赏者余额，预期为：100 * 0.6 = 60
        """
        testUid = self.rate_role["rewardedUid"]  # 被打赏者
        payUid = self.rate_role["rewardUid"]  # 打赏
        conMysql.updateUserMoneyClearSql(testUid, payUid)
        conMysql.updateMoneySql(payUid, money=100)  # 打赏者
        conMysql.checkUserBroker(testUid, bid=self.rate_role["bid"])  # 被打赏者加入工会
        self.join_white_name(testUid)  # 被打赏者加入白名单，分成为60%

        data = basicData.encodeData(payType='package', money=100, rid=200064778, uid=testUid, giftId=config.giftId['5'])
        # 内网支付接口
        res = post_request_session(config.rush_pay_url, data, tokenName='rush')
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(conMysql.selectUserInfoSql('sum_money', payUid), 0)  # 打赏者金额剩余
        assert_equal(conMysql.selectUserInfoSql('sum_money', testUid), 60)  # 被打赏者金额总数
        case_list_b[des] = result

    def test_02_chatPayCustomRate_60(self, des='私聊打赏自定义分成:60'):
        """
        用例描述：
        tdr:后台自定义分成比例为60%
        脚本步骤：
        1.构造打赏者，被打赏者
        2.私聊打赏（打赏1000分）
        3.校验接口状态和返回值数据
        4.检查打赏者余额，预期为：1000 - 1000 = 0
        5.检查被打赏者总余额，预期为：1000 * 0.6 = 600
        """
        testUid = self.rate_role["rewardedUid"]  # 被打赏者
        payUid = self.rate_role["rewardUid"]
        conMysql.updateUserMoneyClearSql(testUid, payUid)
        conMysql.updateMoneySql(payUid, money=1000)  # 打赏者
        conMysql.checkUserBroker(testUid, bid=self.rate_role["bid"])  # 被打赏者加入工会
        self.join_white_name(testUid)  # 被打赏者加入白名单，分成为60%
        data = basicData.encodeData(payType='chat-gift', uid=testUid, giftId=20)
        res = post_request_session(config.rush_pay_url, data, tokenName='rush')
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(conMysql.selectUserInfoSql('sum_money', payUid), 0)  # 打赏者金额剩余
        assert_equal(conMysql.selectUserInfoSql('sum_money', testUid), 600)  # 被打赏者金额总数
        case_list_b[des] = result

    def test_03_defendPayCustomRate_60(self, des='个人守护打赏自定义分成:60'):
        """
        用例描述：
        tdr:后台自定义分成比例为60%
        脚本步骤：
        1.构造打赏者，被打赏者
        2.开通守护
        3.校验接口状态和返回值数据
        4.检查打赏者余额，预期为：52000 - 52000 = 0
        5.检查被打赏者总余额，预期为：52000 * 0.6 = 31200
        """
        testUid = self.rate_role["rewardedUid"]  # 被打赏者
        payUid = self.rate_role["rewardUid"]
        conMysql.updateUserMoneyClearSql(testUid, payUid)
        conMysql.updateMoneySql(payUid, money=52000)  # 打赏者
        conMysql.checkUserBroker(testUid, bid=self.rate_role["bid"])  # 被打赏者加入工会
        self.join_white_name(testUid)  # 被打赏者加入白名单，分成为60%
        data = basicData.encodeData(payType='defend', uid=testUid, money=52000)
        res = post_request_session(config.rush_pay_url, data, tokenName='rush')
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(conMysql.selectUserInfoSql('sum_money', payUid), 0)
        assert_equal(conMysql.selectUserInfoSql('sum_money', testUid), 31200)
        case_list_b[des] = result


if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite.addTest(TestPayCreate("test_03_defendPayCustomRate_60"))
    unittest.TextTestRunner().run(suite)
