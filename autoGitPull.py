import os
from git.repo import Repo

def autoGitPull():
    local_path = "/home/webroot/banban"
    repo = Repo(local_path)
    repo.git.pull("")

def autoGitPull2():
    os.system('cd /home/webroot/banban')
    os.system('git pull')


if __name__=="__main__":
    autoGitPull2()