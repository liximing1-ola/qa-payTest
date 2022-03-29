from common.Config import config
from common.basicData import encodeData
import requests
def ferrisData():
    uids=('131565025', '131564957', '131542117', '128439987', '105002120', '105002231')
    headers = {
        'Content-Type': "application/x-www-form-urlencoded",
        'cache-control': "no-cache",
        'Postman-Token': "f7d705b2-cf29-4a4a-81ba-2c8c8d0f5ed5",
        "user-token": '441dYCJG63WGikAgmAg17KtlHsSZyCagZABGIAi3iykaK76GvwGi8xwuFgYdWZLgdup8dOD03bX2HzCbskOoFR2XH6mX5hDuWEJKPXEKKx__2FWbJb5HuSt3U6F'}
    data = encodeData(payType='package-more', uids=uids)
    res = requests.post(url=config.pay_url, headers=headers, data=data)
    print(res)


if __name__=='__main__':
    ferrisData()