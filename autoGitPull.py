import git
from git.repo import Repo
import time
from Common import logs

def autoGitPull():
    git_dir = '/home/webroot/banban'
    g = git.cmd.Git(git_dir)
    g.pull()
    repo = Repo(git_dir)
    if str(repo.active_branch) == "release-for-proxy":
        commit_log = repo.git.log('--pretty={"commit":"%h","author":"%an","summary":"%s","date":"%cd"}',
                                  max_count=3, date='format:%Y-%m-%d %H:%M:%S')
        log_list = commit_log.split("\n")
        real_time = [eval(item) for item in log_list][0]['date']
        timeArray = time.strptime(real_time, "%Y-%m-%d %H:%M:%S")
        times = int(time.mktime(timeArray))
        lastTime = int(readUpdateTime())
        if times > lastTime:
            logs.get_log('gitCode.log').info('最新代码提交时间: {}, 上次代码更新时间: {}'.format(times, lastTime))
            return True
        else:
            return False
    else:
        print('fail')
        return False

def writeUpdateTime(now):
    txtPath = 'time.txt'
    with open(txtPath, 'w') as f:
        f.write(now)

def readUpdateTime():
    txtPath = 'time.txt'
    with open(txtPath, 'r') as f:
        f = f.read()
        return f


if __name__=="__main__":
    readUpdateTime()