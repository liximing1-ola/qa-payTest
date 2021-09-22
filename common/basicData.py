import urllib.parse

def encodeData(payType='package', money=1000, rid=193185484, uid=105002331, giftId=7, giftType='normal',
               cid=5, boxType='copper', num=1):

    if payType=='packages':
        data = {
            "platform": "available",
            "type": "packages",
            "money": money,
            "params":
                {"rid": rid,
                 "uids": '{}'.format(uid),
                 "positions": "1",
                 "position": -1,
                 "giftId": giftId,
                 "giftNum": 1,
                 "price": money,
                 "cid": 0,
                 "ctype": "",
                 "duction_money": 0,
                 "version": 2,
                 "num": 1,
                 "gift_type": "{}".format(giftType),
                 "useCoin": -1,
                 "exchange": 1,
                 }
        }
        d = urllib.parse.urlencode(data)
        data = d.replace('+', '').replace('%27', '%22')
        print(data)
        return data
    elif payType == 'chat-gift':
        pass
    elif payType=='shop-buy':
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
    elif payType=='defend':
        data = {
            "platform": 'available',
            "type": 'defend',
            "money": money,
            "params":
                {"defend": 1,
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
    elif payType=='title':
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
    elif payType=='exchange_gold':
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
    elif payType=='unity-game-buy':
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
    elif payType=='pub-drink-buy':
        data = {}
        d = urllib.parse.urlencode(data)
        data = d.replace('+', '').replace('%27', '%22')
        return data
    else:
        raise Exception('need payType')





if __name__ == '__main__':
    encodeData(payType='shop-buy', money=100, cid=329, boxType='')