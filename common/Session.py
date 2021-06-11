# coding=utf-8
"""
封装获取cookie方法
"""
import requests
from common.Config import config
from common.params_Yaml import Yaml
from common import Logs
from common import method
class Session:
    def __init__(self):
        self.config = config

    @staticmethod
    def get_session(env):
        """
        获取qq登陆session
        :param env: 环境
        :return: 登陆token
        """
        if env == "release":
            pass
        elif env == "dev":
            # noinspection PyBroadException
            try:
                headers = Yaml.read_yaml('Basic.yml', 'header_dev')
                params = Yaml.read_yaml('Basic.yml', 'params_dev_qq')
                login_url = config.qq_login_url + '?' + params
                body = Yaml.read_yaml('Basic.yml', 'data_dev_qq')
                session = requests.session()
                res = session.post(login_url, data=body, headers=headers)
                res.raise_for_status()
                res = res.json()
                if not method.isExtend(res, 'token') or res['success'] != 1:
                    return res['msg']
                tokenDict = {'token': res['data'].get('token'), 'uid': res['data']['uid']}
                return tokenDict
            except Exception as error:
                Logs.get_log('getSession.log').error('session异常，原因： {}'.format(error))
        elif env == 'pt':
            try:
                headers = Yaml.read_yaml('Basic_pt.yml', 'header_pt')
                body = Yaml.read_yaml('Basic_pt.yml', 'data_pt_mobile')
                session = requests.session()
                res = session.post(config.mobile_login_url, data=body, headers=headers)
                res.raise_for_status()
                res = res.json()
                if not method.isExtend(res, 'token') or res['success'] != 1:
                    return res['msg']
                tokenDict = {'token': res['data'].get('token'), 'uid': res['data']['uid']}
                return tokenDict
            except Exception as error:
                Logs.get_log('getSession.log').error('session获取异常，原因： {}'.format(error))
        else:
            print("env input error")


if __name__ == '__main__':
    ss = Session()
    ss.get_session('dev')