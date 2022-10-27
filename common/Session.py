# coding=utf-8
"""
封装获取cookie方法
"""
import os
import requests
import urllib3
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from common import Logs, method
from common.Config import config
from common.params_Yaml import Yaml


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
        urllib3.disable_warnings()
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
        if env == "release":
            pass
        elif env == "dev":  # 伴伴
            # noinspection PyBroadException
            try:
                headers = Yaml.read_yaml('Basic.yml', 'header_dev')
                params = Yaml.read_yaml('Basic.yml', 'params_dev_qq')
                login_url = config.bb_qqLogin_url + '?' + params + '&package=com.imbb.banban.android'  # 7.22修改，请求接口加包名限制
                body = Yaml.read_yaml('Basic.yml', 'data_dev_qq')
                session = requests.session()
                res = session.post(login_url, data=body, headers=headers, verify=False)
                res.raise_for_status()
                res = res.json()
                if not method.isExtend(res, 'token') or res['success'] != 1:
                    print('failReason： {}'.format(res['msg']))
                tokenDict = {'token': res['data'].get('token'), 'uid': res['data']['uid']}
                Session.checkUserToken('write', app_name=env, token=tokenDict['token'])
                return tokenDict
            except Exception as error:
                Logs.get_log('getSession.log').error('session异常，原因： {}'.format(error))
        elif env == config.appName['冲鸭']:
            # noinspection PyBroadException
            try:
                headers = Yaml.read_yaml('Basic.yml', 'header_dev')
                params = Yaml.read_yaml('Basic.yml', 'params_teammate_qq')
                login_url = config.bb_qqLogin_url + '?' + params + '&package=com.im.duck.android'  # 7.22修改，请求接口加包名限制
                body = Yaml.read_yaml('Basic.yml', 'data_teammate_qq')
                session = requests.session()
                print(1)
                print(headers)
                print(params)
                print(login_url)
                print(body)
                res = session.post(login_url, data=body, headers=headers, verify=False)
                res.raise_for_status()
                res = res.json()
                print(res)
                if not method.isExtend(res, 'token') or res['success'] != 1:
                    print('failReason： {}'.format(res['msg']))
                tokenDict = {'token': res['data'].get('token'), 'uid': res['data']['uid']}
                Session.checkUserToken('write', app_name=env, token=tokenDict['token'])
                print(tokenDict)
                return tokenDict
            except Exception as error:
                Logs.get_log('getSession.log').error('session异常，原因： {}'.format(error))
        elif env == config.appName['Partying']:
            try:
                headers = Yaml.read_yaml('Basic_pt.yml', 'header_pt')
                body = Yaml.read_yaml('Basic_pt.yml', 'data_pt_mobile')
                session = requests.session()
                res = session.post(config.pt_mobile_login_url, data=body, headers=headers, verify=False)
                res.raise_for_status()
                res = res.json()
                if not method.isExtend(res, 'token') or res['success'] != 1:
                    print('failReason： {}'.format(res['msg']))
                tokenDict = {'token': res['data'].get('token'), 'uid': res['data']['uid']}
                Session.checkUserToken('write', app_name=env, token=tokenDict['token'])
                return tokenDict
            except Exception as error:
                Logs.get_log('getSession.log').error('session获取异常，原因： {}'.format(error))
        elif env == config.appName['starify']:
            try:
                from common.Basic_starify import header_starify, query_starify, body_starify
                from caseStarify.tools import create_sign
                from time import time
                from urllib.parse import urlencode, urlunparse, unquote
                # 不去除sign验证,必须自己计算
                headers = header_starify
                query = query_starify.copy()
                query['_timestamp'] = str(int(time()))
                body = body_starify
                sign = create_sign(query)
                query['_sign'] = sign
                url = config.starify_mobile_login_url+"?"+unquote(urlencode(query))
                session = requests.session()
                res = session.post(url, data=body, headers=headers, timeout=30)
                res.raise_for_status()
                res = res.json()
                if not method.isExtend(res, 'token') or res['success'] != 1:
                    print('failReason： {}'.format(res['msg']))
                tokenDict = {'token': res['data'].get('token'), 'uid': res['data']['uid']}
                Session.checkUserToken('write', app_name=env, token=tokenDict['token'])
                return tokenDict
            except Exception as error:
                Logs.get_log('getSession.log').error('session获取异常，原因： {}'.format(error))

        else:
            print("env input error")

    @staticmethod
    def checkUserToken(operate, app_name='dev', token=''):
        txtPath = os.path.split(os.path.realpath(__file__))[0] + '/{}UserToken.txt'.format(app_name)
        if not os.path.exists(txtPath):
            os.system(r"touch {}".format(txtPath))
        if operate == 'write':
            with open(txtPath, 'w') as f:
                f.write(token)
                f.flush()
        elif operate == 'read':
            with open(txtPath, 'r') as f:
                f = f.read()
                return f