import os
import git
from git.repo import Repo
import time

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
    commit_log = repo.git.log('--pretty={"commit":"%h","author":"%an","summary":"%s","date":"%cd"}',
                              max_count=3, date=time.time())
    log_list = commit_log.split("\n")
    real_time = [eval(item) for item in log_list][0]['date']
    #times = int(time.mktime(real_log_list))
    print(real_time)


if __name__=="__main__":
    autoGitPull()