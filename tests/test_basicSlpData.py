# coding=utf-8
"""
common/basicSlpData.py 单元测试（SLP 消费数据编码分发）

全部离线运行（caseSlp.config 为纯常量，无 DB/网络依赖）：
    python -m pytest tests/test_basicSlpData.py -v
"""
import ast
import unittest
import urllib.parse

from common.basicSlpData import PAY_TYPE_HANDLERS, _encode_data, encodeData


def _decode(encoded: str) -> dict:
    outer = {k: v[0] for k, v in urllib.parse.parse_qs(encoded).items()}
    if 'params' in outer:
        # params 子结构是 dict 经 str() 后整体编码（单引号→双引号、空格删除），
        # parse_qs 解码后即为 JSON 风格字典字面量，literal_eval 还原后数字字段保持 int
        outer['params'] = ast.literal_eval(outer['params'])
    return outer


class TestEncodeData(unittest.TestCase):
    """encodeData 各支付类型分发"""

    def test_package_fields(self):
        """package：rid/uids/price 透传，通用字段齐备"""
        out = _decode(encodeData(payType='package', money=100, price=50,
                                 rid=111, uid=222, gift_id=69, num=1, star=0))
        self.assertEqual(out['type'], 'package')
        self.assertEqual(out['money'], '100')
        self.assertEqual(out['params']['rid'], 111)
        self.assertEqual(out['params']['uids'], '222')
        self.assertEqual(out['params']['price'], 50)
        self.assertEqual(out['params']['useCoin'], -1)

    def test_chat_gift_uid_stringified(self):
        """chat-gift：to 应字符串化"""
        out = _decode(encodeData(payType='chat-gift', uid=222, money=100,
                                 gift_id=69, num=2, star=0))
        self.assertEqual(out['type'], 'chat-gift')
        self.assertEqual(out['params']['to'], '222')
        self.assertEqual(out['params']['giftNum'], 2)

    def test_package_more_money_calc(self):
        """package-more：money = money*num*人数，num 汇总为 num*人数"""
        out = _decode(encodeData(payType='package-more', money=100, price=100,
                                 rid=111, gift_id=69, num=2,
                                 uids=('222', '333')))
        self.assertEqual(out['money'], '400')
        self.assertEqual(out['params']['num'], 4)
        self.assertEqual(out['params']['uids'], '222,333')
        self.assertEqual(out['params']['positions'], '1,2')

    def test_zx_box_refer(self):
        """zx_box：refer 应为 search:room，money = price*人数*num"""
        out = _decode(encodeData(payType='zx_box', price=50, num=2,
                                 rid=111, gift_id=88,
                                 uids=('222', '333')))
        self.assertEqual(out['money'], '200')
        self.assertEqual(out['params']['refer'], 'search:room')
        self.assertEqual(out['params']['num'], 4)

    def test_knight_defend_levels(self):
        """package-knightDefend：骑士/持续等级透传"""
        out = _decode(encodeData(payType='package-knightDefend', money=100,
                                 price=100, rid=111, uid=222,
                                 knight_level=3, duration_level=2))
        params = out['params']
        self.assertEqual(params['knight_level'], 3)
        self.assertEqual(params['duration_level'], 2)
        self.assertEqual(params['uids'], '222')

    def test_defend_upgrade_and_break_id_stringified(self):
        """defend-upgrade / defend-break：id 应字符串化"""
        up = _decode(encodeData(payType='defend-upgrade', money=100, defend_id=244))
        self.assertEqual(up['params']['id'], '244')
        br = _decode(encodeData(payType='defend-break', money=100, defend_id=244))
        self.assertEqual(br['params']['id'], '244')

    def test_unknown_pay_type_raises(self):
        """未知 payType 应抛 ValueError"""
        with self.assertRaises(ValueError):
            encodeData(payType='not_exists')

    def test_handler_registry(self):
        """8 个支付类型应全部注册"""
        self.assertEqual(set(PAY_TYPE_HANDLERS), {
            'chat-gift', 'package', 'package-more', 'package-knightDefend',
            'defend', 'defend-upgrade', 'defend-break', 'zx_box'})


class TestEncodeHelper(unittest.TestCase):
    """_encode_data 编码规则（与 basicData 一致）"""

    def test_plus_removed_and_quote_replaced(self):
        out = _encode_data({'a': "it's"})
        self.assertNotIn('%27', out)
        self.assertIn('%22', out)


if __name__ == '__main__':
    unittest.main()
