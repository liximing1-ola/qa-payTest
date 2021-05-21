import git
from git.repo import Repo
import time
from common import Logs
from common.Config import config
import os
from Robot import robot
import requests
def autoGitPull():
    # 默认指定路径
    codeDir = {'pt_git_dir': '/home/webroot/oversea/oversea-server'}
    git_dir = codeDir['pt_git_dir']
    g = git.cmd.Git(git_dir)
    g.pull()
    repo = Repo(git_dir)
    if str(repo.active_branch) == config.pt_git_branch:
        commit_log = repo.git.log('--pretty={"commit":"%h","author":"%an","summary":"%s","date":"%cd"}',
                                  max_count=3, date='format:%Y-%m-%d %H:%M:%S')
        log_list = commit_log.split("\n")
        Logs.get_log('gitCommitPull.log').info('PT当前分支: {}, 最新一条commit: {}'.format(repo.active_branch, log_list[0]))
        times = int(time.mktime(time.strptime([eval(item) for item in log_list][0]['date'], "%Y-%m-%d %H:%M:%S")))
        lastTime = int(readUpdateTime())
        now_version = updateVersion('get')
        last_version = updateVersion('read')
        if now_version != last_version:
            Logs.get_log('updateGitCode.log').info('最新代码部署版本: {}, 上次代码部署版本: {}'.format(now_version, last_version))
            # git commit update message
            robot('success', '{}'.format(log_list[0]), bot='PT')
            return True
        else:
            Logs.get_log('updateGitCode.log').info("未拉取到{}分支代码，最近代码提交时间: {}, "
                                                   "上次代码更新时间: {}".format(repo.active_branch, times, lastTime))
            return False
    else:
        Logs.get_log('gitBranchError.log').error("git branch error： {}".format(repo.active_branch))
        return False

def writeUpdateTime(now):
    txtPath = os.path.split(os.path.realpath(__file__))[0] + '/time.txt'
    with open(txtPath, 'w') as f:
        f.write(now)
        f.flush()

def readUpdateTime():
    txtPath = os.path.split(os.path.realpath(__file__))[0] + '/time.txt'
    if not os.path.exists(txtPath):
        os.system(r"touch {}".format(txtPath))
        with open(txtPath, 'r+') as f:
            f.write('1600000000')
            f.flush()
    with open(txtPath, 'r') as f:
        f = f.read()
        return f

def updateVersion(p):
    api_url = 'http://api.partying.sg/_version.txt'
    res = requests.get(api_url)
    if p == 'write':
        txtPath = os.path.split(os.path.realpath(__file__))[0] + '/version.txt'
        with open(txtPath, 'w') as f:
            f.write(res.text)
            f.flush()
    elif p == 'read':
        txtPath = os.path.split(os.path.realpath(__file__))[0] + '/version.txt'
        if not os.path.exists(txtPath):
            os.system(r"touch {}".format(txtPath))
            with open(txtPath, 'r+') as f:
                f.write('3ca492e')  # 初始值
                f.flush()
        with open(txtPath, 'r') as f:
            f = f.read()
            return f.strip()
    elif p == 'get':
        return res.text.strip()


if __name__=="__main__":
    print(updateVersion('get'))
