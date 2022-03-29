import requests
import sys
import os
sys.path.append(os.path.split(os.path.abspath(os.path.dirname(__file__)))[0])
from common.Config import config
from common.basicData import encodeData


def ferrisData():
    uid = ('131565025', '131564957')
    uids = ('131565025', '131564957', '131542117', '128439987', '105002120', '105002231', '131541046', '131541047',
            '131542035', '131542036', '131542037', '131542038', '131542039', '131542040')
    headers = {
        'Content-Type': "application/x-www-form-urlencoded",
        'cache-control': "no-cache",
        'Postman-Token': "f7d705b2-cf29-4a4a-81ba-2c8c8d0f5ed5",
        "user-token": '441dYCJG63WGikAgmAg17KtlHsSZyCagZABGIAi3iykaK76GvwGi8xwuFgYdWZLgdup8dOD03bX2HzCbskOoFR2XH6mX5hDuWEJKPXEKKx__2FWbJb5HuSt3U6F'}
    data = encodeData(payType='package-more', uids=uids, rid='200022564', giftId=5, money=100)
    res = requests.post(url=config.pay_url, headers=headers, data=data)
    print(res.json())


if __name__ == '__main__':
    ferrisData()
