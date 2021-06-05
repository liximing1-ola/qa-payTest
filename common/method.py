import requests
import random
def dictToList(result_dict):
    list_case = []
    for k, v in result_dict.items():
        list_case.append(
            'checkPoint:  <font color="comment">{}</font>,  结果: <font color=\"info\">{}</font>'.format(k, v))
    case = '\n'.join(list_case)
    return case

def getImage():
    url = 'https://www.mxnzp.com/api/image/girl/list/random?app_id=kilmc0p2ytsnawyp&app_secret=bnNoWElSVDBYbEhsc1EvYVM2WnVnZz09'
    res = requests.get(url)
    res.raise_for_status()
    res = res.json()
    if res['code'] == 1:
        return res['data'][0]['imageUrl']
    else:
        icon = random.randint(1, 140)
        return 'http://xs-image.oss-cn-hangzhou.aliyuncs.com/static/gift_big/{}.png'.format(icon)

def getKeys(data):
    keysAll_list = []

    def getkeys(json_data):  # 遍历json所有key
        if type(json_data) == type({}):
            keys = json_data.keys()
            for key in keys:
                value = json_data.get(key)
                if type(value) != type({}) and type(value) != type([]):
                    keysAll_list.append(key)
                elif type(value) == type({}):
                    keysAll_list.append(key)
                    getkeys(value)
                elif type(value) == type([]):
                    keysAll_list.append(key)
                    for para in value:
                        if type(para) == type({}) or type(para) == type([]):
                            getkeys(para)
                        else:
                            keysAll_list.append(para)
    getkeys(data)
    return keysAll_list

def isExtend(data, tagkey):
    if type(data) != type({}):
        print('please input a json!')
    else:
        key_list = getKeys(data)
        for key in key_list:
            if key == tagkey:
                return True
    return False


if __name__ == '__main__':
    case_dict = {'验证余额不足时，私聊一对一打赏': 'pass', '验证余额足够时，私聊一对一打赏': 'pass', '验证开通个人守护的收益分成': 'pass',
                 '验证余额不足时，房间一对一打赏': 'pass', '验证余额足够时，直播类型房间一对一打赏': 'pass', '验证余额足够时，非直播类型房间一对一打赏': 'pass',
                 '验证商城购买单个道具时逻辑': 'pass', '验证商城购买多个道具时逻辑': 'pass', '验证商城购买的道具在房间内赠送给其他人逻辑': 'pass',
                 '验证商城购买的道具在房间内赠送给他人不足的逻辑': 'pass', '验证爵位开通及返钱到余额': 'pass', '验证爵位续费及返钱到余额': 'pass'}
    # print(dictToList(case_dict))
    print(isExtend(case_dict, '验证余额不足时，私聊一对一打赏'))
