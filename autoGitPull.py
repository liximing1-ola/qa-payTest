import git
from git.repo import Repo
import time
from common import Logs, Consts, Session
from common.Config import config
import os
from Robot import robot
def autoGitPull():
    Consts.startTime = time.time()
    # 默认指定路径
    codeDir = {'git_dir': '/home/webroot/banban', 'pt_git_dir': '/home/webroot/oversea/oversea-server'}
    git_dir = codeDir['git_dir']
    g = git.cmd.Git(git_dir)
    # writeGitStatus(g.status())
    g.pull()
    repo = Repo(git_dir)
    writeGitStatus(repo.git.status())
    # 更新userToken
    Session.Session().get_session('dev')
    # 当前线上分支
    if str(repo.active_branch) == config.banban_git_branch:
        commit_log = repo.git.log('--pretty={"commit":"%h","author":"%an","summary":"%s","date":"%cd"}',
                                  max_count=3, date='format:%Y-%m-%d %H:%M:%S')
        log_list = commit_log.split("\n")
        Logs.get_log('gitCommitPull.log').info('当前分支: {}, 最新一条commit: {}'.format(repo.active_branch, log_list[0]))
        real_time = [eval(item) for item in log_list][0]['date']
        timeArray = time.strptime(real_time, "%Y-%m-%d %H:%M:%S")
        # commit更新时间
        times = int(time.mktime(timeArray))
        # 上次脚本执行时间
        lastTime = int(readUpdateTime())
        if times > lastTime:
            Logs.get_log('updateGitCode.log').info('最新代码提交时间: {}, 上次代码更新时间: {}'.format(times, lastTime))
            # git commit update message
            robot('success', '{}'.format(log_list[0]))
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
            f.write('1600000000')  # 创建txt文件，并默认写入一个时间戳
            f.flush()
    with open(txtPath, 'r') as f:
        f = f.read()
        return f

def writeGitStatus(file):
    txtPath = os.path.split(os.path.realpath(__file__))[0] + '/gitStatus.txt'
    with open(txtPath, 'w') as f:
        f.write(file)
        f.flush()

def readGitStatus():
    txtPath = os.path.split(os.path.realpath(__file__))[0] + '/gitStatus.txt'
    now = time.strftime('%Y-%m-%d %H:%M', time.localtime(time.time()))
    with open(txtPath, 'r') as f:
        for line in f.readlines():
            if line.startswith("Your branch is up to date with 'origin/{}'.".format(config.banban_git_branch)):
                Logs.get_log('gitStatus.log').info(now)
                return True
        else:
            robot('icon', '代码冲突，脚本启动失败，请@lixm严查')


if __name__=='__main__':
    pass