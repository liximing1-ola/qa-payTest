from common.Config import config
from common.conMysql import conMysql
from common.method import reason
import unittest
import pytest
from common.Request import post_request_session
from common.Assert import assert_body, assert_code, assert_equal
from common.basicData import encodeData
from common.Consts import case_list_b, result
from common.conRedis import conRedis


@unittest.skip('网赚分成下线-2022/11/1 ')
class TestPayCreate(unittest.TestCase):
    # 网赚房角色配置
    star_role = {}

    @classmethod
    def setUpClass(cls) -> None:
        conMysql.updateUserInfoSql('super_chatroom', TestPayCreate.star_role['super-voice-fresh'])

    @pytest.mark.run(order=1)
    def test_01_starRoomNoBrokerArtistPay_35(self, des='网赚房无公会无经纪人初级艺人收35%个人魅力值'):
        """
        用例描述：
        tdr：网赚频道非公会无经纪人的初级艺人（0-3500）被打赏后收到35%的个人魅力值（此类房间不走师徒分成）
        脚本步骤：
        1.构造打赏者和被打赏者数据
        2.网赚房间一对一打赏（打赏1000分）
        3.校验接口状态和返回值数据
        4.检查被打赏者余额，预期为：1000 * 0.35 = 350(个人魅力值)
        """
        pass

    @pytest.mark.run(order=2)
    def test_02_starRoomNoBrokerArtistPay_45(self, des='网赚房无公会无经纪人中级艺人收45%个人魅力值'):
        """
        用例描述：
        tdr：网赚频道非公会无经纪人的中级艺人（3501-10000）被打赏后收到45%的个人魅力值
        脚本步骤：
        1.构造打赏者和被打赏者数据
        2.网赚房间一对一打赏（打赏1000分）
        3.校验接口状态和返回值数据
        4.检查被打赏者余额，预期为：1000 * 0.45 = 450(个人魅力值)
        """
        pass

    @pytest.mark.run(order=3)
    def test_03_starRoomNoBrokerArtistPay_55(self, des='网赚房无公会无经纪人高级艺人收55%个人魅力值'):
        """
        用例描述：
        tdr：网赚频道非公会无经纪人的高级艺人（>10001）被打赏后收到55%的个人魅力值
        脚本步骤：
        1.构造打赏者和被打赏者数据
        2.网赚房间一对一打赏（打赏1000分）
        3.校验接口状态和返回值数据
        4.检查被打赏者余额，预期为：1000 * 0.55 = 550(个人魅力值)
        """
        pass

    @pytest.mark.run(order=4)
    def test_05_starRoomNoAgentPay_45(self, des='网赚指定工会无经纪人中级艺人收45%公会魅力值'):
        """
        用例描述：
        tdr：网赚频道有公会无经纪人的中级艺人（3501-10000）被打赏后收到45%的公会魅力值
        脚本步骤：
        1.构造打赏者和被打赏者数据
        2.网赚房间一对一打赏（打赏1000分）
        3.校验接口状态和返回值数据
        4.检查被打赏者余额，预期为：1000 * 0.45 = 450（公会魅力值）
        """
        pass

    @pytest.mark.run(order=5)
    def test_05_starRoomSuperVoicePay_508(self, des='网赚无工会有经纪人(1j)初级艺人分成50:8'):
        """
        用例描述：
        tdr：网赚频道无公会有经纪人的初级艺人（0-3500）被打赏后收到50%的个人魅力值，初级经纪人（公会）收到8%公会魅力值
        脚本步骤：
        1.构造打赏者和被打赏者数据
        2.网赚房间一对一打赏（打赏1000分）
        3.校验接口状态和返回值数据
        4.检查被打赏者余额，预期为：1000 * 0.5 = 500（个人魅力值）
        5.检查经纪人余额，预期为：1000 * 0.8 = 80（个人魅力值）
        """
        pass

    @pytest.mark.run(order=6)
    def test_06_starRoomArtistAgent_608(self, des='网赚指定工会有经纪人(1j)的中级艺人分成60:8'):
        """
        用例描述：
        tdr：网赚频道有公会有经纪人的中级艺人（3501-10000）被打赏后收到60%的公会魅力值，初级经纪人（公会）收到8%公会魅力值
        脚本步骤：
        1.构造打赏者和被打赏者数据
        2.网赚房间一对一打赏（打赏1000分）
        3.校验接口状态和返回值数据
        4.检查被打赏者余额，预期为：1000 * 0.6 = 600
        5.检查经纪人余额，预期为：1000 * 0.08 = 80
        """
        pass

    @pytest.mark.run(order=7)
    def test_07_starRoomArtistAgent_7012(self, des='网赚有工会有经纪人(7j)高级艺人分成70:12'):
        """
        用例描述：
        tdr：网赚频道有公会有经纪人的高级艺人（>10001）被打赏后收到70%的公会魅力值，高级经纪人（公会）收到12%公会魅力值
        脚本步骤：
        1.构造打赏者和被打赏者数据
        2.网赚房间一对一打赏（打赏1000分）
        3.校验接口状态和返回值数据
        4.检查被打赏者余额，预期为：1000 * 0.7 = 700（money_cash）
        5.检查经纪人余额，预期为： 1000 * 0.12 = 120(money_cash)
        """
        pass

    @pytest.mark.run(order=8)
    def test_08_NormalRoomPayArtist_620(self, des='普通房指定工会有经纪人(1j)只艺人收到62%'):
        """
        用例描述：
        tdr：非网赚频道王牌公会中有经纪人的艺人被打赏后收到62%的个人魅力值，经纪人无收入
        脚本步骤：
        1.构造打赏者和被打赏者数据
        2.网赚房间一对一打赏（打赏1000分）
        3.校验接口状态和返回值数据
        4.检查被打赏者余额，预期为：1000 * 0.62 = 620（个人魅力值）
        5.检查经纪人余额，预期为：0
        """
        pass

    @pytest.mark.run(order=9)
    def test_09_starRoomWhiteUserPay_70(self, des='网赚房无公会无经纪人白名单艺人收70%个人魅力值'):
        """
        用例描述：
        tdr：网赚频道非公会无经纪人的白名单初级艺人（0-3500）被打赏后收到70%的个人魅力值
        脚本步骤：
        1.构造打赏者和被打赏者数据
        2.网赚房间一对一打赏（打赏1000分）
        3.校验接口状态和返回值数据
        4.检查被打赏者余额，预期为：1000 * 0.7 = 700(个人魅力值)
        """
        pass
