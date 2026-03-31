# coding=utf-8
"""
基础数据编码模块

提供不同消费场景的数据编码功能，支持多种支付类型和平台。
使用字典映射替代大量 if-elif 分支，提升代码可维护性。
"""
import urllib.parse
from typing import Dict, Any, Tuple, Optional
from common.Config import config

# 默认常量
DEFAULT_VERSION = 2
DEFAULT_USE_COIN = -1
DEFAULT_SHOW_PAC_MAN_GUIDE = 1


def _encode_data_helper(data: Dict[str, Any]) -> str:
    """
    URL 编码辅助函数
    
    Args:
        data: 待编码的字典数据
        
    Returns:
        编码后的字符串
    """
    return urllib.parse.urlencode(data).replace('+', '').replace('%27', '%22')


def _build_package_params(rid: str, uid: str, money: int, giftId: int, 
                          num: int, package_cid: int = 0, ctype: str = '',
                          duction_money: int = 0, star: int = 0,
                          giftType: str = 'normal', **kwargs) -> Dict[str, Any]:
    """构建 package 类型的基础参数"""
    return {
        "rid": rid,
        "uids": uid,
        "positions": kwargs.get('positions', '1'),
        "position": -1,
        "giftId": giftId,
        "giftNum": num,
        "price": money,
        "cid": package_cid,
        "ctype": ctype,
        "duction_money": duction_money,
        "version": DEFAULT_VERSION,
        "num": num,
        "gift_type": giftType,
        "useCoin": DEFAULT_USE_COIN,
        "star": star,
        "show_pac_man_guide": DEFAULT_SHOW_PAC_MAN_GUIDE,
        "refer": "",
        "all_mic": 0,
    }


def _build_shop_buy_params(money: int = 0, num: int = 1, cid: int = 0, price: int = 0,
                           version: int = DEFAULT_VERSION, **kwargs) -> Dict[str, Any]:
    """构建 shop-buy 类型的基础参数
    
    Args:
        money: 金额（如果 price 为 0 则使用 money）
        num: 数量
        cid: 优惠券 ID
        price: 单价（如果为 0 则使用 money）
        version: 版本号
        **kwargs: 其他参数
        
    Returns:
        shop-buy 参数字典
    """
    # 如果 price 为 0，使用 money 作为 price
    if price == 0:
        price = money
    return {
        "num": num,
        "cid": cid,
        "price": price,
        "coupon_id": 0,
        "duction_money": 0,
        "version": version,
        "gift_scene": kwargs.get('gift_scene', 'shop'),
        "useCoin": DEFAULT_USE_COIN,
    }


