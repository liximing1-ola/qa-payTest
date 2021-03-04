import git
from git.repo import Repo
import time
from Common import logs
import os
from robot import robot

def autoGitPull():
    # 默认指定路径
    git_dir = '/home/webroot/banban'
    g = git.cmd.Git(git_dir)
    g.pull()
    repo = Repo(git_dir)
    # 当前线上分支
    if str(repo.active_branch) == "release-for-vpc":
        commit_log = repo.git.log('--pretty={"commit":"%h","author":"%an","summary":"%s","date":"%cd"}',
                                  max_count=3, date='format:%Y-%m-%d %H:%M:%S')
        log_list = commit_log.split("\n")
        logs.get_log('gitPull.log').info('当前分支: {}, 最新一条commit: {}'.format(repo.active_branch, log_list[0]))
        real_time = [eval(item) for item in log_list][0]['date']
        timeArray = time.strptime(real_time, "%Y-%m-%d %H:%M:%S")
        # commit更新时间
        times = int(time.mktime(timeArray))
        # 上次脚本执行时间
        lastTime = int(readUpdateTime())
        if times > lastTime:
            logs.get_log('updateGitCode.log').info('最新代码提交时间: {}, 上次代码更新时间: {}'.format(times, lastTime))
            # git commit update message
            robot('success', '{}'.format(log_list[0]))
            return True
        else:
            logs.get_log('codeNotPull.log').error("Git_Pull未拉取到release分支最新代码")
            return False
    else:
        logs.get_log('gitError.log').error("Git分支不对： {}".format(repo.active_branch))
        return False

def writeUpdateTime(now):
    txtPath = os.path.split(os.path.realpath(__file__))[0] + '/time.txt'
    with open(txtPath, 'w') as f:
        f.write(now)

def readUpdateTime():
    txtPath = os.path.split(os.path.realpath(__file__))[0] + '/time.txt'
    with open(txtPath, 'r') as f:
        f = f.read()
        return f


if __name__=="__main__":
    readUpdateTime()