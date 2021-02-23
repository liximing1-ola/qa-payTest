import os
import git
from git.repo import Repo

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
                              max_count=3, date='format:%Y-%m-%d %H:%M')
    log_list = commit_log.split("\n")
    real_log_list = [eval(item) for item in log_list][0]['date']
    print(real_log_list)


if __name__=="__main__":
    autoGitPull()