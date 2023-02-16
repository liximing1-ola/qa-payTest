import gevent
from gevent import monkey

monkey.patch_all()
import requests
from common.Config import config
from common.sqlScript import mysql
from common import Consts, Logs, method
from common.basicData import encodeData
from common.method import getValue
from common.Session import Session
from common.Request import post_request_session
from common.Assert import assert_equal, assert_code
from time import sleep


class PayConcurrent:

    def ok_test(self):
        url = "https://api-new.yinjietd.com/pay/create?package=com.imbb.banban.android&_ipv=0&_platform=android&_index=1755&_model=SEA-AL10&_timestamp=1676458178&_sign=bfd82709d13088a721188e59c0342638"

        payload = 'platform=available&type=package&money=100&params=%7B%22rid%22%3A118491893%2C%22uids%22%3A%22114820541%22%2C%22positions%22%3A%221%22%2C%22position%22%3A3%2C%22giftId%22%3A69%2C%22giftNum%22%3A1%2C%22price%22%3A100%2C%22cid%22%3A755481761%2C%22ctype%22%3A%22gift%22%2C%22duction_money%22%3A0%2C%22version%22%3A2%2C%22num%22%3A1%2C%22gift_type%22%3A%22normal%22%2C%22star%22%3A0%2C%22show_pac_man_guide%22%3A1%2C%22refer%22%3A%22flow_friendplaying%3Aroom%22%2C%22all_mic%22%3A0%2C%22gift_refer%22%3A%22%22%2C%22useCoin%22%3A-1%7D'
        headers = {
            'user-token': '13d3JsaFNn__2FaL8dXrav8b0IosTROVP7yIOnje3SGB92bMDtxahkSuWX__2FW8ZU047__2BCfvP0YMe5OhDTzy3XMULDNY1__2BHZCh1rk__2BXr7sTRmDVUA39IAzx09eqQQ',
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        print(response.text)

    def ok_test2(self):
        threads = []
        for i in range(20):
            thread = gevent.spawn(self.ok_test)
            threads.append(thread)
        gevent.joinall(threads)


if __name__ == '__main__':
    p = PayConcurrent()
    p.ok_test2()
