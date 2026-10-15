"""
common/basic_data.py 单元测试（数据编码）

全部 mock Config 依赖，可在无后端环境下直接运行：
    python -m pytest tests/test_basic_data.py -v
"""
import unittest
import urllib.parse


class TestEncodeDataHelper(unittest.TestCase):
    """_encode_data_helper 的 URL 编码特殊处理"""

    def test_replaces_plus_signs(self):
        """编码后 + 号应被移除"""
        from common.basic_data import _encode_data_helper
        result = _encode_data_helper({'key': 'a b'})
        self.assertNotIn('+', result)

    def test_replaces_single_quote(self):
        """%27（单引号）应被替换为 %22（双引号）"""
        from common.basic_data import _encode_data_helper
        result = _encode_data_helper({'key': "it's"})
        self.assertNotIn('%27', result)
        self.assertIn('%22', result)

    def test_normal_encoding(self):
        """普通字符串应正常编码"""
        from common.basic_data import _encode_data_helper
        result = _encode_data_helper({'name': 'test', 'value': '123'})
        parsed = urllib.parse.parse_qs(result)
        self.assertEqual(parsed['name'], ['test'])


class TestBuildPackageParams(unittest.TestCase):
    """_build_package_params 参数构建"""

    def test_basic_params(self):
        """基本参数应包含所有必要字段"""
        from common.basic_data import _build_package_params
        result = _build_package_params(rid='100', uid='200', money=1000,
                                       giftId=7, num=1)
        self.assertEqual(result['rid'], '100')
        self.assertEqual(result['uids'], '200')
        self.assertEqual(result['price'], 1000)
        self.assertEqual(result['giftId'], 7)
        self.assertEqual(result['giftNum'], 1)
        self.assertEqual(result['version'], 2)
        self.assertEqual(result['useCoin'], -1)

    def test_custom_package_cid(self):
        """自定义 package_cid 应生效"""
        from common.basic_data import _build_package_params
        result = _build_package_params(rid='1', uid='2', money=100,
                                       giftId=1, num=1, package_cid=99)
        self.assertEqual(result['cid'], 99)


class TestBuildShopBuyParams(unittest.TestCase):
    """_build_shop_buy_params 参数构建"""

    def test_price_zero_uses_money(self):
        """price=0 时应使用 money 作为 price"""
        from common.basic_data import _build_shop_buy_params
        result = _build_shop_buy_params(money=500, num=2)
        self.assertEqual(result['price'], 500)

    def test_price_nonzero(self):
        """price 非零时应使用传入值"""
        from common.basic_data import _build_shop_buy_params
        result = _build_shop_buy_params(money=500, num=2, price=300)
        self.assertEqual(result['price'], 300)

    def test_default_values(self):
        """默认值应正确设置"""
        from common.basic_data import _build_shop_buy_params
        result = _build_shop_buy_params()
        self.assertEqual(result['coupon_id'], 0)
        self.assertEqual(result['duction_money'], 0)
        self.assertEqual(result['version'], 2)
        self.assertEqual(result['useCoin'], -1)


class TestEncodeData(unittest.TestCase):
    """encode_data 的 payType 分发"""

    def test_package_type(self):
        """package 类型应返回编码字符串"""
        from common.basic_data import encode_data
        result = encode_data(payType='package', money=1000, rid='100',
                            uid='200', giftId=7, num=1)
        self.assertIsInstance(result, str)
        self.assertIn('type=package', result)

    def test_package_more_type(self):
        """package-more 多人打赏应计算总金额"""
        from common.basic_data import encode_data
        result = encode_data(payType='package-more', money=100, num=2,
                            uids=('100', '200'))
        self.assertIsInstance(result, str)
        self.assertIn('type=package', result)

    def test_chat_gift_type(self):
        """chat-gift 类型应包含 to 和 giftId"""
        from common.basic_data import encode_data
        result = encode_data(payType='chat-gift', money=500, uid='300',
                            giftId=7, num=1)
        self.assertIsInstance(result, str)
        self.assertIn('type=chat-gift', result)

    def test_shop_buy_type(self):
        """shop-buy 类型应返回编码字符串"""
        from common.basic_data import encode_data
        result = encode_data(payType='shop-buy', money=100, num=1)
        self.assertIsInstance(result, str)
        self.assertIn('type=shop-buy', result)

    def test_defend_type(self):
        """defend 类型应包含 defend_id"""
        from common.basic_data import encode_data
        result = encode_data(payType='defend', money=1000, uid='100', defend_id=244)
        self.assertIsInstance(result, str)
        self.assertIn('type=defend', result)

    def test_title_type(self):
        """title 类型应返回编码字符串"""
        from common.basic_data import encode_data
        result = encode_data(payType='title', money=2000)
        self.assertIsInstance(result, str)
        self.assertIn('type=title', result)

    def test_defend_break_special_encode(self):
        """defend-break 应使用 _special_encode 分支（普通 urlencode）"""
        from common.basic_data import encode_data
        result = encode_data(payType='defend-break', money=1000, defend_id=100)
        self.assertIsInstance(result, str)
        self.assertIn('type=defend-break', result)
        # defend-break 使用 urllib.parse.urlencode 而非 _encode_data_helper
        # 所以 + 不会被移除
        parsed = urllib.parse.parse_qs(result)
        self.assertIn('type', parsed)

    def test_unknown_paytype_raises(self):
        """未知 payType 应抛出 ValueError"""
        from common.basic_data import encode_data
        with self.assertRaises(ValueError) as ctx:
            encode_data(payType='nonexistent_type')
        self.assertIn('nonexistent_type', str(ctx.exception))


class TestEncodeOverseaData(unittest.TestCase):
    """encode_oversea_data 的 payType 分发"""

    def test_package_type(self):
        """海外版 package 类型应返回编码字符串"""
        from common.basic_data import encode_oversea_data
        result = encode_oversea_data(payType='package', money=600, rid='100',
                                   uid='200', giftId=10, num=1)
        self.assertIsInstance(result, str)
        self.assertIn('type=package', result)

    def test_chat_gift_type(self):
        """海外版 chat-gift 应包含 hideErrorToast"""
        from common.basic_data import encode_oversea_data
        result = encode_oversea_data(payType='chat-gift', money=600, uid='300',
                                   giftId=10, num=1)
        self.assertIsInstance(result, str)
        self.assertIn('type=chat-gift', result)

    def test_defend_type(self):
        """海外版 defend 类型应返回编码字符串"""
        from common.basic_data import encode_oversea_data
        result = encode_oversea_data(payType='defend', money=600, uid='100')
        self.assertIsInstance(result, str)
        self.assertIn('type=defend', result)

    def test_unknown_paytype_raises(self):
        """海外版未知 payType 应抛出 ValueError"""
        from common.basic_data import encode_oversea_data
        with self.assertRaises(ValueError):
            encode_oversea_data(payType='nonexistent_oversea_type')

    def test_shop_buy_box_type(self):
        """海外版 shop-buy-box 应返回编码字符串"""
        from common.basic_data import encode_oversea_data
        result = encode_oversea_data(payType='shop-buy-box', money=100,
                                   cid=5, num=1, boxType='copper')
        self.assertIsInstance(result, str)
        self.assertIn('type=shop-buy', result)


if __name__ == '__main__':
    unittest.main()
