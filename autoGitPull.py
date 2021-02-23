import os
import git
from git.repo import Repo
import time
from Common import logs

def autoGitPull2():
    os.popen('cd /home/webroot/banban')
    result = os.popen('pwd')
    result = result.read()
    print(result)

def autoGitPull():
    git_dir = '/home/webroot/banban'
    g = git.cmd.Git(git_dir)
    g.pull()
    repo = Repo(git_dir)
    if repo.active_branch == 'release-for-proxy':
        commit_log = repo.git.log('--pretty={"commit":"%h","author":"%an","summary":"%s","date":"%cd"}',
                                  max_count=3, date='format:%Y-%m-%d %H:%M:%S')
        log_list = commit_log.split("\n")
        real_time = [eval(item) for item in log_list][0]['date']
        timeArray = time.strptime(real_time, "%Y-%m-%d %H:%M:%S")
        times = int(time.mktime(timeArray))
        now = int(time.time())
        print(times)
        print(now)
        if times + 120 >= now:
            logs.get_log('gitCode.log').info('最新代码提交时间: {}, 当前拉取试行时间: {}'.format(times, now))
            return True
        else:
            return False
    else:
        print('fail')
        return False




if __name__=="__main__":
    autoGitPull()