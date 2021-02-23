import os

def autoGitPull2():
    os.popen('cd /home/webroot/banban')
    result = os.popen('pwd')
    result = result.read()
    print(result)


if __name__=="__main__":
    autoGitPull2()