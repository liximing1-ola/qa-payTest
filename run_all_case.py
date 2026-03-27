# coding=utf-8
"""
自动化测试运行器

支持多应用（伴伴/PT/不夜星球）的测试用例自动执行、结果汇总和通知。
"""
import platform
from time import time, sleep
import unittest
from typing import Optional, Dict, Any, List, Tuple
from Robot import robot
from autoGitPull import updateTime, updateCode
from common import Logs, method, Consts
from common.Config import config
from common.method import check_path


# 应用配置映射
APP_CONFIG: Dict[str, Dict[str, Any]] = {
    config.appName['1']: {
        'dir': '/case',
        'git_repos': ['bb_php', 'bb_go'],
        'bot': 'BB',
        'mode': 'slack',
        'branch_key': 'bb_git_branch',
        'lang': 'zh'
    },
    config.appName['2']: {
        'dir': '/caseOversea',
        'git_repos': None,  # 使用 appInfo
        'bot': 'PT',
        'mode': 'slack_pt',
        'branch_key': 'pt_git_branch',
        'lang': 'en'
    },
    config.appName['不夜星球']: {
        'dir': '/caseSlp',
        'git_repos': ['slp_php', 'slp_common_rpc'],
        'bot': 'slp',
        'mode': 'slack',
        'branch_key': 'slp_git_branch',
        'lang': 'zh',
        'to': 'slack'
    },
}


def load_cases(app_info: str) -> Optional[unittest.TestSuite]:
    """加载测试用例
    
    Args:
        app_info: 应用信息
        
    Returns:
        测试套件，失败返回 None
    """
    cfg = APP_CONFIG.get(app_info)
    if not cfg:
        return None
    
    case_dir = config.BASE_PATH + cfg['dir']
    discover = unittest.defaultTestLoader.discover(case_dir, pattern="test_*.py", top_level_dir=None)
    testcase = unittest.TestSuite()
    testcase.addTests(discover)
    return testcase


def run_tests(app_info: str) -> unittest.TextTestResult:
    """执行测试
    
    Args:
        app_info: 应用信息
        
    Returns:
        测试结果对象
    """
    return unittest.TextTestRunner(verbosity=3).run(load_cases(app_info))


def log_result(test_result: unittest.TextTestResult, lang: str = 'zh') -> str:
    """记录测试结果
    
    Args:
        test_result: 测试结果对象
        lang: 语言（zh/en）
        
    Returns:
        结果描述字符串
    """
    if lang == 'en':
        des = (f"Total: {test_result.testsRun}, "
               f"failures: {len(test_result.failures)}, "
               f"errors: {len(test_result.errors)}")
    else:
        des = (f"用例总数：{test_result.testsRun}, "
               f"失败用例数：{len(test_result.failures)}, "
               f"异常用例数：{len(test_result.errors)}")
    
    Logs.get_logger('caseResult.log').info(des)
    return des


def get_summary_data(test_result: unittest.TextTestResult, 
                    branch_key: str) -> Tuple[str, str, str, str]:
    """获取汇总数据
    
    Args:
        test_result: 测试结果对象
        branch_key: 分支键名
        
    Returns:
        (case_list, case_list_2, use_time, branch) 元组
    """
    case_list = method.dict_to_markdown(Consts.case_list)
    case_list_2 = method.dict_to_markdown(Consts.case_list_b)
    use_time = str(int(Consts.endTime - Consts.startTime)) + 's'
    branch = config.codeInfo[branch_key]
    return case_list, case_list_2, use_time, branch


def notify_success(app_info: str, test_result: unittest.TextTestResult) -> None:
    """通知成功结果
    
    Args:
        app_info: 应用信息
        test_result: 测试结果对象
    """
    cfg = APP_CONFIG[app_info]
    case_list, case_list_2, use_time, branch = get_summary_data(test_result, cfg['branch_key'])
    
    if cfg['lang'] == 'en':
        des_2 = (f"{case_list_2}\n"
                 f"Total: {test_result.testsRun}, Failures: 0, "
                 f"Times: {use_time}, Branch: {branch}")
    else:
        des_2 = (f"{case_list_2}\n"
                 f"用例数：{test_result.testsRun}, 失败数：0, "
                 f"总耗时：{use_time}, 代码分支：{branch}")
    
    to = cfg.get('to', 'wx')
    robot(cfg['mode'], case_list, bot=cfg['bot'], to=to)
    sleep(0.1)
    robot(cfg['mode'], des_2, bot=cfg['bot'], to=to)


def notify_failures(app_info: str, test_result: unittest.TextTestResult, 
                   des: str) -> None:
    """通知失败结果
    
    Args:
        app_info: 应用信息
        test_result: 测试结果对象
        des: 结果描述
    """
    cfg = APP_CONFIG[app_info]
    failures = test_result.failures
    errors = test_result.errors
    to = cfg.get('to', 'wx')
    
    if failures:
        Logs.get_logger('failCase.log').error(f"failures: {failures}")
        robot(cfg['mode'], des, bot=cfg['bot'], color='danger', to=to)
        for case, _ in failures:
            robot(cfg['mode'], Consts.fail_case_reason[0], 
                 title=case.id(), color='danger', bot=cfg['bot'], to=to)
            break
    elif errors:
        Logs.get_logger('failCase.log').error(f"error: {errors}")
        for case, reason in errors:
            robot(cfg['mode'], reason, case.id(), 
                 color='danger', bot=cfg['bot'], to=to)
            break


def handle_result(app_info: str, test_result: unittest.TextTestResult) -> None:
    """处理测试结果
    
    Args:
        app_info: 应用信息
        test_result: 测试结果对象
    """
    cfg = APP_CONFIG[app_info]
    des = log_result(test_result, cfg['lang'])
    
    if len(test_result.failures) == 0 and len(test_result.errors) == 0:
        notify_success(app_info, test_result)
    else:
        notify_failures(app_info, test_result, des)


def pull_code(app_info: str) -> bool:
    """拉取代码
    
    Args:
        app_info: 应用信息
        
    Returns:
        是否成功拉取
    """
    cfg = APP_CONFIG[app_info]
    repos = cfg.get('git_repos')
    
    if repos:
        results = [updateCode.autoGitPull(repo, bot=cfg.get('bot'), 
                     to=cfg.get('to')) for repo in repos]
        return any(results)
    else:
        return updateCode.autoGitPull(app_info)


def main(app_info: str) -> None:
    """主入口
    
    Args:
        app_info: 应用信息
    """
    if app_info not in APP_CONFIG:
        Logs.get_logger('runCode.log').error(f'{app_info} 执行异常')
        return
    
    if app_info == config.appName['2']:
        check_path(config.codeInfo['pt_php_path'])
    
    if pull_code(app_info):
        updateTime('write', now=str(int(time())))
        test_result = run_tests(app_info)
        Consts.endTime = time()
        handle_result(app_info, test_result)
    else:
        Logs.get_logger('runCode.log').info('NoRun')


if __name__ == "__main__":
    node = platform.node()
    if node == config.linux_node['ali']:
        main(config.appName['2'])
    elif node == config.linux_node['ali-slp']:
        main(config.appName['不夜星球'])
    else:
        main(config.appName['1'])