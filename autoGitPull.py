import git
import os
import time
from git.repo import Repo
from Robot import robot
from common.Session import Session
from common import Logs, Consts
class updateCode:
    code_path = {'bb_php_path': '/home/webroot/banban',
                 'bb_go_path': '/home/webroot/banban-go/banban-consume',
                 'pt_php_path': '/home/webroot/release_oversea/oversea-server',
                 'bb_git_branch': 'release-for-vpc',
                 'bb_go_git_branch': 'master',
                 'pt_git_branch': 'main'}

    @staticmethod
    def autoGitPull(appInfo):
        if appInfo == 'bb_php':
            gtr_path = updateCode.code_path['bb_php_path']
            git_branch = updateCode.code_path['bb_git_branch']
            env = 'dev'
            bot = 'BB'
        elif appInfo == 'bb_go':
            gtr_path = updateCode.code_path['bb_go_path']
            git_branch = updateCode.code_path['bb_go_git_branch']
            env = 'dev'
            bot = 'BB'
        elif appInfo == 'pt':
            gtr_path = updateCode.code_path['pt_php_path']
            git_branch = updateCode.code_path['pt_git_branch']
            env = 'pt'
            bot = 'PT'
        else:
            Logs.get_log('gitBranchError.log').error("{} error".format(appInfo))
            return

        g = git.cmd.Git(gtr_path)
        g.pull()
        repo = Repo(gtr_path)
        Consts.startTime = time.time()
        Session().getSession(env)  # 更新userToken

        if str(repo.active_branch) == git_branch:  # 当前线上分支
            commit_log = repo.git.log('--pretty={"commit":"%h","author":"%an","summary":"%s","date":"%cd"}',
                                      max_count=3, date='format:%Y-%m-%d %H:%M:%S')
            log_list = commit_log.split("\n")
            Logs.get_log('gitCommitPull.log').info('当前分支: {}, 最新一条commit: {}'
                                                   .format(repo.active_branch, log_list[0]))
            times = int(time.mktime(time.strptime([eval(item) for item in log_list][0]['date'],
                                                  "%Y-%m-%d %H:%M:%S")))  # commit更新时间
            lastTime = int(updateTime('read'))  # 上次脚本执行时间
            if times > lastTime:
                Logs.get_log('updateGitCode.log').info('最新代码提交时间: {}, 上次代码更新时间: {}'.format(times, lastTime))
                robot('success', '{}'.format(log_list[0]), bot=bot)  # git commit update message
                return True
            else:
                Logs.get_log('updateGitCode.log').info("未拉取到{}分支代码，最近代码提交时间: {}, "
                                                       "上次代码更新时间: {}".format(repo.active_branch, times, lastTime))
                return False
        else:
            Logs.get_log('gitBranchError.log').error("git branch error： {}".format(repo.active_branch))
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