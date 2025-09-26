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
    设置日志记录器，同时输出到文件和终端

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
        # 创建格式化器
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        
        # 文件处理器
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

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
    动态设置日志级别，同时控制文件和终端输出
    
    Args:
        logger: 日志记录器
        level: 新的日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    log_level = getattr(logging, level.upper())
    logger.setLevel(log_level)
    
    # 同时设置所有处理器的日志级别
    for handler in logger.handlers:
        handler.setLevel(log_level)


def toggle_console_output(logger: logging.Logger, enable: bool = True) -> None:
    """
    开启或关闭控制台日志输出
    
    Args:
        logger: 日志记录器
        enable: True开启控制台输出，False关闭
    """
    if enable:
        # 检查是否已有控制台处理器
        has_console = any(isinstance(h, logging.StreamHandler) and not isinstance(h, logging.FileHandler) 
                         for h in logger.handlers)
        if not has_console:
            console_handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            console_handler.setFormatter(formatter)
            console_handler.setLevel(logger.level)
            logger.addHandler(console_handler)
    else:
        # 移除控制台处理器
        handlers_to_remove = []
        for handler in logger.handlers:
            if isinstance(handler, logging.StreamHandler) and not isinstance(handler, logging.FileHandler):
                handlers_to_remove.append(handler)
        
        for handler in handlers_to_remove:
            logger.removeHandler(handler)