# coding=utf-8
import unittest
import time
from Common import logs
from autoGitPull import writeUpdateTime
from autoGitPull import autoGitPull
from robot import roBot, robot_success
from Common.HTMLTestRunner import HTMLTestRunner

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
        if len(test_result.failures) == 0 and len(test_result.errors) == 0:
            time.sleep(3)
            robot_success(des)
        if len(test_result.failures) >= 1 or len(test_result.errors) >= 1:
            logs.get_log('failCase.log').error("error: {}, failures: {}".format(test_result.errors, test_result.failures))
            time.sleep(3)
            robot_success(des)
        for case, reason in test_result.failures:
            if len(test_result.failures) > 0:
                roBot(case.id())
                break
        for case, reason in test_result.errors:
            if len(test_result.errors) > 0:
                roBot(case.id())
                break
    else:
        pass


if __name__ == "__main__":
    main()