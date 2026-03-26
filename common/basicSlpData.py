import urllib.parse
from caseSlp.config import *


def _encode_data(data):
    """编码数据为URL格式"""
    d = urllib.parse.urlencode(data)
    return d.replace('+', '').replace('%27', '%22')


def _build_base_params(giftId, num, price, giftType, star, cid=0, ctype='', duction_money=0):
    """构建通用参数"""
    return {
        "giftId": giftId,
        "giftNum": num,
        "price": price,
        "cid": cid,
        "ctype": ctype,
        "duction_money": duction_money,
        "version": 2,
        "num": num,
        "gift_type": giftType,
        "star": star,
        "show_pac_man_guide": 1,
        "all_mic": 0,
        "useCoin": -1
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
    """国内Slp消费场景数据编码"""
    
    if payType == 'chat-gift':
        data = {
            "platform": "available",
            "type": "chat-gift",
            "money": money,
            "params": {
                "notify_group_id": 0,
                "to": '{}'.format(uid),
                "giftId": giftId,
                "giftNum": num,
                "cid": 0,
                "ctype": "",
                "duction_money": 0,
                "version": 2,
                "num": num,
                "gift_type": "normal",
                "star": star,
                "show_pac_man_guide": 1,
                "all_mic": 0,
                "useCoin": -1
            }
        }
        return _encode_data(data)

    if payType == 'package':
        data = {
            "platform": "available",
            "type": "package",
            "money": money,
            "params": {
                "rid": rid,
                "uids": '{}'.format(uid),
                "positions": "1",
                "position": -1,
                **_build_base_params(giftId, num, price, giftType, star, package_cid, ctype, duction_money),
                "refer": "",
            }
        }
        return _encode_data(data)

    if payType == 'package-more':
        uid_str = ','.join(uids)
        num_more = len(uids)
        position = ','.join(str(i + 1) for i in range(num_more))
        data = {
            "platform": "available",
            "type": "package",
            "money": money * num * num_more,
            "params": {
                "rid": rid,
                "uids": uid_str,
                "positions": position,
                "position": -1,
                "giftId": giftId,
                "giftNum": num,
                "price": price,
                "cid": 0,
                "ctype": "",
                "duction_money": 0,
                "version": 2,
                "num": num_more * num,
                "gift_type": giftType,
                "useCoin": -1,
                "star": star,
                "show_pac_man_guide": 1,
                "refer": "",
                "all_mic": 0,
            }
        }
        return _encode_data(data)

    if payType == 'package-knightDefend':
        data = {
            "platform": "available",
            "type": "package",
            "money": money,
            "params": {
                "price": price,
                "knight_level": knight_level,
                "duration_level": duration_level,
                "rid": rid,
                "uids": "{}".format(uid),
                "useCoin": -1,
            }
        }
        return _encode_data(data)

    if payType == 'defend':
        data = {
            "platform": 'available',
            "type": 'defend',
            "money": money,
            "params": {
                "defend": defend_id,
                "to": uid,
                "cid": 0,
                "duction_money": 0,
                "unified_relation_version": 1,
                "useCoin": -1
            }
        }
        return _encode_data(data)

    if payType == 'defend-upgrade':
        data = {
            "platform": 'available',
            "type": 'defend-upgrade',
            "money": money,
            "params": {
                "id": "{}".format(defend_id),
                "useCoin": -1
            }
        }
        return _encode_data(data)

    if payType == 'defend-break':
        data = {
            "platform": 'available',
            "type": 'defend-break',
            "money": money,
            "params": {
                "id": "{}".format(defend_id),
                "useCoin": -1
            }
        }
        return _encode_data(data)

    if payType == 'zx_box':
        uid_str = ','.join(uids)
        num_more = len(uids)
        position = ','.join(str(i + 1) for i in range(num_more))
        data = {
            "platform": "available",
            "type": "package",
            "money": price * num_more * num,
            "params": {
                "rid": rid,
                "uids": uid_str,
                "positions": position,
                "position": -1,
                "giftId": giftId,
                "giftNum": num,
                "price": price,
                "cid": 0,
                "ctype": "",
                "duction_money": 0,
                "version": 2,
                "num": num * num_more,
                "gift_type": "normal",
                "star": 0,
                "show_pac_man_guide": 1,
                "refer": "search:room",
                "all_mic": 0,
                "gift_refer": "",
                "useCoin": -1
            }
        }
        return _encode_data(data)

    raise Exception(f'payType {payType} is not supported')


if __name__ == '__main__':
    data = encodeData(
        payType='zx_box',
        num=2,
        giftId=zx_box['6']['gid'],
        price=zx_box['6']['price'],
        uids=('{}'.format(normal_uid), '{}'.format(gsUid))
    )
    print(data)
