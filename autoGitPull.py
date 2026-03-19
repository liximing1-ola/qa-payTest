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
APP_CONFIGS = {
    'bb_php': {
        'path_key': 'bb_php_path',
        'branch_key': 'bb_git_branch',
        'env': 'dev',
        'bot': 'BB'
    },
    'bb_go': {
        'path_key': 'bb_go_path',
        'branch_key': 'bb_go_git_branch',
        'env': 'dev',
        'bot': 'BB'
    },
    'pt': {
        'path_key': 'pt_php_path',
        'branch_key': 'pt_git_branch',
        'env': 'pt',
        'bot': 'PT'
    },
    'slp_php': {
        'path_key': 'slp_php_path',
        'branch_key': 'slp_git_branch',
        'env': 'slp',
        'bot': 'slp'
    },
    'slp_common_rpc': {
        'path_key': 'slp_common_rpc_path',
        'branch_key': 'slp_git_branch',
        'env': 'slp',
        'bot': 'slp'
    }
}

TIME_FILE = 'time.txt'
DEFAULT_TIMESTAMP = '1600000000'
DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'


class GitUpdater:
    """Git code updater with notification"""

    def __init__(self):
        self.logger_pull = Logs.get_log('gitCommitPull.log')
        self.logger_update = Logs.get_log('updateGitCode.log')
        self.logger_error = Logs.get_log('gitBranchError.log')

    def _get_app_config(self, app_info):
        """Get application configuration by app info"""
        if app_info not in APP_CONFIGS:
            self.logger_error.error(f"Unknown app info: {app_info}")
            return None
        
        config_data = APP_CONFIGS[app_info]
        return {
            'path': config.codeInfo[config_data['path_key']],
            'branch': config.codeInfo[config_data['branch_key']],
            'env': config_data['env'],
            'bot': config_data['bot']
        }

    def _should_pull_code(self, app_info):
        """Check if code should be pulled for this app"""
        return not app_info.startswith('slp')

    def _parse_commit_date(self, commit_data):
        """Parse commit date string to timestamp"""
        try:
            commit_dict = json.loads(commit_data)
            date_str = commit_dict['date']
            dt = datetime.strptime(date_str, DATETIME_FORMAT)
            return int(dt.timestamp())
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            self.logger_error.error(f"Failed to parse commit date: {e}")
            return 0

    def _send_notification(self, app_info, commit_info, bot, to='slack'):
        """Send notification based on app type"""
        notification_map = {
            'pt': lambda: robot('slack_pt', commit_info, bot=bot),
            'slp_php': lambda: self._send_slp_notification(commit_info, bot, to),
            'slp_common_rpc': lambda: self._send_slp_notification(commit_info, bot, to),
        }
        
        handler = notification_map.get(app_info)
        if handler:
            handler()
        else:
            robot('slack', commit_info, bot=bot)

    def _send_slp_notification(self, commit_info, bot, to):
        """Send SLP notification"""
        if to == 'slack':
            robot('slack', commit_info, bot=bot, to=to)
        else:
            robot('markdown', commit_info, bot=bot, to=to)

    def auto_git_pull(self, app_info, env='dev', bot='BB', to='slack'):
        """
        Automatically pull git code and send notifications
        
        Args:
            app_info (str): Application identifier
            env (str): Environment name
            bot (str): Bot identifier
            to (str): Notification target
            
        Returns:
            bool: True if update successful, False otherwise
        """
        # Get app configuration
        app_config = self._get_app_config(app_info)
        if not app_config:
            return False

        path = app_config['path']
        expected_branch = app_config['branch']
        actual_env = app_config['env']
        actual_bot = app_config['bot']

        try:
            # Pull code if needed
            if self._should_pull_code(app_info):
                git_client = git.cmd.Git(path)
                git_client.pull()
                self.logger_pull.info(f"Pulled code for {app_info}")
            else:
                self.logger_pull.info(f"Skipped pulling code for {app_info}")

            # Initialize repository
            repo = Repo(path)
            
            # Update session token
            Consts.startTime = time()
            Session.getSession(actual_env)
            
            # Get latest commits
            commit_log = repo.git.log(
                '--pretty={"commit":"%h","author":"%an","summary":"%s","date":"%cd"}',
                max_count=3,
                date='format:%Y-%m-%d %H:%M:%S'
            )
            commit_list = commit_log.strip().split('\n')
            
            current_branch = str(repo.active_branch)
            self.logger_pull.info(f'Current branch: {current_branch}, Latest commit: {commit_list[0]}')

            # Check branch
            if current_branch != expected_branch:
                self.logger_error.error(f"Branch mismatch: expected {expected_branch}, got {current_branch}")
                return False

            # Check commit time
            latest_commit_time = self._parse_commit_date(commit_list[0])
            last_update_time = int(update_time('read'))
            
            self.logger_update.info(
                f'Latest commit time: {latest_commit_time}, Last update time: {last_update_time}'
            )

            if latest_commit_time > last_update_time:
                # Send notification
                self._send_notification(app_info, commit_list[0], actual_bot, to)
                self.logger_update.info("Code update notification sent")
                return True
            else:
                self.logger_update.info(
                    f"No new code pulled for branch {current_branch}. "
                    f"Latest commit time: {latest_commit_time}, Last update time: {last_update_time}"
                )
                return False

        except Exception as e:
            self.logger_error.error(f"Error processing {app_info}: {str(e)}")
            return False


def update_time(operate, now=''):
    """
    Manage update timestamp file
    
    Args:
        operate (str): Operation type ('read', 'write', 'change')
        now (str): Timestamp to write (used with 'write' operation)
        
    Returns:
        str: File content for 'read' operation
    """
    script_dir = os.path.dirname(os.path.realpath(__file__))
    time_file_path = os.path.join(script_dir, TIME_FILE)
    
    try:
        if operate == 'write':
            with open(time_file_path, 'w', encoding='utf-8') as f:
                f.write(now)
                
        elif operate == 'read':
            # Create file with default timestamp if not exists
            if not os.path.exists(time_file_path):
                with open(time_file_path, 'w', encoding='utf-8') as f:
                    f.write(DEFAULT_TIMESTAMP)
            
            with open(time_file_path, 'r', encoding='utf-8') as f:
                return f.read().strip()
                
        elif operate == 'change':
            with open(time_file_path, 'w', encoding='utf-8') as f:
                f.write(DEFAULT_TIMESTAMP)
                
    except IOError as e:
        print(f"Error handling time file: {e}")
        return DEFAULT_TIMESTAMP if operate == 'read' else None


# Backward compatibility
updateCode = GitUpdater()


if __name__ == '__main__':
    update_time('change')