# 支付类型处理器映射表
PAY_TYPE_HANDLERS = {
    # ==================== 普通场景 ====================
    'package': lambda **kw: {
        "platform": "available",
        "type": "package",
        "money": kw['money'],
        "params": _build_package_params(**kw)
    },
    
    'package-more': lambda **kw: {
        "platform": "available",
        "type": "package",
        "money": kw['money'] * kw['num'] * len(kw['uids']),
        "params": {
            **_build_package_params(
                rid=kw['rid'],
                uid=','.join(kw['uids']),
                money=kw['money'],
                giftId=kw['giftId'],
                num=kw['num'],
                positions=','.join(str(i + 1) for i in range(len(kw['uids']))),
                **kw
            ),
            "cid": 0,
            "ctype": "",
            "duction_money": 0,
        }
    },
    
    'package-exchange': lambda **kw: {
        "platform": "available",
        "type": "package",
        "money": kw['money'],
        "params": {
            **_build_package_params(**kw),
            "cid": 0,
            "ctype": "",
            "duction_money": 0,
            "exchange": 1
        }
    },
    
    'package-knightDefend': lambda **kw: {
        "platform": "available",
        "type": "package",
        "money": kw['money'],
        "params": {
            "price": kw['money'],
            "knight_level": 2,
            "duration_level": 2,
            "rid": kw['rid'],
            "uids": kw['uid'],
            "useCoin": DEFAULT_USE_COIN,
        }
    },
    
    'package-radioDefend': lambda **kw: {
        "platform": "available",
        "type": "package",
        "money": kw['money'],
        "params": {
            "price": kw['money'],
            "rid": kw['rid'],
            "uids": kw['uid'],
            "positions": "0",
            "defend": 3,
            "cid": kw.get('package_cid', 0),
            "duction_money": 0,
            "useCoin": DEFAULT_USE_COIN,
        }
    },
    
    'chat-gift': lambda **kw: {
        "platform": "available",
        "type": "chat-gift",
        "money": kw['money'],
        "params": {
            "notify_group_id": 0,
            "to": kw['uid'],
            "giftId": kw['giftId'],
            "giftNum": kw['num'],
            "cid": 0,
            "ctype": "",
            "duction_money": 0,
            "version": DEFAULT_VERSION,
            "num": kw['num'],
            "gift_type": "normal",
            "star": kw.get('star', 0),
            "show_pac_man_guide": DEFAULT_SHOW_PAC_MAN_GUIDE,
            "all_mic": 0,
            "useCoin": DEFAULT_USE_COIN
        }
    },
    
    'shop-buy-box': lambda **kw: {
        "platform": 'available',
        "type": 'shop-buy',
        "money": kw['money'] * kw['num'],
        "params": {
            "num": kw['num'],
            "cid": kw['cid'],
            "price": kw['money'],
            "type": kw['boxType'],
            "opennum": kw['num'],
            "coupon_id": 0,
            "duction_money": 0,
            "version": DEFAULT_VERSION,
            "star": kw.get('star', 4),
            "show_pac_man_guide": DEFAULT_SHOW_PAC_MAN_GUIDE,
            "useCoin": DEFAULT_USE_COIN
        }
    },
    
    'shop-buy': lambda **kw: {
        "platform": 'available',
        "type": 'shop-buy',
        "money": kw['money'] * kw['num'],
        "params": _build_shop_buy_params(**kw)
    },
    
    'defend': lambda **kw: {
        "platform": 'available',
        "type": 'defend',
        "money": kw['money'],
        "params": {
            "defend": kw['defend_id'],
            "to": kw['uid'],
            "cid": 0,
            "duction_money": 0,
            "unified_relation_version": 1,
            "useCoin": DEFAULT_USE_COIN
        }
    },
    
    'defend-upgrade': lambda **kw: {
        "platform": 'available',
        "type": 'defend-upgrade',
        "money": kw['money'],
        "params": {
            "id": str(kw['defend_id']),
            "useCoin": DEFAULT_USE_COIN
        }
    },
    
    'defend-break': lambda **kw: {
        "platform": 'available',
        "type": 'defend-break',
        "money": kw['money'],
        "params": {
            "id": str(kw['defend_id']),
            "useCoin": DEFAULT_USE_COIN
        },
        "_special_encode": True  # 标记需要特殊处理
    },
    
    'title': lambda **kw: {
        "platform": "available",
        "type": "title",
        "money": kw['money'],
        "params": {
            "level": 1,
            "num": 1,
            "tid": 1,
            "cid": 0,
            "ctype": "",
            "duction_money": 0,
            "useCoin": DEFAULT_USE_COIN
        }
    },
    
    'exchange_gold': lambda **kw: {
        "platform": 'available',
        "type": 'exchange_gold',
        "money": '600',
        "params": {
            "type": "exchange_gold"
        }
    },
    
    'unity-game-buy': lambda **kw: {
        "platform": 'available',
        "type": 'unity-game-buy',
        "money": kw['money'],
        "params": {
            "amount": 1,
            "app_ver": "1.0.0",
            "c_id": 10001,
            "c_name": "棋子皮肤",
            "c_num": 1,
            "game_type": "Ludo",
            "money_type": "diamond",
            "rid": 105707946
        }
    },
    
    'pub-drink-buy': lambda **kw: {
        "platform": 'available',
        "type": 'pub-drink-buy',
        "money": kw['money'],
        "params": {
            "pub_club_rid": kw['rid'],
            "menu_id": 6,
            "num": 1,
            "useCoin": DEFAULT_USE_COIN,
            "gift_type": 'bean',
            "refer": "",
            "exchange": 1,
        }
    },
    
    'deco-present': lambda **kw: {
        "platform": 'available',
        "type": 'deco-present',
        "money": kw['money'],
        "params": {
            "num": 1,
            "uids": kw['uid'],
            "money_type": "bean",
            "cid": kw['cid'],
            "price": kw['money'],
            "coupon_id": 0,
            "duction_money": 0,
            "version": DEFAULT_VERSION,
            "useCoin": DEFAULT_USE_COIN
        }
    },
    
    'banban-consume': lambda **kw: {
        "platform": 'available',
        "type": 'banban-consume',
        "money": kw['money'],
        "params": {
            "consume_type": "music_order",
            "rid": kw['rid'],
            "order_songs": [{"song_id": 10282, "singer_id": kw['uid']}],
            "useCoin": DEFAULT_USE_COIN
        }
    },
}

