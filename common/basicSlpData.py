# coding=utf-8
"""
SLP 消费数据编码模块

使用字典映射替代 if-chain 分支，与 basicData.py 保持一致的 handler 模式。
"""
import logging
import urllib.parse
from typing import Optional, Tuple

from caseSlp.config import (
    business_room_rid, default_num, giftId, gsUid, normal_uid, rewardUid,
    room_defend, zx_box,
)

logger = logging.getLogger(__name__)


def _encode_data(data):
    """编码数据为URL格式"""
    d = urllib.parse.urlencode(data)
    return d.replace('+', '').replace('%27', '%22')


def _build_base_params(gift_id, num, price, gift_type, star, cid=0, ctype='', duction_money=0):
    """构建 package 类场景的通用 params 字段"""
    return {
        "giftId": gift_id,
        "giftNum": num,
        "price": price,
        "cid": cid,
        "ctype": ctype,
        "duction_money": duction_money,
        "version": 2,
        "num": num,
        "gift_type": gift_type,
        "star": star,
        "show_pac_man_guide": 1,
        "all_mic": 0,
        "useCoin": -1
    }


# ============ Handler 工厂函数 ============

def _handler_chat_gift(**kw):
    """聊天礼物"""
    return {
        "platform": "available",
        "type": "chat-gift",
        "money": kw['money'],
        "params": {
            "notify_group_id": 0,
            "to": str(kw['uid']),
            "giftId": kw['giftId'],
            "giftNum": kw['num'],
            "cid": 0,
            "ctype": "",
            "duction_money": 0,
            "version": 2,
            "num": kw['num'],
            "gift_type": "normal",
            "star": kw['star'],
            "show_pac_man_guide": 1,
            "all_mic": 0,
            "useCoin": -1
        }
    }


def _handler_package(**kw):
    """单人套餐打赏"""
    return {
        "platform": "available",
        "type": "package",
        "money": kw['money'],
        "params": {
            "rid": kw['rid'],
            "uids": str(kw['uid']),
            "positions": "1",
            "position": -1,
            **_build_base_params(
                kw['giftId'], kw['num'], kw['price'],
                kw['giftType'], kw['star'], kw['package_cid'],
                kw['ctype'], kw['duction_money'],
            ),
            "refer": "",
        }
    }


def _build_multi_uid_params(**kw):
    """构建多人打赏的公共 params（package-more / zx_box 共用）"""
    uid_str = ','.join(kw['uids'])
    num_more = len(kw['uids'])
    position = ','.join(str(i + 1) for i in range(num_more))
    return {
        "rid": kw['rid'],
        "uids": uid_str,
        "positions": position,
        "position": -1,
        "giftId": kw['giftId'],
        "giftNum": kw['num'],
        "price": kw['price'],
        "cid": 0,
        "ctype": "",
        "duction_money": 0,
        "version": 2,
        "num": kw['num'] * num_more,
        "gift_type": kw['giftType'],
        "star": kw['star'],
        "show_pac_man_guide": 1,
        "all_mic": 0,
        "useCoin": -1,
    }


def _handler_package_more(**kw):
    """多人套餐打赏"""
    num_more = len(kw['uids'])
    return {
        "platform": "available",
        "type": "package",
        "money": kw['money'] * kw['num'] * num_more,
        "params": {
            **_build_multi_uid_params(**kw),
            "refer": "",
        }
    }


def _handler_package_knight_defend(**kw):
    """骑士守护套餐"""
    return {
        "platform": "available",
        "type": "package",
        "money": kw['money'],
        "params": {
            "price": kw['price'],
            "knight_level": kw['knight_level'],
            "duration_level": kw['duration_level'],
            "rid": kw['rid'],
            "uids": str(kw['uid']),
            "useCoin": -1,
        }
    }


def _handler_defend(**kw):
    """守护关系"""
    return {
        "platform": 'available',
        "type": 'defend',
        "money": kw['money'],
        "params": {
            "defend": kw['defend_id'],
            "to": kw['uid'],
            "cid": 0,
            "duction_money": 0,
            "unified_relation_version": 1,
            "useCoin": -1
        }
    }


def _handler_defend_upgrade(**kw):
    """守护升级"""
    return {
        "platform": 'available',
        "type": 'defend-upgrade',
        "money": kw['money'],
        "params": {
            "id": str(kw['defend_id']),
            "useCoin": -1
        }
    }


def _handler_defend_break(**kw):
    """守护解除"""
    return {
        "platform": 'available',
        "type": 'defend-break',
        "money": kw['money'],
        "params": {
            "id": str(kw['defend_id']),
            "useCoin": -1
        }
    }


def _handler_zx_box(**kw):
    """真心话大冒险箱子"""
    num_more = len(kw['uids'])
    return {
        "platform": "available",
        "type": "package",
        "money": kw['price'] * num_more * kw['num'],
        "params": {
            **_build_multi_uid_params(**kw),
            "refer": "search:room",
            "gift_refer": "",
        }
    }


# 支付类型处理器映射表
PAY_TYPE_HANDLERS = {
    'chat-gift': _handler_chat_gift,
    'package': _handler_package,
    'package-more': _handler_package_more,
    'package-knightDefend': _handler_package_knight_defend,
    'defend': _handler_defend,
    'defend-upgrade': _handler_defend_upgrade,
    'defend-break': _handler_defend_break,
    'zx_box': _handler_zx_box,
}


def encodeData(
        payType='package',
        money=giftId['69']['price'] * default_num,
        rid=business_room_rid,
        uid=rewardUid,
        giftId=giftId['69']['gid'],
        giftType='normal',
        cid=5,
        boxType='copper',
        num=default_num,
        package_cid=0,
        ctype='',
        duction_money=0,
        star=0,
        defend_id=244,
        uids=('{}'.format(rewardUid), '{}'.format(gsUid)),
        knight_level=room_defend['zhenai']['month']['knight_level'],
        duration_level=room_defend['zhenai']['month']['duration_level'],
        price=giftId['69']['price']
):
    """国内Slp消费场景数据编码

    Args:
        payType: 支付类型（见 PAY_TYPE_HANDLERS）
        money: 金额
        rid: 房间 ID
        uid: 用户 ID
        giftId: 礼物 ID
        giftType: 礼物类型
        cid: 优惠券 ID
        boxType: 盒子类型
        num: 数量
        package_cid: 套餐 CID
        ctype: 物品类型
        duction_money: 优惠金额
        star: 星级
        defend_id: 守护 ID
        uids: 用户 ID 元组（多人场景）
        knight_level: 骑士等级
        duration_level: 持续等级
        price: 单价

    Returns:
        编码后的数据字符串

    Raises:
        ValueError: payType 不存在时抛出
    """
    handler = PAY_TYPE_HANDLERS.get(payType)
    if not handler:
        raise ValueError(f'payType "{payType}" is not supported')

    data = handler(
        money=money, rid=rid, uid=uid, giftId=giftId,
        giftType=giftType, cid=cid, boxType=boxType, num=num,
        package_cid=package_cid, ctype=ctype, duction_money=duction_money,
        star=star, defend_id=defend_id, uids=uids,
        knight_level=knight_level, duration_level=duration_level,
        price=price,
    )
    return _encode_data(data)


if __name__ == '__main__':
    data = encodeData(
        payType='zx_box',
        num=2,
        giftId=zx_box['6']['gid'],
        price=zx_box['6']['price'],
        uids=('{}'.format(normal_uid), '{}'.format(gsUid))
    )
    logger.info(data)
