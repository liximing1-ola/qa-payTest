# coding=utf-8
import unittest
import time
from common import Logs, method
from autoGitPull import autoGitPull, writeUpdateTime
from Robot import robot
from common import Consts

def all_case():
    # win下路径
    # case_dir = os.path.join(os.getcwd(), "Case")
    testcase = unittest.TestSuite()
    # 指定待执行用例的目录
    discover = unittest.defaultTestLoader.discover("/home/banban-1/payTest/case",
                                                   pattern="test_*",
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
        Logs.get_log('caseResult.log').info(des)
        case_list=method.dictToList(Consts.CASE_LIST)
        if len(test_result.failures) == 0 and len(test_result.errors) == 0:
            des = "执行用例总数: {}, 失败用例总数: {}, 异常用例总数: {}, 执行结果如下:\n {}" \
                .format(test_result.testsRun, len(test_result.failures), len(test_result.errors), case_list)
            time.sleep(2)
            robot('markdown', des)
        elif len(test_result.failures) >= 1:
            Logs.get_log('failCase.log').error("failures: {}".format(test_result.failures))
            time.sleep(2)
            # 失败用例更新提醒
            robot('success', des)
            for case, reason in test_result.failures:
                robot('fail', set(Consts.fail_case_reason), title=case.id())
                # 反馈一个，否则骚扰
                break
        elif len(test_result.errors) >= 1:
            Logs.get_log('failCase.log').error("error: {}".format(test_result.errors))
            for case, reason in test_result.errors:
                robot('fail', reason, case.id())
                break
    else:
        pass


if __name__ == "__main__":
    # all_case() 123
    main()