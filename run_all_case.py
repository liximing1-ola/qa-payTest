# coding=utf-8
import unittest
import time
from Common import logs, api
from autoGitPull import writeUpdateTime
from autoGitPull import autoGitPull
from robot import robot_fail, robot_success
from Common.HTMLTestRunner import HTMLTestRunner
import os
from Common import consts

def all_case():
    # case_dir = os.path.join(os.getcwd(), "Case")   # 待执行用例的目录
    testcase = unittest.TestSuite()
    discover = unittest.defaultTestLoader.discover("/home/banban-1/payTest/Case",
                                                   pattern="test_*.py",
                                                   top_level_dir=None)
    testcase.addTests(discover)  # 直接加载 discover
    return testcase


def main():
    if autoGitPull():
        # 生成HTML格式
        # html_path = '/home/banban-1/payTest/report/result.html'
        # fp = open(html_path, 'wb')
        # runner = HTMLTestRunner(stream=fp, title=u"测试报告", description=u"用例测试情况")
        # test_result = runner.run(all_case())
        test_result = unittest.TextTestRunner(verbosity=3).run(all_case())
        writeUpdateTime(str(int(time.time())))
        des = "执行用例总数: {}, 失败用例总数: {}, 异常用例总数: {}" \
            .format(test_result.testsRun, len(test_result.failures), len(test_result.errors))
        logs.get_log('runCaseTime.log').info(des)
        case_list=api.dictToList(consts.CASE_LIST)
        if len(test_result.failures) == 0 and len(test_result.errors) == 0:
            des = "执行用例总数: {}, 失败用例总数: {}, 异常用例总数: {}, 执行结果如下:\n {}" \
                .format(test_result.testsRun, len(test_result.failures), len(test_result.errors), case_list)
            time.sleep(2)
            robot_success(des)
        elif len(test_result.failures) >= 1:
            logs.get_log('failCase.log').error("failures: {}".format(test_result.failures))
            time.sleep(3)
            # 失败用例更新提醒
            robot_success(des)
            for case, reason in test_result.failures:
                robot_fail(case.id(), consts.fail_case_reason)
                break
        elif len(test_result.errors) >= 1:
            logs.get_log('failCase.log').error("error: {}".format(test_result.errors))
            for case, reason in test_result.errors:
                robot_fail(case.id(), reason)
                break
    else:
        pass

def html_runner():
    # 生成HTML格式
    html_path = '/home/banban-1/payTest/report/result.html'
    fp = open(html_path, 'wb')
    runner = HTMLTestRunner(stream=fp, title=u"测试报告", description=u"用例测试情况")
    all_case_name = all_case()
    m = runner.run(all_case_name)
    fp.close()
    return m


if __name__ == "__main__":
    # all_case()
    main()