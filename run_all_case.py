# coding=utf-8
import unittest
import time
from common import Logs, method, Consts, Config
from autoGitPull import autoGitPull, writeUpdateTime
from Robot import robot
def all_case():
    case_dir = {"bb_dir": '/home/banban-1/payTest/case',
                "pt_dir": '/root/payTest/case'}
    testcase = unittest.TestSuite()
    discover = unittest.defaultTestLoader.discover(case_dir['bb_dir'],  # 指定待执行用例的目录
                                                   pattern="test_.py",
                                                   top_level_dir=None)
    testcase.addTests(discover)
    return testcase

def main():
    if autoGitPull():
        writeUpdateTime(str(int(time.time())))
        test_result = unittest.TextTestRunner(verbosity=3).run(all_case())
        Consts.endTime = time.time()
        des = "用例总数: {}, 失败用例数: {}, 异常用例数: {}" \
            .format(test_result.testsRun, len(test_result.failures), len(test_result.errors))
        Logs.get_log('caseResult.log').info(des)
        case_list = method.dictToList(Consts.case_list)
        case_list_2 = method.dictToList(Consts.case_list_b)
        use_time = str(int(Consts.endTime - Consts.startTime)) + 's'
        if len(test_result.failures) == 0 and len(test_result.errors) == 0:
            des = "{}\n".format(case_list)
            des_2 = "{}\n用例数: {}, 失败数: {}, 总耗时: {}, 代码分支：{}".format(
                case_list_2, test_result.testsRun,
                len(test_result.failures) + len(test_result.errors),
                use_time,
                Config.config.bb_user['bb_git_branch'])
            robot('markdown', des)
            time.sleep(0.1)
            robot('markdown', des_2)
        elif len(test_result.failures) >= 1:
            Logs.get_log('failCase.log').error("failures: {}".format(test_result.failures))
            robot('success', des)
            for case, reason in test_result.failures:
                robot('fail', Consts.fail_case_reason[0], title=case.id())
                break
        elif len(test_result.errors) >= 1:
            Logs.get_log('failCase.log').error("error: {}".format(test_result.errors))
            for case, reason in test_result.errors:
                robot('fail', reason, case.id())
                break
    else:
        Logs.get_log('runCode.log').info('NoRun')


if __name__ == "__main__":
    main()
