import git
from git.repo import Repo
from common import Logs
from common.Config import config
import os
from Robot import robot
import time
def autoGitPull():
    # 默认指定路径
    codeDir = {'pt_git_dir': '/home/webroot/release_oversea/oversea-server'}
    git_dir = codeDir['pt_git_dir']
    g = git.cmd.Git(git_dir)
    g.pull()
    repo = Repo(git_dir)
    if str(repo.active_branch) == config.pt_git_branch:
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
            Logs.get_log('ptUpdateGitCode.log').info('最新代码提交时间: {}, 上次代码更新时间: {}'.format(times, lastTime))
            robot('success', '{}'.format(log_list[0]), bot='PT')  # git commit update message
            return True
        else:
            Logs.get_log('ptUpdateGitCode.log').info("未拉取到{}分支代码，最近代码提交时间: {}, "
                                                   "上次代码更新时间: {}".format(repo.active_branch, times, lastTime))
            return False
    else:
        Logs.get_log('ptGitBranchError.log').error("go branch error： {}".format(repo.active_branch))
        return False

def updateTime(operate, now=''):
    default_time = '1600000000'  # 默认时间戳
    txtPath = os.path.split(os.path.realpath(__file__))[0] + '/time.txt'
    if operate == 'write':
        with open(txtPath, 'w') as f:
            f.write(now)
            f.flush()
    elif operate == 'read':
        if not os.path.exists(txtPath):
            os.system(r"touch {}".format(txtPath))
            with open(txtPath, 'r+') as f:
                f.write(default_time)
                f.flush()
        with open(txtPath, 'r') as f:
            f = f.read()
            return f
    elif operate == 'change':
        with open(txtPath, 'w') as f:
            f.write(default_time)
            f.flush()


if __name__=='__main__':
    updateTime('change')
