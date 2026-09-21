# coding=utf-8
"""
common/basicData.py 单元测试（encodeData / encodeOverseaData 分发与编码）

全部离线运行（默认参数仅读 config 常量，无 DB/网络依赖）：
    python -m pytest tests/test_basicData.py -v
"""
import ast
import urllib.parse

import unittest

from common.basicData import (
    PAY_TYPE_HANDLERS,
    OVERSEA_PAY_TYPE_HANDLERS,
    _encode_data_helper,
    encodeData,
    encodeOverseaData,
)


def _decode(encoded: str) -> dict:
    """把编码输出解回字典（单层；params 子结构为字符串）"""
    return {k: v[0] for k, v in urllib.parse.parse_qs(encoded).items()}


def _decode_params(encoded: str) -> dict:
    """把 package 类输出中的 params 子结构解回字典

    params 子结构是 dict 经 str() 后整体编码（单引号被替换为双引号、
    空格被删除），需 unquote 后 literal_eval 还原，数字字段保持 int。
    """
    return ast.literal_eval(urllib.parse.unquote(_decode(encoded)['params']))


class TestEncodeHelper(unittest.TestCase):
    """_encode_data_helper 编码规则"""

    def test_plus_removed_and_quote_replaced(self):
        """空格编码出的 + 应删除，单引号 %27 应替换为双引号 %22"""
        out = _encode_data_helper({'a': 'x y', "b": "it's"})
        self.assertNotIn('+', out)
        self.assertIn('%22', out)
        self.assertNotIn('%27', out)


class TestEncodeData(unittest.TestCase):
    """encodeData 各支付类型分发"""

    def test_package_structure(self):
        """package：type/platform/money 平铺，params 含核心打赏字段"""
        out = _decode(encodeData(payType='package', money=600, rid=111, uid=222,
                                 giftId=46, num=1))
        self.assertEqual(out['platform'], 'available')
        self.assertEqual(out['type'], 'package')
        self.assertEqual(out['money'], '600')
        params = _decode_params(encodeData(payType='package', money=600, rid=111,
                                            uid=222, giftId=46, num=1))
        self.assertEqual(params['rid'], 111)
        self.assertEqual(params['uids'], '222')
        self.assertEqual(params['giftId'], 46)
        self.assertEqual(params['price'], 600)
        self.assertEqual(params['useCoin'], -1)

    def test_package_more_money_calc(self):
        """package-more：money = money*num*人数，uids 逗号连接、positions 顺序编号"""
        out = _decode(encodeData(payType='package-more', money=100, num=2,
                                 rid=111, giftId=46, uids=('222', '333')))
        self.assertEqual(out['money'], '400')
        params = _decode_params(encodeData(payType='package-more', money=100, num=2,
                                           rid=111, giftId=46, uids=('222', '333')))
        self.assertEqual(params['uids'], '222,333')
        self.assertEqual(params['positions'], '1,2')
        self.assertEqual(params['num'], 2)

    def test_package_exchange_flag(self):
        """package-exchange：params 应带 exchange=1"""
        params = _decode_params(encodeData(payType='package-exchange', rid=111,
                                            uid=222, giftId=46))
        self.assertEqual(params['exchange'], 1)

    def test_chat_gift_fields(self):
        """chat-gift：to/giftNum 透传，star 默认 0"""
        params = _decode_params(encodeData(payType='chat-gift', uid=222, giftId=7,
                                            money=1000, num=3))
        self.assertEqual(params['to'], '222')
        self.assertEqual(params['giftId'], 7)
        self.assertEqual(params['giftNum'], 3)
        self.assertEqual(params['star'], 0)

    def test_shop_buy_price_fallback(self):
        """shop-buy：price=0 时回退为 money，money 为 money*num"""
        params = _decode_params(encodeData(payType='shop-buy', money=16, num=10))
        self.assertEqual(params['price'], 16)
        self.assertEqual(params['num'], 10)
        self.assertEqual(params['gift_scene'], 'shop')
        outer = _decode(encodeData(payType='shop-buy', money=16, num=10))
        self.assertEqual(outer['money'], '160')

    def test_shop_buy_box_fields(self):
        """shop-buy-box：type=boxType、opennum=num、star 透传默认 0"""
        params = _decode_params(encodeData(payType='shop-buy-box', money=100,
                                            num=2, cid=362, boxType='copper'))
        self.assertEqual(params['type'], 'copper')
        self.assertEqual(params['opennum'], 2)
        self.assertEqual(params['cid'], 362)
        # kw.get('star', 4) 的兜底值仅在 star 键缺席时生效，encodeData 总是传 star=0
        self.assertEqual(params['star'], 0)

    def test_defend_fields(self):
        """defend：defend=defend_id、to=uid"""
        params = _decode_params(encodeData(payType='defend', uid=222, money=52000,
                                            defend_id=2))
        self.assertEqual(params['defend'], 2)
        self.assertEqual(params['to'], '222')

    def test_defend_upgrade_id_stringified(self):
        """defend-upgrade：id 应字符串化"""
        params = _decode_params(encodeData(payType='defend-upgrade', money=99900,
                                           defend_id=244))
        self.assertEqual(params['id'], '244')
    def test_defend_break_special_encode(self):
        """defend-break：走 urlencode 原样编码（单引号 %22 替换不生效）"""
        out = encodeData(payType='defend-break', money=28800, defend_id=244)
        self.assertIn('type=defend-break', out)
        self.assertIn('money=28800', out)
        # params 子结构以原始 dict 字符串形式编码（含单引号 %27）
        self.assertIn('%27', out)

    def test_title_fields(self):
        """title：固定等级/头衔参数"""
        params = _decode_params(encodeData(payType='title', money=100))
        self.assertEqual(params['level'], 1)
        self.assertEqual(params['tid'], 1)

    def test_default_arguments_package(self):
        """无参调用应使用默认 package 场景并带上默认金额"""
        out = _decode(encodeData())
        self.assertEqual(out['type'], 'package')
        self.assertEqual(out['money'], '1000')

    def test_unknown_pay_type_raises(self):
        """未知 payType 应抛 ValueError"""
        with self.assertRaises(ValueError):
            encodeData(payType='not_exists')
        with self.assertRaises(ValueError):
            encodeOverseaData(payType='not_exists')


