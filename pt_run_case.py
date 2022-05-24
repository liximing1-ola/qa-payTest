# coding=utf-8
import unittest
import time
from common import Logs, method
from pt_autoGitPull import autoGitPull, updateTime
from Robot import robot
from common import Consts
def all_case():
    case_dir = {"pt_dir": '/root/payTest/caseOversea'}
    testcase = unittest.TestSuite()
    discover = unittest.defaultTestLoader.discover(case_dir['pt_dir'],
                                                   pattern="test_*",
                                                   top_level_dir=None)
    testcase.addTests(discover)
    return testcase

def main():
    if autoGitPull():
        test_result = unittest.TextTestRunner(verbosity=3).run(all_case())
        updateTime('write', now=str(int(time.time())))
        des = "PT:执行用例数: {}, 失败用例数: {}, 异常用例数: {}" \
            .format(test_result.testsRun, len(test_result.failures), len(test_result.errors))
        Logs.get_log('caseResult.log').info(des)
        case_list=method.dictToList(Consts.case_list)
        if len(test_result.failures) == 0 and len(test_result.errors) == 0:
            des = "PT:执行用例数: {}, 失败用例数: {}, 异常用例数: {}, 执行结果如下:\n {}" \
                .format(test_result.testsRun, len(test_result.failures), len(test_result.errors), case_list)
            time.sleep(2)
            robot('markdown', des, bot='PT')
        elif len(test_result.failures) >= 1:
            Logs.get_log('failCase.log').error("failures: {}".format(test_result.failures))
            time.sleep(2)
            robot('success', des, bot='PT')
            for case, reason in test_result.failures:
                robot('fail', set(Consts.fail_case_reason), title=case.id(), bot='PT')
                break
        elif len(test_result.errors) >= 1:
            Logs.get_log('failCase.log').error("error: {}".format(test_result.errors))
            for case, reason in test_result.errors:
                robot('fail', reason, case.id(), bot='PT')
                break
    else:
        pass


if __name__ == "__main__":
    main()