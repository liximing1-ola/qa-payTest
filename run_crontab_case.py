# coding=utf-8
import unittest
import time
from common import Logs, method
from Robot import robot
from common import Consts
from common import Config
def all_case():
    case_dir = '/home/banban-1/payTest/case'
    testcase = unittest.TestSuite()
    discover = unittest.defaultTestLoader.discover(case_dir, pattern="test_pay_package.py", top_level_dir=None)
    testcase.addTests(discover)
    return testcase

def main():
    test_result = unittest.TextTestRunner(verbosity=3).run(all_case())
    des = "定时任务执行数: {}, 失败用例数: {}, 异常用例数: {}".format(test_result.testsRun, len(test_result.failures), len(test_result.errors))
    Logs.get_log('caseResult_2.log').info(des)
    if len(test_result.failures) == 0 and len(test_result.errors) == 0:
        des = "用例数: {}, 失败数: {}, 分支：{}".format(test_result.testsRun,
                                                                       len(test_result.failures) + len(test_result.errors),
                                                                       Config.config.bb_test['bb_git_branch'])
        robot('markdown', des, bot='test')
    elif len(test_result.failures) >= 1:
        Logs.get_log('failCase.log').error("failures: {}".format(test_result.failures))
        time.sleep(0.5)
        print(set(Consts.fail_case_reason))
        robot('success', des)
        for case, reason in test_result.failures:
            print(case, reason)
            robot('icon', Consts.fail_case_reason, title=case.id())
    elif len(test_result.errors) >= 1:
        Logs.get_log('failCase.log').error("error: {}".format(test_result.errors))
        for case, reason in test_result.errors:
            print(case, reason)
            robot('icon', reason, case.id())


if __name__ == "__main__":
    main()