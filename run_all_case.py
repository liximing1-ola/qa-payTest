# coding=utf-8
import unittest
import os
import requests
import random
import time
from Common import logs
from autoGitPull import writeUpdateTime, autoGitPull
def all_case():
    # case_dir = os.path.join(os.getcwd(), "Case")   # 待执行用例的目录
    testcase = unittest.TestSuite()
    discover = unittest.defaultTestLoader.discover("/home/banban-1/payTest/Case",
                                                   pattern="test_pay_package.py",
                                                   top_level_dir=None)
    testcase.addTests(discover)  # 直接加载 discover
    return testcase

def main():
    if autoGitPull():
        test_result = unittest.TextTestRunner(verbosity=2).run(all_case())
        writeUpdateTime(str(int(time.time())))
        now = time.strftime('%F-%H:%M', time.localtime(time.time()))
        logs.get_log('runCaseTime.log').info("执行用例总数: {}, 失败用例总数: {}, 执行时间: {}"
                                             .format(test_result.testsRun, len(test_result.failures), now))
        logs.get_log('failCase.log').error(test_result.failures)
        for case, reason in test_result.failures:
            if len(test_result.failures) > 0:
               # robot(case.id())
                break
    else:
        pass


def robot(des, ):
    url = 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=f9d916cb-6b93-4389-8aa4-f51c755faa0e'
    headers = {'Content-Type': 'application/json'}
    now = time.strftime('%F:%H:%M', time.localtime(time.time()))
    title = "警告!内测支付异常__{}".format(now)
    des = des
    icon = getImage()
    data = {
        "msgtype": "news",
        "news": {
            "articles": [
                {
                    "title": title,
                    "description": des,
                    "url": "https://www.baidu.com/",
                    "picurl": icon,
                }
            ]
        }
    }
    r = requests.post(
        url,
        headers=headers, json=data)
    if r.status_code == 200 and r.text.find('ok'):
        data = {
            "msgtype": "text",
            "text": {
                "mentioned_mobile_list": ["@all"]
            }
        }
        requests.post(url, headers=headers, json=data)

def getImage():
    url = 'https://www.mxnzp.com/api/image/girl/list/random?app_id=kilmc0p2ytsnawyp&' \
          'app_secret=bnNoWElSVDBYbEhsc1EvYVM2WnVnZz09'
    res = requests.get(url)
    res.raise_for_status()
    res = res.json()
    if res['code'] == 1:
        return res['data'][0]['imageUrl']
    else:
        icon = random.randint(1, 140)
        return 'http://xs-image.oss-cn-hangzhou.aliyuncs.com/static/gift_big/{}.png'.format(icon)


if __name__ == "__main__":
    main()