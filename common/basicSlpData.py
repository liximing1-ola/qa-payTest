import urllib.parse
from caseSlp.config import *


# 国内Slp消费场景
def encodeData(
        payType='package',
        money=giftId['69']['price'] * default_num,
        rid=business_room_rid,  # 商业标准9麦
        uid=rewardUid,
        giftId=giftId['69']['gid'],
        giftType='normal',
        cid=5,
        boxType='copper',
        num=default_num,
        package_cid=0,  # xs_user_commodity的id
        ctype='',
        duction_money=0,
        star=0,
        defend_id=244,
        uids=('{}'.format(rewardUid), '{}'.format(gsUid)),
        knight_level=room_defend['zhenai']['month']['knight_level'],
        duration_level=room_defend['zhenai']['month']['duration_level'],
        price=giftId['69']['price']
):
    if payType == 'chat-gift':
        data = {
            "platform": "available",
            "type": "chat-gift",
            "money": money,
            "params":
                {
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
                },
        }
        print(data)
        d = urllib.parse.urlencode(data)
        data = d.replace('+', '').replace('%27', '%22')
        return data
    if payType == 'package':
        data = {
            "platform": "available",
            "type": "package",
            "money": money,
            "params":
                {
                    "rid": rid,
                    "uids": '{}'.format(uid),
                    "positions": "1",
                    "position": -1,
                    "giftId": giftId,
                    "giftNum": num,
                    "price": price,
                    "cid": package_cid,
                    "ctype": ctype,
                    "duction_money": duction_money,
                    "version": 2,
                    "num": num,
                    "gift_type": "{}".format(giftType),
                    "star": star,
                    "show_pac_man_guide": 1,
                    "refer": "",
                    "all_mic": 0,
                    "useCoin": -1,
                }
        }
        print(data)
        d = urllib.parse.urlencode(data)
        data = d.replace('+', '').replace('%27', '%22')
        return data
    elif payType == 'package-more':
        p = []
        uid = ','.join(uids)
        num_more = len(uids)
        for i in range(len(uids)):
            p.append(str(i + 1))
        position = ','.join(p)
        data = {
            "platform": "available",
            "type": "package",
            "money": money * num * num_more,
            "params":
                {
                    "rid": rid,
                    "uids": '{}'.format(uid),
                    "positions": "{}".format(position),
                    "position": -1,
                    "giftId": giftId,
                    "giftNum": num,
                    "price": price,
                    "cid": 0,
                    "ctype": "",
                    "duction_money": 0,
                    "version": 2,
                    "num": num_more * num,
                    "gift_type": "{}".format(giftType),
                    "useCoin": -1,
                    "star": star,
                    "show_pac_man_guide": 1,
                    "refer": "",
                    "all_mic": 0,
                }
        }
        print(data)
        d = urllib.parse.urlencode(data)
        data = d.replace('+', '').replace('%27', '%22')
        return data
    # elif payType == 'package-exchange':
    #     data = {
    #         "platform": "available",
    #         "type": "package",
    #         "money": money,
    #         "params":
    #             {"rid": rid,
    #              "uids": '{}'.format(uid),
    #              "positions": "1",
    #              "position": -1,
    #              "giftId": giftId,
    #              "giftNum": num,
    #              "price": price,
    #              "cid": 0,
    #              "ctype": "",
    #              "duction_money": 0,
    #              "version": 2,
    #              "num": num,
    #              "gift_type": "{}".format(giftType),
    #              "useCoin": -1,
    #              "star": star,
    #              "show_pac_man_guide": 1,
    #              "refer": "",
    #              "all_mic": 0,
    #              "exchange": 1
    #              }
    #     }
    #     print(data)
    #     d = urllib.parse.urlencode(data)
    #     data = d.replace('+', '').replace('%27', '%22')
    #     return data
    elif payType == 'package-knightDefend':
        data = {
            "platform": "available",
            "type": "package",
            "money": money,
            "params":
                {
                    "price": price,
                    "knight_level": knight_level,
                    "duration_level": duration_level,
                    "rid": rid,
                    "uids": "{}".format(uid),
                    "useCoin": -1,
                }
        }
        print(data)
        d = urllib.parse.urlencode(data)
        data = d.replace('+', '').replace('%27', '%22')
        return data
    # elif payType == 'package-radioDefend':
    #     data = {
    #         "platform": "available",
    #         "type": "package",
    #         "money": money,  # 520
    #         "params":
    #             {"price": price,
    #              "rid": rid,  # business-radio
    #              "uids": '{}'.format(uid),
    #              "positions": "0",
    #              "defend": 3,
    #              "cid": package_cid,
    #              "duction_money": 0,
    #              "useCoin": -1,
    #              }
    #     }
    #     print(data)
    #     d = urllib.parse.urlencode(data)
    #     data = d.replace('+', '').replace('%27', '%22')
    #     return data
    # elif payType == 'chat-gift':
    #     data = {
    #         "platform": "available",
    #         "type": "chat-gift",
    #         "money": money,
    #         "params":
    #             {"notify_group_id": 0,
    #              "to": '{}'.format(uid),
    #              "giftId": giftId,
    #              "giftNum": num,
    #              "cid": 0,
    #              "ctype": "",
    #              "duction_money": 0,
    #              "version": 2,
    #              "num": num,
    #              "gift_type": "normal",
    #              "star": star,
    #              "show_pac_man_guide": 1,
    #              "all_mic": 0,
    #              "useCoin": -1
    #              }
    #     }
    #     print(data)
    #     d = urllib.parse.urlencode(data)
    #     data = d.replace('+', '').replace('%27', '%22')
    #     return data
    # elif payType == 'shop-buy-box':
    #     data = {
    #         "platform": 'available',
    #         "type": 'shop-buy',
    #         "money": money * num,
    #         "params":
    #             {"num": num,
    #              "cid": cid,
    #              "price": price,
    #              "type": "{}".format(boxType),
    #              "opennum": num,
    #              "coupon_id": 0,
    #              "duction_money": 0,
    #              "version": 2,
    #              "star": 4,
    #              "show_pac_man_guide": 0,
    #              "useCoin": -1
    #              }
    #     }
    #     print(data)
    #     d = urllib.parse.urlencode(data)
    #     data = d.replace('+', '').replace('%27', '%22')
    #     return data
    # elif payType == 'shop-buy':
    #     data = {
    #         "platform": 'available',
    #         "type": 'shop-buy',
    #         "money": money * num,
    #         "params":
    #             {"num": num,
    #              "cid": cid,
    #              "price": price,
    #              "coupon_id": 0,
    #              "duction_money": 0,
    #              "version": 2,
    #              "gift_scene": "shop",
    #              "money_type": "money",
    #              "useCoin": -1}
    #     }
    #     print(data)
    #     d = urllib.parse.urlencode(data)
    #     data = d.replace('+', '').replace('%27', '%22')
    #     return data
    elif payType == 'defend':
        data = {
            "platform": 'available',
            "type": 'defend',
            "money": money,
            "params":
                {
                    "defend": defend_id,
                    "to": uid,
                    "cid": 0,
                    "duction_money": 0,
                    "unified_relation_version": 1,
                    "useCoin": -1
                }
        }
        print(data)
        d = urllib.parse.urlencode(data)
        data = d.replace('+', '').replace('%27', '%22')
        return data
    elif payType == 'defend-upgrade':
        data = {
            "platform": 'available',
            "type": 'defend-upgrade',
            "money": money,
            "params":
                {
                    "id": "{}".format(defend_id),  # xs_relation_defend  id
                    "useCoin": -1
                }
        }
        print(data)
        d = urllib.parse.urlencode(data)
        data = d.replace('+', '').replace('%27', '%22')
        return data
    elif payType == 'defend-break':
        data = {
            "platform": 'available',
            "type": 'defend-break',
            "money": money,
            "params":
                {
                    "id": "{}".format(defend_id),  # xs_relation_defend  id
                    "useCoin": -1
                }
        }
        print(data)
        d = urllib.parse.urlencode(data)
        data = d.replace('+', '').replace('%27', '%22')
        return data
    if payType == 'zx_box':  # 甄选礼盒
        p = []
        uid = ','.join(uids)
        num_more = len(uids)
        for i in range(len(uids)):
            p.append(str(i + 1))
        position = ','.join(p)
        data = {
            "platform": "available",
            "type": "package",
            "money": price * num_more * num,  # 单价*人数*单次送礼个数
            "params": {
                "rid": rid,
                "uids": '{}'.format(uid),
                "positions": "{}".format(position),
                "position": -1,
                "giftId": giftId,
                "giftNum": num,
                "price": price,
                "cid": 0,
                "ctype": "",
                "duction_money": 0,
                "version": 2,
                "num": num * num_more,  # 人数*单次送礼个数
                "gift_type": "normal",
                "star": 0,
                "show_pac_man_guide": 1,
                "refer": "search:room",
                "all_mic": 0,
                "gift_refer": "",
                "useCoin": -1
            }
        }
        print(data)
        d = urllib.parse.urlencode(data)
        data = d.replace('+', '').replace('%27', '%22')
        return data
    # elif payType == 'title':
    #     data = {
    #         "platform": "available",
    #         "type": "title",
    #         "money": money,
    #         "params":
    #             {"level": 1,
    #              "num": 1,
    #              "tid": 1,
    #              "cid": 0,
    #              "ctype": "",
    #              "duction_money": 0,
    #              "useCoin": -1,
    #              }
    #     }
    #     print(data)
    #     d = urllib.parse.urlencode(data)
    #     data = d.replace('+', '').replace('%27', '%22')
    #     return data
    # elif payType == 'exchange_gold':
    #     data = {
    #         "platform": 'available',
    #         "type": 'exchange_gold',
    #         "money": '600',
    #         "params": {
    #             "type": "exchange_gold"
    #         }
    #     }
    #     print(data)
    #     d = urllib.parse.urlencode(data)
    #     data = d.replace('+', '').replace('%27', '%22')
    #     return data
    # elif payType == 'unity-game-buy':
    #     data = {
    #         "platform": 'available',
    #         "type": 'unity-game-buy',
    #         "money": money,
    #         "params": {
    #             "amount": 1,
    #             "app_ver": "1.0.0",
    #             "c_id": 10001,
    #             "c_name": "棋子皮肤",
    #             "c_num": 1,
    #             "game_type": "Ludo",
    #             "money_type": "diamond",
    #             "rid": 105707946
    #         }
    #     }
    #     print(data)
    #     d = urllib.parse.urlencode(data)
    #     data = d.replace('+', '').replace('%27', '%22')
    #     return data
    # elif payType == 'pub-drink-buy':
    #     data = {
    #         "platform": 'available',
    #         "type": 'pub-drink-buy',
    #         "money": money,
    #         "params": {
    #             "pub_club_rid": rid,
    #             "menu_id": 6,
    #             "num": 1,
    #             "useCoin": -1,
    #             "gift_type": 'bean',
    #             "refer": "",
    #             "exchange": 1,
    #         }
    #     }
    #     print(data)
    #     d = urllib.parse.urlencode(data)
    #     data = d.replace('+', '').replace('%27', '%22')
    #     return data
    # elif payType == 'deco-present':
    #     data = {
    #         "platform": 'available',
    #         "type": 'deco-present',
    #         "money": money,
    #         "params": {
    #             "num": 1,
    #             "uids": uid,
    #             "money_type": "bean",
    #             "cid": cid,  # 1629
    #             "price": price,
    #             "coupon_id": 0,
    #             "duction_money": 0,
    #             "version": 2,
    #             "useCoin": -1
    #         }
    #     }
    #     print(data)
    #     d = urllib.parse.urlencode(data)
    #     data = d.replace('+', '').replace('%27', '%22')
    #     return data
    # elif payType == 'banban-consume':
    #     data = {
    #         "platform": 'available',
    #         "type": 'banban-consume',
    #         "money": money,
    #         "params":
    #             {"consume_type": "music_order",
    #              "rid": rid,
    #              "order_songs": [{"song_id": 10282, "singer_id": uid}],
    #              "useCoin": -1
    #              }
    #     }
    #     print(data)
    #     d = urllib.parse.urlencode(data)
    #     data = d.replace('+', '').replace('%27', '%22')
    #     return data
    # else:
    #     raise Exception('payType is error')
    #


if __name__ == '__main__':
    uid = gsUid
    rid = gs_soundchat_rid
    data = encodeData(
        payType='zx_box',
        num=2,
        giftId=zx_box['6']['gid'],
        price=zx_box['6']['price'],
        uids=('{}'.format(normal_uid), '{}'.format(gsUid))
    )
    print(data)
