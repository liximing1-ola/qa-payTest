import requests
import sys
import os
sys.path.append(os.path.split(os.path.abspath(os.path.dirname(__file__)))[0])
from common.Config import config
from common.basicData import encodeData
from common.sqlScript import mysql
def ferrisData():
    uids = mysql.getUids(50)
    token = 'f1e7Y__2F61q5JZ6yGwIfuiqa__2FjoNuMpm__2BumZl0y0__2BkHfTGiG8VNqi7nBlnlqIz__2BitjLGqVUWnFtiVsQ4omz3dRRguKxDUs3GQrAWnk0PxIlnH2VBfFKKJwtPKx'
    print(uids)
    headers = {
        'Content-Type': "application/x-www-form-urlencoded",
        'cache-control': "no-cache",
        'Postman-Token': "f7d705b2-cf29-4a4a-81ba-2c8c8d0f5ed5",
        "user-token": token
    }
    data = encodeData(payType='package-more', uids=uids, rid='200022564', giftId=88, money=52000)
    res = requests.post(url=config.pay_url, headers=headers, data=data)
    print(res.json())


if __name__ == '__main__':
    ferrisData()