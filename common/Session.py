# coding=utf-8
"""
封装获取cookie方法
"""
import os
import requests
import urllib3
from common import Logs
from common.Config import config
from common.paramsYaml import Yaml

urllib3.disable_warnings()
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class Session:
    """会话管理类"""

    # 环境配置映射
    ENV_CONFIGS = {
        "dev": {
            "headers_key": 'header_dev',
            "params_key": 'params_dev_qq',
            "body_key": 'data_dev_qq',
            "package": 'x.x.x.x',
            "login_url": config.bb_qqLogin_url,
            "use_backup": True,
        },
        "rush": {
            "headers_key": 'header_dev',
            "params_key": 'params_teammate_qq',
            "body_key": 'data_teammate_qq',
            "package": 'com.im.duck.android',
            "login_url": config.bb_qqLogin_url,
            "use_backup": False,
        },
        config.appName['1']: {
            "headers_key": 'header_pt',
            "params_key": 'data_pt_mobile_params',
            "body_key": 'data_slp_mobile',
            "package": None,
            "login_url": config.pt_mobile_login_url,
            "use_backup": False,
        },
        config.appName['不夜星球']: {
            "headers_key": 'header_slp',
            "params_key": 'data_slp_mobile_params',
            "body_key": 'data_slp_mobile',
            "package": 'com.yhl.sleepless.android',
            "login_url": config.slp_mobile_login_url,
            "use_backup": True,
        },
    }

    @staticmethod
    def _login(env_config, env):
        """执行登录请求"""
        headers = Yaml.read('Basic.yml', env_config['headers_key'])
        params = Yaml.read('Basic.yml', env_config['params_key'])
        body = Yaml.read('Basic.yml', env_config['body_key'])

        login_url = env_config['login_url'] + '?' + params
        if env_config['package']:
            login_url += f"&package={env_config['package']}"

        session = requests.session()
        res = session.post(login_url, data=body, headers=headers, verify=False)
        res.raise_for_status()
        return res.json()

    @staticmethod
    def _handle_response(res, env):
        """处理响应结果"""
        if not res.get('success') or 'token' not in res.get('data', {}):
            print(f'failReason： {res.get("msg", "")}')
            return None

        token = res['data'].get('token')
        uid = res['data'].get('uid')
        print(f'{env}：token:{token}')

        Session.checkUserToken('write', app_name=env, token=token)
        return {'token': token, 'uid': uid}

    @staticmethod
    def _use_backup_plan(env, error_msg):
        """使用备选方案获取token"""
        Logs.get_logger('getSession.log').error(f'{error_msg}，原因： {error_msg}')
        from common.conMysql import conMysql
        from common.getToken import TokenGenerator

        token = TokenGenerator(config.payUid, conMysql.selectUserInfoSql('user_index', config.payUid)).generate()
        Session.checkUserToken('write', app_name=env, token=token)
        print(f'默认方案失败，启用备选方案：token:{token}')
        return {'token': token}

    @staticmethod
    def getSession(env):
        """
        获取登录session
        :param env: 环境
        :return: 登录token
        """
        if env == "release":
            return None

        env_config = Session.ENV_CONFIGS.get(env)
        if not env_config:
            print("env input error")
            return None

        try:
            res = Session._login(env_config, env)
            result = Session._handle_response(res, env)
            if result:
                return result
        except Exception as error:
            if env_config.get('use_backup'):
                return Session._use_backup_plan(env, str(error))
            Logs.get_logger('getSession.log').error(f'session获取异常，原因： {error}')

        return None

    @staticmethod
    def checkUserToken(operate, app_name='dev', token='', uid=None):
        """检查/写入用户token"""
        base_path = os.path.split(os.path.realpath(__file__))[0]
        filename = f'{app_name}UserToken_{uid}.txt' if uid else f'{app_name}UserToken.txt'
        txt_path = os.path.join(base_path, filename)

        if not os.path.exists(txt_path):
            open(txt_path, 'w').close()

        if operate == 'write':
            with open(txt_path, 'w') as f:
                f.write(token)
                f.flush()
        elif operate == 'read':
            with open(txt_path, 'r') as f:
                content = f.read()
                if content:
                    return content
                raise Exception(f"{txt_path}-为空!")
