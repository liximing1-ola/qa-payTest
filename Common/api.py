# 内网打印调试
def errorMsg(res):
    if res['body']['success'] != 1:
        print(res['body'])
    else:
        print(res)

def dictToList(case_dict):
    list_case = []
    for k, v in case_dict.items():
        list_case.append('Case: {}, 结果: {}'.format(k, v))

    case = '\n'.join(list_case)
    return case


if __name__ == '__main__':
    case_dict = {'验证余额不足时，私聊一对一打赏': 'pass', '验证余额足够时，私聊一对一打赏': 'pass', '验证开通个人守护的收益分成': 'pass',
                 '验证余额不足时，房间一对一打赏': 'pass', '验证余额足够时，直播类型房间一对一打赏': 'pass', '验证余额足够时，非直播类型房间一对一打赏': 'pass',
                 '验证商城购买单个道具时逻辑': 'pass', '验证商城购买多个道具时逻辑': 'pass', '验证商城购买的道具在房间内赠送给其他人逻辑': 'pass',
                 '验证商城购买的道具在房间内赠送给他人不足的逻辑': 'pass', '验证爵位开通及返钱到余额': 'pass', '验证爵位续费及返钱到余额': 'pass'}

    print(dictToList(case_dict))