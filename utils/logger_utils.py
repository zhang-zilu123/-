"""
日志工具模块 - 提供通用的日志记录器设置功能
"""
import logging
import os
from typing import Optional

# 导入配置
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.config import LOGGING_CONFIG


def setup_logger(log_name: str, log_dir: str = "logs") -> logging.Logger:
    """
    设置日志记录器

    Args:
        log_name (str): 日志名称
        log_dir (str): 日志存储目录

    Returns:
        logging.Logger: 配置好的日志记录器
    """
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    log_file = os.path.join(log_dir, f"{log_name}.log")
    logger = logging.getLogger(log_name)
    logger.setLevel(logging.INFO)

    # 防止重复添加处理器
    if not logger.handlers:
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    获取日志记录器的便捷函数
    
    Args:
        name: 日志记录器名称
    
    Returns:
        logging.Logger: 日志记录器
    """
    return setup_logger(name)


def set_log_level(logger: logging.Logger, level: str) -> None:
    """
    动态设置日志级别
    
    Args:
        logger: 日志记录器
        level: 新的日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    logger.setLevel(getattr(logging, level.upper()))
    for handler in logger.handlers:
        handler.setLevel(getattr(logging, level.upper()))