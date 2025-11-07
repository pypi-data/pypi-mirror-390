"""
FakeMCP 日志系统配置

提供统一的日志配置和管理功能。
"""

import logging
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime


class ColoredFormatter(logging.Formatter):
    """带颜色的日志格式化器（用于终端输出）"""
    
    # ANSI 颜色代码
    COLORS = {
        'DEBUG': '\033[36m',      # 青色
        'INFO': '\033[32m',       # 绿色
        'WARNING': '\033[33m',    # 黄色
        'ERROR': '\033[31m',      # 红色
        'CRITICAL': '\033[35m',   # 紫色
    }
    RESET = '\033[0m'
    
    def format(self, record):
        # 添加颜色
        if record.levelname in self.COLORS:
            record.levelname = f"{self.COLORS[record.levelname]}{record.levelname}{self.RESET}"
        return super().format(record)


def setup_logging(
    level: str = "INFO",
    log_file: Optional[str] = None,
    log_dir: Optional[str] = None,
    enable_colors: bool = True
) -> None:
    """
    配置日志系统
    
    Args:
        level: 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: 日志文件名（可选）
        log_dir: 日志目录（可选，默认为 logs/）
        enable_colors: 是否在终端输出中启用颜色
    """
    # 获取根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper()))
    
    # 清除现有的处理器
    root_logger.handlers.clear()
    
    # 日志格式
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    
    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, level.upper()))
    
    if enable_colors and sys.stdout.isatty():
        # 使用彩色格式化器
        console_formatter = ColoredFormatter(log_format, datefmt=date_format)
    else:
        console_formatter = logging.Formatter(log_format, datefmt=date_format)
    
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # 文件处理器（如果指定了日志文件）
    if log_file:
        # 创建日志目录
        if log_dir:
            log_path = Path(log_dir)
        else:
            log_path = Path("logs")
        
        log_path.mkdir(parents=True, exist_ok=True)
        
        # 创建文件处理器
        file_handler = logging.FileHandler(
            log_path / log_file,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)  # 文件记录所有级别
        
        # 文件不使用颜色
        file_formatter = logging.Formatter(log_format, datefmt=date_format)
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)


def get_logger(name: str) -> logging.Logger:
    """
    获取日志记录器
    
    Args:
        name: 日志记录器名称（通常使用 __name__）
        
    Returns:
        配置好的日志记录器
    """
    return logging.getLogger(name)


def setup_default_logging() -> None:
    """
    设置默认日志配置
    
    从配置文件读取日志设置并应用。
    """
    try:
        from fakemcp.config import Config
        
        # 生成日志文件名（包含日期）
        log_filename = f"fakemcp_{datetime.now().strftime('%Y%m%d')}.log"
        
        setup_logging(
            level=Config.LOG_LEVEL,
            log_file=log_filename,
            log_dir=str(Path(Config.CACHE_DIR) / "logs"),
            enable_colors=True
        )
        
        logger = get_logger(__name__)
        logger.info("Logging system initialized")
        logger.debug(f"Log level: {Config.LOG_LEVEL}")
        logger.debug(f"Log file: {log_filename}")
        
    except Exception as e:
        # 如果配置失败，使用基本配置
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        logger = logging.getLogger(__name__)
        logger.warning(f"Failed to load config, using default logging: {e}")


class LogContext:
    """
    日志上下文管理器
    
    用于在特定代码块中临时添加上下文信息到日志中。
    """
    
    def __init__(self, logger: logging.Logger, **context):
        self.logger = logger
        self.context = context
        self.old_factory = None
    
    def __enter__(self):
        self.old_factory = logging.getLogRecordFactory()
        
        def record_factory(*args, **kwargs):
            record = self.old_factory(*args, **kwargs)
            for key, value in self.context.items():
                setattr(record, key, value)
            return record
        
        logging.setLogRecordFactory(record_factory)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        logging.setLogRecordFactory(self.old_factory)


def log_function_call(logger: logging.Logger):
    """
    装饰器：记录函数调用
    
    用于调试，记录函数的调用和返回。
    
    Example:
        @log_function_call(logger)
        def my_function(arg1, arg2):
            return arg1 + arg2
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            logger.debug(f"Calling {func.__name__} with args={args}, kwargs={kwargs}")
            try:
                result = func(*args, **kwargs)
                logger.debug(f"{func.__name__} returned: {result}")
                return result
            except Exception as e:
                logger.error(f"{func.__name__} raised {type(e).__name__}: {e}")
                raise
        return wrapper
    return decorator
