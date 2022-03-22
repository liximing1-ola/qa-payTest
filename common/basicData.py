import urllib.parse

def encodeData(payType='package', money=1000, rid=193185484, uid=105002331, giftId=7, giftType='normal',
               cid=5, boxType='copper', num=1, package_cid=0, ctype='', duction_money=0, star=0, uids=('105002312', '100500205')):

    if payType == 'package':
        data = {
            "platform": "available",
            "type": "package",
            "money": money,
            "params":
                {"rid": rid,
                 "uids": '{}'.format(uid),
                 "positions": "1",
                 "position": -1,
                 "giftId": giftId,
                 "giftNum": num,
                 "price": money,
                 "cid": package_cid,
                 "ctype": ctype,
                 "duction_money": duction_money,
                 "version": 2,
                 "num": num,
                 "gift_type": "{}".format(giftType),
                 "useCoin": -1,
                 "star": star,
                 "show_pac_man_guide": 1,
                 "refer": "",
                 "all_mic": 0,
                 }
        }
        d = urllib.parse.urlencode(data)
        data = d.replace('+', '').replace('%27', '%22')
        return data
    elif payType == 'package-more':
        p = []
        uid = ','.join(uids)
        num_more = len(uids)
        for i in range(len(uids)):
            p.append(str(i+1))
        position = ','.join(p)
        data = {
            "platform": "available",
            "type": "package",
            "money": money * num * num_more,
            "params":
                {"rid": rid,
                 "uids": '{}'.format(uid),
                 "positions": "{}".format(position),
                 "position": -1,
                 "giftId": giftId,
                 "giftNum": num,
                 "price": money,
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
        d = urllib.parse.urlencode(data)
        data = d.replace('+', '').replace('%27', '%22')
        return data
    elif payType == 'package-exchange':
        data = {
            "platform": "available",
            "type": "package",
            "money": money,
            "params":
                {"rid": rid,
                 "uids": '{}'.format(uid),
                 "positions": "1",
                 "position": -1,
                 "giftId": giftId,
                 "giftNum": num,
                 "price": money,
                 "cid": 0,
                 "ctype": "",
                 "duction_money": 0,
                 "version": 2,
                 "num": num,
                 "gift_type": "{}".format(giftType),
                 "useCoin": -1,
                 "star": star,
                 "show_pac_man_guide": 1,
                 "refer": "",
                 "all_mic": 0,
                 "exchange": 1
                 }
        }
        d = urllib.parse.urlencode(data)
        data = d.replace('+', '').replace('%27', '%22')
        return data
    elif payType == 'package-knightDefend':
        data = {
            "platform": "available",
            "type": "package",
            "money": money,
            "params":
                {"price": money,
                 "knight_level": 2,
                 "duration_level": 2,
                 "rid": rid,
                 "uids": "{}".format(uid),
                 "useCoin": -1,
                 }
        }
        d = urllib.parse.urlencode(data)
        data = d.replace('+', '').replace('%27', '%22')
        return data
    elif payType == 'chat-gift':
        data = {
            "platform": "available",
            "type": "chat-gift",
            "money": money,
            "params":
                {"notify_group_id": 0,
                 "to": '{}'.format(uid),
                 "giftId": giftId,
                 "giftNum": num,
                 "cid": 0,
                 "ctype": "",
                 "duction_money": 0,
                 "version": 2,
                 "num": num,
                 "gift_type": "normal",
                 "star": 0,
                 "show_pac_man_guide": 1,
                 "all_mic": 0,
                 "useCoin": -1
                 }
        }
        d = urllib.parse.urlencode(data)
        data = d.replace('+', '').replace('%27', '%22')
        return data
    elif payType == 'shop-buy-box':
        data = {
            "platform": 'available',
            "type": 'shop-buy',
            "money": money*num,
            "params":
                {"num": num,
                 "cid": cid,
                 "price": money,
                 "type": "{}".format(boxType),
                 "opennum": num,
                 "coupon_id": 0,
                 "duction_money": 0,
                 "version": 2,
                 "star": 4,
                 "show_pac_man_guide": 0,
                 "useCoin": -1
                 }
        }
        d = urllib.parse.urlencode(data)
        data = d.replace('+', '').replace('%27', '%22')
        return data
    elif payType == 'shop-buy':
        data = {
            "platform": 'available',
            "type": 'shop-buy',
            "money": money*num,
            "params":
                {"num": num,
                 "cid": cid,
                 "price": money,
                 "coupon_id": 0,
                 "duction_money": 0,
                 "version": 2,
                 "gift_scene": "shop",
                 "money_type": "money",
                 "useCoin": -1}
        }
        d = urllib.parse.urlencode(data)
        data = d.replace('+', '').replace('%27', '%22')
        return data
    elif payType == 'defend':
        data = {
            "platform": 'available',
            "type": 'defend',
            "money": money,
            "params":
                {"defend": 2,
                 "to": uid,
                 "cid": 0,
                 "duction_money": 0,
                 "unified_relation_version": 1,
                 "useCoin": -1
                 }
        }
        d = urllib.parse.urlencode(data)
        data = d.replace('+', '').replace('%27', '%22')
        return data
    elif payType == 'title':
        data = {
            "platform": "available",
            "type": "title",
            "money": money,
            "params":
                {"level": 1,
                 "num": 1,
                 "tid": 1,
                 "cid": 0,
                 "ctype": "",
                 "duction_money": 0,
                 "useCoin": -1,
                 }
        }
        d = urllib.parse.urlencode(data)
        data = d.replace('+', '').replace('%27', '%22')
        return data
    elif payType == 'exchange_gold':
        data = {
            "platform": 'available',
            "type": 'exchange_gold',
            "money": '600',
            "params": {
                "type": "exchange_gold"
            }
        }
        d = urllib.parse.urlencode(data)
        data = d.replace('+', '').replace('%27', '%22')
        return data
    elif payType == 'unity-game-buy':
        data = {
            "platform": 'available',
            "type": 'unity-game-buy',
            "money": money,
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
        }
        d = urllib.parse.urlencode(data)
        data = d.replace('+', '').replace('%27', '%22')
        return data
    elif payType == 'pub-drink-buy':
        data = {
            "platform": 'available',
            "type": 'pub-drink-buy',
            "money": money,
            "params": {
                "pub_club_rid": rid,
                "menu_id": 6,
                "num": 1,
                "useCoin": -1,
                "gift_type": 'bean',
                "refer": "",
                "exchange": 1,
            }
        }
        d = urllib.parse.urlencode(data)
        data = d.replace('+', '').replace('%27', '%22')
        return data
    elif payType == 'deco-present':
        data = {
            "platform": 'available',
            "type": 'deco-present',
            "money": money,
            "params": {
                "num": 1,
                "uids": uid,
                "money_type": "bean",
                "cid": cid,  # 1629
                "price": money,
                "coupon_id": 0,
                "duction_money": 0,
                "version": 2,
                "useCoin": -1
            }
        }
        d = urllib.parse.urlencode(data)
        data = d.replace('+', '').replace('%27', '%22')
        return data
    else:
        raise Exception('payType is error')


if __name__ == '__main__':
    encodeData(payType='package-knightDefend', money=28800, uid=100000000,
                                    rid=100000000)