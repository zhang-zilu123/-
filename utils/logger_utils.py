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


def setup_logger(name: Optional[str] = None, 
                 level: Optional[str] = None,
                 file_path: Optional[str] = None,
                 format_str: Optional[str] = None) -> logging.Logger:
    """
    设置日志记录器 - 通用函数
    
    Args:
        name: 日志记录器名称，如果为None则使用调用模块的名称
        level: 日志级别，如果为None则使用配置中的默认值
        file_path: 日志文件路径，如果为None则使用配置中的默认值
        format_str: 日志格式字符串，如果为None则使用配置中的默认值
    
    Returns:
        logging.Logger: 配置好的日志记录器
    """
    # 使用传入的参数或配置中的默认值
    logger_name = name or __name__
    log_level = level or LOGGING_CONFIG["level"]
    log_file_path = file_path or LOGGING_CONFIG["file_path"]
    log_format = format_str or LOGGING_CONFIG["format"]
    
    # 获取或创建日志记录器
    logger = logging.getLogger(logger_name)
    logger.setLevel(getattr(logging, log_level))
    
    # 避免重复添加处理器
    if logger.handlers:
        return logger
    
    # 创建文件处理器
    os.makedirs(os.path.dirname(log_file_path), exist_ok=True)
    file_handler = logging.FileHandler(log_file_path, encoding='utf-8')
    file_handler.setLevel(getattr(logging, log_level))
    
    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, log_level))
    
    # 创建格式器
    formatter = logging.Formatter(log_format)
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # 添加处理器到日志记录器
    logger.addHandler(file_handler)
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
    动态设置日志级别
    
    Args:
        logger: 日志记录器
        level: 新的日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    logger.setLevel(getattr(logging, level.upper()))
    for handler in logger.handlers:
        handler.setLevel(getattr(logging, level.upper())) 