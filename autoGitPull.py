import os
import git

def autoGitPull2():
    os.popen('cd /home/webroot/banban')
    result = os.popen('pwd')
    result = result.read()
    print(result)

def autoGitPull():
    git_dir = '/home/webroot/banban'
    g = git.cmd.Git(git_dir)
    g.pull()


if __name__=="__main__":
    autoGitPull()