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
    des = "定时脚本执行数: {}, 失败用例数: {}, 异常用例数: {}".format(test_result.testsRun, len(test_result.failures), len(test_result.errors))
    Logs.get_log('caseResult_2.log').info(des)
    case_list=method.dictToList(Consts.CASE_LIST)
    use_time=str(int(Consts.endTime-Consts.startTime)) + 's'
    if len(test_result.failures) == 0 and len(test_result.errors) == 0:
        des = "{}\n用例数: {}, 失败数: {}, 执行时间: {}, 执行分支：{}".format(case_list, test_result.testsRun,
                                                                       len(test_result.failures) + len(test_result.errors),
                                                                       use_time, Config.config.bb_test['bb_git_branch'])
        robot('markdown', des, bot='test')
    elif len(test_result.failures) >= 1:
        Logs.get_log('failCase.log').error("failures: {}".format(test_result.failures))
        time.sleep(0.5)
        print(set(Consts.fail_case_reason))
        robot('success', des)
        for case, reason in test_result.failures:
            robot('icon', set(Consts.fail_case_reason), title=case.id(), bot='test')
    elif len(test_result.errors) >= 1:
        Logs.get_log('failCase.log').error("error: {}".format(test_result.errors))
        for case, reason in test_result.errors:
            robot('icon', reason, case.id(), bot='test')


if __name__ == "__main__":
    main()