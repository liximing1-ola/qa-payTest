import os
import sys

sys.path.append(os.path.split(os.path.abspath(os.path.dirname(__file__)))[0])
import unittest

from Robot import robot
from common import Logs, method, Consts
from common.Config import config


def all_case():
    case_dir = config.BASE_PATH
    case_dir += '/concurrentPay'
    case_name = 'test_*.py'

    testcase = unittest.TestSuite()
    discover = unittest.defaultTestLoader.discover(case_dir,  # 指定待执行用例的目录
                                                   pattern=case_name,
                                                   top_level_dir=None)
    testcase.addTests(discover)
    return testcase


def main():
    unittest.TextTestRunner(verbosity=3).run(all_case())
    case_list = method.dictToList(Consts.case_list_c)
    des = "{}\n".format(case_list)
    Logs.get_log('concurrentCaseResult.log').info(des)
    robot('success', reason=des)


if __name__ == '__main__':
    main()
