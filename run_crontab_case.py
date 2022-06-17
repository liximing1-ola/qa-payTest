# coding=utf-8
import unittest
import time
from common import Logs
from Robot import robot
from common.Config import config
def all_case():
    case_dir = config.BASE_PATH + '/caseLuckyPlay'
    testcase = unittest.TestSuite()
    discover = unittest.defaultTestLoader.discover(case_dir, pattern="test_*", top_level_dir=None)
    testcase.addTests(discover)
    return testcase

def main():
    test_result = unittest.TextTestRunner(verbosity=3).run(all_case())
    now = time.strftime('%Y-%m-%d %H:%M', time.localtime(time.time()))
    des = "用例总数: {}, 失败用例数: {}, 异常用例数: {}" \
        .format(test_result.testsRun, len(test_result.failures), len(test_result.errors))
    Logs.get_log('caseResult_2.log').info(des)
    if len(test_result.failures) == 0 and len(test_result.errors) == 0:
        des = "{}, 用例数:{}, 失败数:{}, 分支:{}".format(now, test_result.testsRun,
                                                 len(test_result.failures) + len(test_result.errors),
                                                 config.codeInfo['bb_git_branch'])
        robot('markdown', des, bot='pt')
    elif len(test_result.failures) >= 1:
        Logs.get_log('failCase.log').error("failures: {}".format(test_result.failures))
        for case, reason in test_result.failures:
            robot('icon', case.id().split('.')[2], bot='pt')
    elif len(test_result.errors) >= 1:
        Logs.get_log('failCase.log').error("error: {}".format(test_result.errors))
        for case, reason in test_result.errors:
            robot('icon', case.id().split('.')[2], bot='pt')


if __name__ == "__main__":
    main()