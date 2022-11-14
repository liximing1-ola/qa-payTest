# coding=utf-8
import platform
from time import time, sleep
import unittest
from Robot import robot
from autoGitPull import updateTime, updateCode
from common import Logs, method, Consts
from common.Config import config
from common.method import checkPath
def main(appInfo):
    if appInfo == config.appName['伴伴']:
        if updateCode.autoGitPull('bb_php') | updateCode.autoGitPull('bb_go'):
            updateTime('write', now=str(int(time())))
            test_result = unittest.TextTestRunner(verbosity=3).run(all_case(appInfo))
            Consts.endTime = time()
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
                    config.codeInfo['bb_git_branch'])
                robot('slack', des)
                sleep(0.1)
                robot('slack', des_2)
            elif len(test_result.failures) >= 1:
                Logs.get_log('failCase.log').error("failures: {}".format(test_result.failures))
                robot('slack', des, color='danger')
                for case, reason in test_result.failures:
                    robot('slack', Consts.fail_case_reason[0], title=case.id(), color='danger')
                    break
            elif len(test_result.errors) >= 1:
                Logs.get_log('failCase.log').error("error: {}".format(test_result.errors))
                for case, reason in test_result.errors:
                    robot('slack', reason, case.id(), color='danger')
                    break
        else:
            Logs.get_log('runCode.log').info('NoRun')
    elif appInfo == config.appName['Partying']:
        checkPath(config.codeInfo['pt_php_path'])
        if updateCode.autoGitPull(appInfo):
            updateTime('write', now=str(int(time())))
            test_result = unittest.TextTestRunner(verbosity=3).run(all_case(appInfo))
            Consts.endTime = time()
            des = "Total: {}, failures: {}, errors: {}" \
                .format(test_result.testsRun, len(test_result.failures), len(test_result.errors))
            Logs.get_log('caseResult.log').info(des)
            case_list = method.dictToList(Consts.case_list)
            case_list_2 = method.dictToList(Consts.case_list_b)
            use_time = str(int(Consts.endTime - Consts.startTime)) + 's'
            if len(test_result.failures) == 0 and len(test_result.errors) == 0:
                des = "{}\n".format(case_list)
                des_2 = "{}\nTotal: {}, Failures: {}, Times: {}, Branch：{}".format(
                    case_list_2, test_result.testsRun,
                    len(test_result.failures) + len(test_result.errors),
                    use_time,
                    config.codeInfo['pt_git_branch'])
                robot('slack_pt', des, bot='PT')
                sleep(0.1)
                robot('slack_pt', des_2, bot='PT')
            elif len(test_result.failures) >= 1:
                Logs.get_log('failCase.log').error("failures: {}".format(test_result.failures))
                robot('slack_pt', des, bot='PT')
                for case, reason in test_result.failures:
                    robot('slack_pt', Consts.fail_case_reason[0], title=case.id(), bot='PT')
                    break
            elif len(test_result.errors) >= 1:
                Logs.get_log('failCase.log').error("error: {}".format(test_result.errors))
                for case, reason in test_result.errors:
                    robot('slack_pt', reason, case.id(), bot='PT')
                    break
        else:
            Logs.get_log('runCode.log').info('NoRun')
    elif appInfo == config.appName['starify']:
        if updateCode.autoGitPull('starify_go') | updateCode.autoGitPull('starify_room'):
            updateTime('write', now=str(int(time())))
            test_result = unittest.TextTestRunner(verbosity=3).run(all_case(appInfo))
            Consts.endTime = time()
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
                    config.codeInfo['starify_git_branch'])
                robot('slack', des, bot='starify')
                sleep(0.1)
                robot('slack', des_2, bot='starify')
            elif len(test_result.failures) >= 1:
                Logs.get_log('failCase.log').error("failures: {}".format(test_result.failures))
                robot('slack', des, bot='starify', color="danger")
                for case, reason in test_result.failures:
                    robot('slack', Consts.fail_case_reason[0], title=case.id(), bot='starify', color="danger")
                    break
            elif len(test_result.errors) >= 1:
                Logs.get_log('failCase.log').error("error: {}".format(test_result.errors))
                for case, reason in test_result.errors:
                    robot('slack', reason, case.id(), bot='starify', color="danger")
                    break
        else:
            Logs.get_log('runCode.log').info('NoRun')
    else:
        Logs.get_log('runCode.log').error('{} 执行异常'.format(appInfo))

def all_case(appInfo):
    case_dir = config.BASE_PATH
    if appInfo == config.appName['伴伴']:
        case_dir += '/case'
    elif appInfo == config.appName['Partying']:
        case_dir += '/caseOversea'
    elif appInfo == config.appName['starify']:
        case_dir += '/caseStarify'
    else:
        return

    testcase = unittest.TestSuite()
    discover = unittest.defaultTestLoader.discover(case_dir,  # 指定待执行用例的目录
                                                   pattern="test_pay_bean.py",
                                                   top_level_dir=None)
    testcase.addTests(discover)
    return testcase


if __name__ == "__main__":
    if platform.node() == config.linux_node['ali']:
        main(config.appName['Partying'])
    elif platform.node() == config.linux_node['ali-starify']:
        main(config.appName['starify'])
    else:
        main(config.appName['伴伴'])
