# coding=utf-8
import unittest
import time
from common import Logs, method, Consts, Config
from autoGitPull import autoGitPull, writeUpdateTime
from Robot import robot
import threading
def all_case():
    # win 路径
    # case_dir = os.path.join(os.getcwd(), "Case")
    # linux
    case_dir = {"bb_dir": '/home/banban-1/payTest/case',
                "pt_dir": '/root/payTest/case'}
    testcase = unittest.TestSuite()
    # 指定待执行用例的目录
    discover = unittest.defaultTestLoader.discover(case_dir['bb_dir'],
                                                   pattern="test_*.py",
                                                   top_level_dir=None)
    testcase.addTests(discover)
    return testcase

def main():
    if autoGitPull():
        # 生成HTML格式
        # html_path = '/home/banban-1/payTest/report/result.html'
        # fp = open(html_path, 'wb')
        # runner = HTMLTestRunner(stream=fp, title=u"测试报告", description=u"用例测试情况")
        # test_result = runner.run(all_case())
        lock = threading.Lock()
        lock.acquire(blocking=True, timeout=1)  # 加
        test_result = unittest.TextTestRunner(verbosity=3).run(all_case())
        writeUpdateTime(str(int(time.time())))
        des = "用例总数: {}, 失败用例数: {}, 异常用例数: {}" \
            .format(test_result.testsRun, len(test_result.failures), len(test_result.errors))
        Logs.get_log('caseResult.log').info(des)
        case_list=method.dictToList(Consts.CASE_LIST)
        case_list_2=method.dictToList(Consts.CASE_LIST_2)
        use_time=str(int(Consts.endTime-Consts.startTime)) + 's'
        lock.release()  # 解
        if len(test_result.failures) == 0 and len(test_result.errors) == 0:
            des = "{}\n".format(case_list)
            des_2 = "{}\n用例数: {}, 失败数: {}, 执行时间: {}, 执行分支：{}".format(case_list_2, test_result.testsRun,
                                                                       len(test_result.failures) + len(test_result.errors),
                                                                       use_time, Config.config.bb_test['bb_git_branch'])
            robot('markdown', des)
            time.sleep(0.2)
            robot('markdown', des_2)
        elif len(test_result.failures) >= 1:
            Logs.get_log('failCase.log').error("failures: {}".format(test_result.failures))
            time.sleep(0.2)
            print(set(Consts.fail_case_reason))
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