# 海外版平台支付类型处理器
OVERSEA_PAY_TYPE_HANDLERS = {
    'package': lambda **kw: {
        "platform": "available",
        "type": "package",
        "money": kw['money'],
        "params": _build_package_params(**kw)
    },
    
    'package-more': lambda **kw: {
        "platform": "available",
        "type": "package",
        "money": kw['money'] * kw['num'] * len(kw['uids']),
        "params": {
            **_build_package_params(
                rid=kw['rid'],
                uid=','.join(kw['uids']),
                money=kw['money'],
                giftId=kw['giftId'],
                num=kw['num'],
                positions=','.join(str(i + 1) for i in range(len(kw['uids']))),
                **kw
            ),
            "cid": 0,
            "ctype": "",
            "duction_money": 0,
        }
    },
    
    'package-exchange': lambda **kw: {
        "platform": "available",
        "type": "package",
        "money": kw['money'],
        "params": {
            **_build_package_params(**kw),
            "cid": 0,
            "ctype": "",
            "duction_money": 0,
            "exchange": 1
        }
    },
    
    'chat-gift': lambda **kw: {
        "platform": "available",
        "type": "chat-gift",
        "money": kw['money'],
        "params": {
            "to": kw['uid'],
            "giftId": kw['giftId'],
            "giftNum": kw['num'],
            "cid": 0,
            "ctype": "",
            "duction_money": 0,
            "version": DEFAULT_VERSION,
            "num": kw['num'],
            "gift_type": "normal",
            "star": kw.get('star', 0),
            "hideErrorToast": 1,
            "all_mic": 0,
            "useCoin": DEFAULT_USE_COIN
        }
    },
    
    'shop-buy': lambda **kw: {
        "platform": 'available',
        "type": 'shop-buy',
        "money": kw['money'] * kw['num'],
        "params": _build_shop_buy_params(**kw)
    },
    
    'shop-buy-box': lambda **kw: {
        "platform": 'available',
        "type": 'shop-buy',
        "money": kw['money'] * kw['num'],
        "params": {
            "num": kw['num'],
            "cid": kw['cid'],
            "price": kw['money'],
            "type": kw['boxType'],
            "opennum": kw['num'],
            "coupon_id": 0,
            "duction_money": 0,
            "version": DEFAULT_VERSION,
            "star": 0,
            "scene": "shop_box",
            "useCoin": DEFAULT_USE_COIN
        }
    },
    
    'coin-shop-buy': lambda **kw: {
        "platform": 'available',
        "type": 'coin-shop-buy',
        "money": kw['money'] * kw['num'],
        "params": {
            "num": kw['num'],
            "cid": kw['cid'],
            "price": kw['money'],
            "coupon_id": 0,
            "duction_money": 0,
            "version": 2,
            "useCoin": -1
        }
    },
    
    'exchange_gold': lambda **kw: {
        "platform": 'available',
        "type": 'exchange_gold',
        "money": 600,
        "params": {
            "type": "exchange_gold"
        }
    },
    
    'defend': lambda **kw: {
        "platform": 'available',
        "type": 'defend',
        "money": kw['money'],
        "params": {
            "defend": 8,
            "to": kw['uid'],
            "cid": 0,
            "duction_money": 0,
            "unified_relation_version": 1,
            "useCoin": DEFAULT_USE_COIN
        }
    },
    
    'shop-buy-crazyspin': lambda **kw: {
        "platform": 'available',
        "type": 'shop-buy',
        "money": 1000,
        "params": {
            "num": 10,
            "cid": 32,
            "price": 100,
            "coupon_id": 0,
            "duction_money": 0,
            "version": DEFAULT_VERSION,
            "gift_scene": "shop",
            "rid": kw['rid'],
            "useCoin": DEFAULT_USE_COIN
        }
    },
    
    'play-crazyspin': lambda **kw: {
        "rid": kw['rid'],
        "draw_type": 10,
        "turntable_type": 1,
    },
    
    'journey_planet_draw': lambda **kw: {
        "platform": "available",
        "type": "journey-planet-draw",
        "money": 1500,
        "params": {
            "jp_id": 1,
            "floor": 1,
            "price": 1500,
            "rid": kw['rid'],
            "useCoin": DEFAULT_USE_COIN
        }
    },
    
    'chat-pay-card': lambda **kw: {
        'platform': 'available',
        'type': 'chat-pay-card',
        'money': '160',
        'params': '{"cid":42598,"num":10,"price":16.0,"useCoin":-1}',
    },
}


