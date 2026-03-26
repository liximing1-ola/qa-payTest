# coding=utf-8
"""
日志管理模块

使用方式:
    from common.Logs import get_logger
    logger = get_logger('app.log')
    logger.info('message')
"""
import logging
import os
from logging.handlers import TimedRotatingFileHandler
from common.Config import config


# 默认日志配置
DEFAULT_LOG_LEVEL = logging.DEBUG
DEFAULT_WHEN = 'midnight'
DEFAULT_BACK_COUNT = 0
DEFAULT_FORMAT = '%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s'


def _ensure_log_dir() -> str:
    """确保日志目录存在"""
    log_path = os.path.join(config.BASE_PATH, 'log')
    os.makedirs(log_path, exist_ok=True)
    return log_path


def _create_handlers(log_file_path: str, level: int, formatter: logging.Formatter):
    """创建日志处理器"""
    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    # 文件处理器（按时间轮转）
    file_handler = TimedRotatingFileHandler(
        filename=log_file_path,
        when=DEFAULT_WHEN,
        backupCount=DEFAULT_BACK_COUNT,
        encoding='UTF-8'
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)

    return console_handler, file_handler


def get_logger(
    name: str,
    level: int = DEFAULT_LOG_LEVEL,
    when: str = DEFAULT_WHEN,
    back_count: int = DEFAULT_BACK_COUNT
) -> logging.Logger:
    """
    获取日志记录器

    Args:
        name: 日志文件名
        level: 日志级别，默认为DEBUG
        when: 轮转时间单位，默认为'midnight'
        back_count: 备份文件数量，默认为0（不删除）

    Returns:
        logging.Logger: 配置好的日志记录器
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # 避免重复添加handler
    if logger.handlers:
        return logger

    log_path = _ensure_log_dir()
    log_file_path = os.path.join(log_path, name)
    formatter = logging.Formatter(DEFAULT_FORMAT)

    console_handler, file_handler = _create_handlers(log_file_path, level, formatter)
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger
