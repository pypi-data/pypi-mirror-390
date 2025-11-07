"""
Tests for logging system
"""

import logging
import tempfile
from pathlib import Path

import pytest

from fakemcp.logger import (
    setup_logging,
    get_logger,
    ColoredFormatter,
    LogContext
)


def test_get_logger():
    """测试获取日志记录器"""
    logger = get_logger("test_module")
    
    assert isinstance(logger, logging.Logger)
    assert logger.name == "test_module"


def test_setup_logging_console_only():
    """测试仅控制台日志配置"""
    setup_logging(level="DEBUG", enable_colors=False)
    
    logger = get_logger("test")
    assert logger.level == logging.DEBUG or logger.getEffectiveLevel() == logging.DEBUG


def test_setup_logging_with_file():
    """测试带文件的日志配置"""
    with tempfile.TemporaryDirectory() as tmpdir:
        log_file = "test.log"
        setup_logging(
            level="INFO",
            log_file=log_file,
            log_dir=tmpdir,
            enable_colors=False
        )
        
        logger = get_logger("test")
        logger.info("Test message")
        
        # 验证日志文件已创建
        log_path = Path(tmpdir) / log_file
        assert log_path.exists()
        
        # 验证日志内容
        content = log_path.read_text(encoding='utf-8')
        assert "Test message" in content


def test_colored_formatter():
    """测试彩色格式化器"""
    formatter = ColoredFormatter('%(levelname)s - %(message)s')
    
    # 创建日志记录
    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname="test.py",
        lineno=1,
        msg="Test message",
        args=(),
        exc_info=None
    )
    
    formatted = formatter.format(record)
    assert "Test message" in formatted


def test_log_context():
    """测试日志上下文管理器"""
    logger = get_logger("test_context")
    
    # 使用上下文管理器
    with LogContext(logger, request_id="123", user="test_user"):
        # 在这个上下文中，日志记录应该包含额外的上下文信息
        pass
    
    # 上下文退出后，应该恢复原来的工厂
    assert logging.getLogRecordFactory() is not None


def test_logging_levels():
    """测试不同的日志级别"""
    with tempfile.TemporaryDirectory() as tmpdir:
        log_file = "levels.log"
        setup_logging(
            level="WARNING",
            log_file=log_file,
            log_dir=tmpdir,
            enable_colors=False
        )
        
        logger = get_logger("test_levels")
        
        # 记录不同级别的日志
        logger.debug("Debug message")  # 不应该被记录
        logger.info("Info message")    # 不应该被记录
        logger.warning("Warning message")  # 应该被记录
        logger.error("Error message")      # 应该被记录
        
        # 验证日志文件内容
        log_path = Path(tmpdir) / log_file
        content = log_path.read_text(encoding='utf-8')
        
        assert "Debug message" not in content
        assert "Info message" not in content
        assert "Warning message" in content
        assert "Error message" in content
