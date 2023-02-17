import gevent
from gevent import monkey

monkey.patch_all()
import requests
from common.basicData import encodeData


class PayConcurrent:
    url = "https://api-new.yinjietd.com/pay/create?package=com.imbb.banban.android&_ipv=0&_platform=android&_index=1755&_model=SEA-AL10&_timestamp=1676458178&_sign=bfd82709d13088a721188e59c0342638"
    commodity_id = 'https://api-new.yinjietd.com/commodity/userList?version=3&type=gift&package=com.imbb.banban.android&_ipv=0&_platform=android&_index=157&_model=SEA-AL10&_timestamp=1676621169&_sign=fba57be89a5882903e2458d55017145d'

    def release_test(self):
        payload = encodeData(payType='package',
                             rid=118491893,
                             uid=114820541,
                             giftId=694,  # 修改id
                             money=30,
                             package_cid=754946029,  # 修改id
                             ctype='gift')
        headers = {
            'user-token': '13d3JsaFNn__2FaL8dXrav8b0IosTROVP7yIOnje3SGB92bMDtxahkSuWX__2FW8ZU047__2BCfvP0YMe5OhDTzy3XMULDNY1__2BHZCh1rk__2BXr7sTRmDVUA39IAzx09eqQQ',
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        response = requests.request("POST", self.url, headers=headers, data=payload)
        print(response.json())

    def release_test2(self):
        threads = []
        for i in range(20):
            thread = gevent.spawn(self.release_test)
            threads.append(thread)
        gevent.joinall(threads)

    def getCommodityId(self):
        res = requests.get(self.commodity_id)
        print(res)


if __name__ == '__main__':
    p = PayConcurrent()
    # p.release_test2()
    p.getCommodityId()
