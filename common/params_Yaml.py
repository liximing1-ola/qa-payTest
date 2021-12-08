# coding=utf-8
import yaml
from common.Config import config
import os
from common import Logs
import git
from git.repo import Repo
class Yaml:
    @staticmethod
    def read_yaml(yaml_fileName, yaml_name):
        """
        读取yaml
        :return: yaml_data[yaml_name]
        """
        # bath_path = os.path.dirname(os.path.dirname(os.path.abspath(os.path.defpath)))
        # yaml_path = bath_path + '/' + yaml_fileName
        yaml_path = config.BASE_PATH + '/common/' + yaml_fileName
        try:
            if not os.path.exists(yaml_path):
                return FileExistsError
            if checkBranch('master'):
                yaml_data = yaml.load(open(yaml_path, 'r', encoding='utf-8'))
            else:
                yaml_data = yaml.load(open(yaml_path, 'r', encoding='utf-8'), Loader=yaml.FullLoader)  # 添加后不会报warning
            if yaml_data[yaml_name] is None:
                return TypeError
            else:
                return yaml_data[yaml_name]
        except Exception as e:
            print(e)

def checkBranch(git_branch):
    codeDir = '/home/banban-1/payTest'  # 默认指定路径
    g = git.cmd.Git(codeDir)
    g.pull()
    repo = Repo(codeDir)
    if str(repo.active_branch) != git_branch:  # 当前线上分支
        Logs.get_log('gitBranchError.log').error("git branch error： {}".format(repo.active_branch))
        return False
    return True