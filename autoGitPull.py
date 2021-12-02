import git
import os
import time
from git.repo import Repo
from Robot import robot
from common.Session import Session
from common import Logs, Consts
from common.Config import config
def autoGitPull():
    Consts.startTime = time.time()
    gtr = '/home/webroot/banban'  # 默认指定路径
    g = git.cmd.Git(gtr)
    g.pull()
    repo = Repo(gtr)
    Session().getSession('dev')  # 更新userToken
    if str(repo.active_branch) == config.banban_git_branch:  # 当前线上分支
        commit_log = repo.git.log('--pretty={"commit":"%h","author":"%an","summary":"%s","date":"%cd"}',
                                  max_count=3, date='format:%Y-%m-%d %H:%M:%S')
        log_list = commit_log.split("\n")
        Logs.get_log('gitCommitPull.log').info('当前分支: {}, 最新一条commit: {}'
                                               .format(repo.active_branch, log_list[0]))
        real_time = [eval(item) for item in log_list][0]['date']
        timeArray = time.strptime(real_time, "%Y-%m-%d %H:%M:%S")
        times = int(time.mktime(timeArray))  # commit更新时间
        lastTime = int(updateTime('read'))  # 上次脚本执行时间
        if times > lastTime:
            Logs.get_log('updateGitCode.log').info('最新代码提交时间: {}, 上次代码更新时间: {}'.format(times, lastTime))
            robot('success', '{}'.format(log_list[0]))  # git commit update message
            return True
        else:
            Logs.get_log('updateGitCode.log').info("未拉取到{}分支代码，最近代码提交时间: {}, "
                                                   "上次代码更新时间: {}".format(repo.active_branch, times, lastTime))
            return False
    else:
        Logs.get_log('gitBranchError.log').error("git branch error： {}".format(repo.active_branch))
        return False

def updateTime(operate, now=''):
    txtPath = os.path.split(os.path.realpath(__file__))[0] + '/time.txt'
    if operate == 'write':
        with open(txtPath, 'w') as f:
            f.write(now)
            f.flush()
    elif operate == 'read':
        if not os.path.exists(txtPath):
            os.system(r"touch {}".format(txtPath))
            with open(txtPath, 'r+') as f:
                f.write('1600000000')  # 创建txt文件，并默认写入一个时间戳
                f.flush()
        with open(txtPath, 'r') as f:
            f = f.read()
            return f