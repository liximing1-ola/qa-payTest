# coding=utf-8
import unittest
from common import Logs, method, Consts
from Robot import robot
from common.Config import config
import platform


# 应用配置映射
APP_CONFIG = {
    config.appName['1']: {'dir': '/case', 'pattern': 'test_pay_punish.py', 'bot': None, 'branch_key': 'bb_git_branch'},
    config.appName['2']: {'dir': '/caseLuckyPlay', 'pattern': 'test_*.py', 'bot': '1', 'branch_key': 'pt_git_branch'},
}


def load_cases(app_info):
    """加载测试用例"""
    cfg = APP_CONFIG.get(app_info)
    if not cfg:
        return None
    
    case_dir = config.BASE_PATH + cfg['dir']
    discover = unittest.defaultTestLoader.discover(case_dir, pattern=cfg['pattern'], top_level_dir=None)
    testcase = unittest.TestSuite()
    testcase.addTests(discover)
    return testcase


def run_tests(app_info):
    """执行测试并返回结果"""
    cases = load_cases(app_info)
    if not cases:
        return None
    return unittest.TextTestRunner(verbosity=3).run(cases)


def log_result(test_result):
    """记录测试结果"""
    des = f"用例总数: {test_result.testsRun}, 失败用例数: {len(test_result.failures)}, 异常用例数: {len(test_result.errors)}"
    Logs.get_logger('caseResult_2.log').info(des)
    return des


def notify_success(app_info, test_result, case_list):
    """通知成功结果"""
    cfg = APP_CONFIG[app_info]
    des = f"定时任务:\n{case_list}\n用例数: {test_result.testsRun}, 失败数: 0, 代码分支：{config.codeInfo[cfg['branch_key']]}"
    robot('markdown', des, bot=cfg['bot'])


def notify_failures(app_info, failures, log_type='failures'):
    """通知失败结果"""
    Logs.get_logger('failCase.log').error(f"{log_type}: {failures}")
    cfg = APP_CONFIG[app_info]
    for case, _ in failures:
        robot('icon', case.id().split('.')[2], bot=cfg['bot'])


def handle_result(app_info, test_result):
    """处理测试结果"""
    log_result(test_result)
    case_list = method.dict_to_markdown(Consts.case_list_c)
    
    failures_count = len(test_result.failures)
    errors_count = len(test_result.errors)
    
    if failures_count == 0 and errors_count == 0:
        notify_success(app_info, test_result, case_list)
    elif failures_count >= 1:
        notify_failures(app_info, test_result.failures, 'failures')
    elif errors_count >= 1:
        notify_failures(app_info, test_result.errors, 'errors')


def main(app_info):
    """主入口"""
    if app_info not in APP_CONFIG:
        Logs.get_logger('runCode.log').error(f'{app_info} 执行异常')
        return
    
    test_result = run_tests(app_info)
    if test_result:
        handle_result(app_info, test_result)


if __name__ == "__main__":
    target_app = config.appName['2'] if platform.node() == config.linux_node['ali'] else config.appName['1']
    main(target_app)