def encodeData(payType: str = 'package',
               money: int = 1000,
               rid: str = config.live_role['auto_rid'],
               uid: str = config.rewardUid,
               giftId: int = config.giftId['7'],
               giftType: str = 'normal',
               cid: int = 5,
               boxType: str = 'copper',
               num: int = 1,
               package_cid: int = 0,
               ctype: str = '',
               duction_money: int = 0,
               star: int = 0,
               defend_id: int = 244,
               uids: Optional[Tuple[str, ...]] = None) -> str:
    """
    编码普通场景的消费数据
    
    Args:
        payType: 支付类型
        money: 金额
        rid: 房间 ID
        uid: 用户 ID
        giftId: 礼物 ID
        giftType: 礼物类型
        cid: 优惠券 ID
        boxType: 盒子类型
        num: 数量
        package_cid: 套餐 ID
        ctype: 物品类型
        duction_money: 优惠金额
        star: 星级
        defend_id: 守护 ID
        uids: 用户 ID 元组
        
    Returns:
        编码后的数据字符串
        
    Raises:
        ValueError: payType 不存在时抛出
    """
    if uids is None:
        uids = (str(config.rewardUid), str(config.masterUid))
    
    if payType not in PAY_TYPE_HANDLERS:
        raise ValueError(f'payType "{payType}" is not supported')
    
    handler = PAY_TYPE_HANDLERS[payType]
    data = handler(
        money=money,
        rid=rid,
        uid=str(uid),
        giftId=giftId,
        giftType=giftType,
        cid=cid,
        boxType=boxType,
        num=num,
        package_cid=package_cid,
        ctype=ctype,
        duction_money=duction_money,
        star=star,
        defend_id=defend_id,
        uids=uids
    )
    
    # 特殊处理：defend-break 需要单独编码
    if data.pop('_special_encode', False):
        return urllib.parse.urlencode(data)
    
    return _encode_data_helper(data)


def encodeOverseaData(payType: str = 'package',
                 money: int = 600,
                 rid: str = config.oversea_room['business_joy'],
                 uid: str = config.oversea_testUid,
                 giftId: int = 10,
                 giftType: str = 'normal',
                 cid: int = 5,
                 boxType: str = 'copper',
                 num: int = 1,
                 package_cid: int = 0,
                 ctype: str = '',
                 duction_money: int = 0,
                 star: int = 0,
                 uids: Optional[Tuple[str, ...]] = None) -> str:
    """
    编码海外版平台的消费数据
    
    Args:
        payType: 支付类型
        money: 金额
        rid: 房间 ID
        uid: 用户 ID
        giftId: 礼物 ID
        giftType: 礼物类型
        cid: 优惠券 ID
        boxType: 盒子类型
        num: 数量
        package_cid: 套餐 ID
        ctype: 物品类型
        duction_money: 优惠金额
        star: 星级
        uids: 用户 ID 元组
        
    Returns:
        编码后的数据字符串
        
    Raises:
        ValueError: payType 不存在时抛出
    """
    if uids is None:
        uids = (str(config.oversea_testUid), str(config.oversea_brokerUid))
    
    if payType not in OVERSEA_PAY_TYPE_HANDLERS:
        raise ValueError(f'payType "{payType}" is not supported')
    
    handler = OVERSEA_PAY_TYPE_HANDLERS[payType]
    data = handler(
        money=money,
        rid=rid,
        uid=str(uid),
        giftId=giftId,
        giftType=giftType,
        cid=cid,
        boxType=boxType,
        num=num,
        package_cid=package_cid,
        ctype=ctype,
        duction_money=duction_money,
        star=star,
        uids=uids
    )
    
    return _encode_data_helper(data)


if __name__ == '__main__':
    # 测试示例
    data = encodeData(payType='package-more',
                      num=2,
                      star=8,
                      money=2100,
                      giftId=config.giftId['47'],
                      uids=(str(config.rewardUid), str(config.gsUid)))
    print(data)