class TestEncodeOverseaData(unittest.TestCase):
    """encodeOverseaData 海外版分发"""

    def test_chat_gift_hide_error_toast(self):
        """海外 chat-gift：params 应带 hideErrorToast=1"""
        params = _decode_params(encodeOverseaData(payType='chat-gift', uid=222,
                                                   giftId=10, money=6, num=1))
        self.assertEqual(params['hideErrorToast'], 1)
        self.assertEqual(params['to'], '222')

    def test_defend_fixed_id(self):
        """海外 defend：defend 固定为 8"""
        params = _decode_params(encodeOverseaData(payType='defend', uid=222,
                                                   money=100))
        self.assertEqual(params['defend'], 8)

    def test_chat_pay_card_params_as_string(self):
        """chat-pay-card：params 应保持 JSON 字符串原样编码"""
        out = encodeOverseaData(payType='chat-pay-card')
        self.assertIn('type=chat-pay-card', out)
        self.assertIn('%22cid%22', out)

    def test_play_crazyspin_flat_structure(self):
        """play-crazyspin：平铺结构（无 platform/type/params 包裹）"""
        out = _decode(encodeOverseaData(payType='play-crazyspin', rid=999))
        self.assertEqual(out['rid'], '999')
        self.assertEqual(out['draw_type'], '10')
        self.assertEqual(out['turntable_type'], '1')
        self.assertNotIn('params', out)

    def test_shared_handlers_between_tables(self):
        """package 系列处理器应为两张表共享（同对象）"""
        for key in ('package', 'package-more', 'package-exchange',
                    'shop-buy', 'exchange_gold'):
            self.assertIs(PAY_TYPE_HANDLERS[key], OVERSEA_PAY_TYPE_HANDLERS[key])


if __name__ == '__main__':
    unittest.main()
