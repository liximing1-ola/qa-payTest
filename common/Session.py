# coding=utf-8
"""
封装获取cookie方法
"""
import requests
from common.Config import config
from common.params_Yaml import Yaml
from common import Logs, method
import os
class Session:
    def __init__(self):
        self.config = config

    @staticmethod
    def getSession(env):
        """
        获取qq登陆session
        :param env: 环境
        :return: 登陆token
        """
        if env == "release":
            pass
        elif env == "dev":  # 伴伴
            # noinspection PyBroadException
            try:
                headers = Yaml.read_yaml('Basic.yml', 'header_dev')
                params = Yaml.read_yaml('Basic.yml', 'params_dev_qq')
                login_url = config.qq_login_url + '?' + params + '&package=com.imbb.banban.android'  # 7.22修改，请求接口加包名限制
                body = Yaml.read_yaml('Basic.yml', 'data_dev_qq')
                session = requests.session()
                res = session.post(login_url, data=body, headers=headers)
                res.raise_for_status()
                res = res.json()
                if not method.isExtend(res, 'token') or res['success'] != 1:
                    print('failReason： {}'.format(res['msg']))
                tokenDict = {'token': res['data'].get('token'), 'uid': res['data']['uid']}
                print(tokenDict['token'])
                Session.checkUserToken('write', app_name=env, token=tokenDict['token'])
                return tokenDict
            except Exception as error:
                Logs.get_log('getSession.log').error('session异常，原因： {}'.format(error))
        elif env == 'havefun':  # 嗨歌
            try:
                headers = Yaml.read_yaml('Basic.yml', 'header_dev')
                params = Yaml.read_yaml('', '')
                login_url = config.qq_login_url + '?' + params + '&package=com.havefun.android'  # 7.22修改，请求接口加包名限制
                body = Yaml.read_yaml('', '')
                session = requests.session()
                res = session.post(login_url, data=body, headers=headers)
                res.raise_for_status()
                res = res.json()
                if not method.isExtend(res, 'token') or res['success'] != 1:
                    print('failReason： {}'.format(res['msg']))
                tokenDict = {'token': res['data'].get('token'), 'uid': res['data']['uid']}
                Session.checkUserToken('write', app_name=env, token=tokenDict['token'])
                return tokenDict
            except Exception as error:
                Logs.get_log('getSession.log').error('session异常，原因： {}'.format(error))
        elif env == 'games':  # 凶手
            try:
                headers = Yaml.read_yaml('Basic.yml', 'header_dev')
                params = Yaml.read_yaml('Basic.yml', 'params_games_qq')
                login_url = config.qq_login_url + '?' + params + '&package=com.who.android'
                body = Yaml.read_yaml('Basic.yml', 'data_games_qq')
                session = requests.session()
                res = session.post(login_url, data=body, headers=headers)
                res.raise_for_status()
                res = res.json()
                if not method.isExtend(res, 'token') or res['success'] != 1:
                    print('failReason： {}'.format(res['msg']))
                tokenDict = {'token': res['data'].get('token'), 'uid': res['data']['uid']}
                Session.checkUserToken('write', app_name=env, token=tokenDict['token'])
                return tokenDict
            except Exception as error:
                Logs.get_log('getSession.log').error('session异常，原因： {}'.format(error))
        elif env == 'pt':  # Parting
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
                Session.checkUserToken('write', app_name=env, token=tokenDict['token'])
                return tokenDict
            except Exception as error:
                Logs.get_log('ptGetSession.log').error('session获取异常，原因： {}'.format(error))
        else:
            print("env input error")

    @staticmethod
    def checkUserToken(operate, app_name='dev', token=''):
        txtPath = os.path.split(os.path.realpath(__file__))[0] + '/{}UserToken.txt'.format(app_name)
        print(txtPath)
        if not os.path.exists(txtPath):
            os.system(r"touch {}".format(txtPath))
        if operate == 'write':
            with open(txtPath, 'w') as f:
                f.write(token)
                f.flush()
        elif operate == 'read':
            with open(txtPath, 'r') as f:
                f = f.read()
                print(f)
                return f