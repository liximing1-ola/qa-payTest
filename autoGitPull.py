"""
Auto Git Pull Module
Automatically pull code updates and notify via robot
"""
import os
import json
import git
from datetime import datetime
from time import time
from git.repo import Repo
from Robot import robot
from common import Logs, Consts
from common.Config import config
from common.Session import Session


# Constants
TIME_FILE = 'time.txt'
DEFAULT_TIMESTAMP = '1600000000'
DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'


class GitUpdater:
    """Git code updater with notification"""

    APP_CONFIGS = {
        'bb_php': {'path_key': 'bb_php_path', 'branch_key': 'bb_git_branch', 'env': 'dev', 'bot': 'BB'},
        'bb_go': {'path_key': 'bb_go_path', 'branch_key': 'bb_go_git_branch', 'env': 'dev', 'bot': 'BB'},
        'pt': {'path_key': 'pt_php_path', 'branch_key': 'pt_git_branch', 'env': 'pt', 'bot': 'PT'},
        'slp_php': {'path_key': 'slp_php_path', 'branch_key': 'slp_git_branch', 'env': 'slp', 'bot': 'slp'},
        'slp_common_rpc': {'path_key': 'slp_common_rpc_path', 'branch_key': 'slp_git_branch', 'env': 'slp', 'bot': 'slp'}
    }

    NOTIFICATION_MODES = {
        'pt': 'slack_pt',
        'slp_php': 'slack',
        'slp_common_rpc': 'slack'
    }

    def __init__(self):
        self.logger_pull = Logs.get_logger('gitCommitPull.log')
        self.logger_update = Logs.get_logger('updateGitCode.log')
        self.logger_error = Logs.get_logger('gitBranchError.log')

    def _get_config(self, app_info):
        """Get application configuration"""
        cfg = self.APP_CONFIGS.get(app_info)
        if not cfg:
            self.logger_error.error(f"Unknown app info: {app_info}")
            return None
        return {
            'path': config.codeInfo[cfg['path_key']],
            'branch': config.codeInfo[cfg['branch_key']],
            'env': cfg['env'],
            'bot': cfg['bot']
        }

    def _parse_commit_time(self, commit_data):
        """Parse commit date to timestamp"""
        try:
            commit_dict = json.loads(commit_data)
            dt = datetime.strptime(commit_dict['date'], DATETIME_FORMAT)
            return int(dt.timestamp())
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            self.logger_error.error(f"Failed to parse commit date: {e}")
            return 0

    def _send_notification(self, app_info, commit_info, bot, to='slack'):
        """Send notification"""
        mode = self.NOTIFICATION_MODES.get(app_info, 'slack')
        robot(mode, commit_info, bot=bot, to=to)

    def _pull_code(self, path, app_info):
        """Pull code if needed"""
        if not app_info.startswith('slp'):
            git.cmd.Git(path).pull()
            self.logger_pull.info(f"Pulled code for {app_info}")
        else:
            self.logger_pull.info(f"Skipped pulling code for {app_info}")

    def _get_commits(self, repo):
        """Get latest commits"""
        log = repo.git.log(
            '--pretty={"commit":"%h","author":"%an","summary":"%s","date":"%cd"}',
            max_count=3,
            date=f'format:{DATETIME_FORMAT}'
        )
        return log.strip().split('\n')

    def autoGitPull(self, app_info, env='dev', bot='BB', to='slack'):
        """
        Automatically pull git code and send notifications
        
        Returns:
            bool: True if update successful, False otherwise
        """
        cfg = self._get_config(app_info)
        if not cfg:
            return False

        try:
            # Pull code
            self._pull_code(cfg['path'], app_info)

            # Init repo and session
            repo = Repo(cfg['path'])
            Consts.startTime = time()
            Session.getSession(cfg['env'])

            # Get commits
            commits = self._get_commits(repo)
            current_branch = str(repo.active_branch)
            self.logger_pull.info(f'Branch: {current_branch}, Latest: {commits[0]}')

            # Check branch
            if current_branch != cfg['branch']:
                self.logger_error.error(f"Branch mismatch: expected {cfg['branch']}, got {current_branch}")
                return False

            # Check commit time
            latest_time = self._parse_commit_time(commits[0])
            last_time = int(update_time('read'))
            self.logger_update.info(f'Latest: {latest_time}, Last: {last_time}')

            if latest_time > last_time:
                self._send_notification(app_info, commits[0], cfg['bot'], to)
                self.logger_update.info("Code update notification sent")
                return True
            else:
                self.logger_update.info(f"No new code for branch {current_branch}")
                return False

        except Exception as e:
            self.logger_error.error(f"Error processing {app_info}: {e}")
            return False


def update_time(operate, now=''):
    """Manage update timestamp file"""
    file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), TIME_FILE)
    
    try:
        if operate == 'write':
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(now)
                
        elif operate == 'read':
            if not os.path.exists(file_path):
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(DEFAULT_TIMESTAMP)
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read().strip()
                
        elif operate == 'change':
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(DEFAULT_TIMESTAMP)
                
    except IOError as e:
        print(f"Error handling time file: {e}")
        return DEFAULT_TIMESTAMP if operate == 'read' else None


# Backward compatibility
updateCode = GitUpdater()


if __name__ == '__main__':
    update_time('change')
