# coding=utf-8
import unittest
import time
from Common import logs
from autoGitPull import writeUpdateTime
from autoGitPull import autoGitPull
from robot import roBot, roBOt
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
        test_result = unittest.TextTestRunner(verbosity=2).run(all_case())
        writeUpdateTime(str(int(time.time())))
        now = time.strftime('%F-%H:%M', time.localtime(time.time()))
        logs.get_log('runCaseTime.log').info("执行用例总数: {}, 失败用例总数: {}, 执行时间: {}"
                                             .format(test_result.testsRun, len(test_result.failures), now))
        if len(test_result.failures) == 0:
            time.sleep(5)
            des = "执行用例总数: {}, 失败用例总数: {}, 执行时间: {}".format(test_result.testsRun, len(test_result.failures), now)
            roBOt(des)
        if len(test_result.failures) >= 1:
            logs.get_log('failCase.log').error(test_result.failures)
        for case, reason in test_result.failures:
            if len(test_result.failures) > 0:
                roBot(case.id())
                break
    else:
        pass


if __name__ == "__main__":
    main()