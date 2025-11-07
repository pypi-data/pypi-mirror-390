"""
Configuration management for FakeMCP

This module provides centralized configuration management for the FakeMCP server,
including database paths, cache settings, logging configuration, and server metadata.

Environment Variables:
    FAKEMCP_DB_PATH: Path to SQLite database file
    FAKEMCP_CACHE_DIR: Directory for caching schemas and example data
    FAKEMCP_LOG_LEVEL: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    FAKEMCP_LOG_FILE: Path to log file
    FAKEMCP_CACHE_TTL: Cache time-to-live in seconds
    FAKEMCP_MAX_CACHE_SIZE: Maximum cache size in MB
"""

import os
from pathlib import Path
from typing import Optional


class Config:
    """
    FakeMCP 配置管理
    
    提供所有配置项的集中管理，支持通过环境变量覆盖默认值。
    """
    
    # ========== 数据库配置 ==========
    DATABASE_PATH = os.getenv(
        "FAKEMCP_DB_PATH",
        str(Path.home() / ".fakemcp" / "fakemcp.db")
    )
    
    # ========== 缓存配置 ==========
    CACHE_DIR = os.getenv(
        "FAKEMCP_CACHE_DIR",
        str(Path.home() / ".fakemcp" / "cache")
    )
    
    # 缓存过期时间（秒）
    CACHE_TTL = int(os.getenv("FAKEMCP_CACHE_TTL", "3600"))  # 1 小时
    
    # 最大缓存大小（MB）
    MAX_CACHE_SIZE = int(os.getenv("FAKEMCP_MAX_CACHE_SIZE", "100"))
    
    # ========== 日志配置 ==========
    LOG_LEVEL = os.getenv("FAKEMCP_LOG_LEVEL", "INFO")
    LOG_FILE = os.getenv(
        "FAKEMCP_LOG_FILE",
        str(Path.home() / ".fakemcp" / "fakemcp.log")
    )
    
    # 日志文件最大大小（MB）
    LOG_MAX_SIZE = int(os.getenv("FAKEMCP_LOG_MAX_SIZE", "10"))
    
    # 日志文件备份数量
    LOG_BACKUP_COUNT = int(os.getenv("FAKEMCP_LOG_BACKUP_COUNT", "5"))
    
    # ========== MCP 服务器配置 ==========
    SERVER_NAME = "FakeMCP"
    SERVER_VERSION = "0.1.0"
    SERVER_DESCRIPTION = "A special MCP server that simulates other MCP servers for testing AI Agents"
    
    # ========== 数据生成配置 ==========
    # 默认时间序列数据点数量
    DEFAULT_TIMESERIES_POINTS = int(os.getenv("FAKEMCP_TIMESERIES_POINTS", "100"))
    
    # 默认时间间隔（秒）
    DEFAULT_TIME_INTERVAL = int(os.getenv("FAKEMCP_TIME_INTERVAL", "60"))
    
    # ========== 目标 MCP 连接配置 ==========
    # 连接超时（秒）
    TARGET_MCP_TIMEOUT = int(os.getenv("FAKEMCP_TARGET_TIMEOUT", "30"))
    
    # 最大重试次数
    TARGET_MCP_MAX_RETRIES = int(os.getenv("FAKEMCP_MAX_RETRIES", "3"))
    
    @classmethod
    def ensure_directories(cls):
        """
        确保必要的目录存在
        
        创建数据库、缓存和日志文件所需的目录结构。
        如果目录已存在则不做任何操作。
        """
        Path(cls.DATABASE_PATH).parent.mkdir(parents=True, exist_ok=True)
        Path(cls.CACHE_DIR).mkdir(parents=True, exist_ok=True)
        Path(cls.LOG_FILE).parent.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def validate(cls) -> bool:
        """
        验证配置的有效性
        
        Returns:
            bool: 配置是否有效
            
        Raises:
            ValueError: 配置无效时抛出异常
        """
        # 验证日志级别
        valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if cls.LOG_LEVEL.upper() not in valid_log_levels:
            raise ValueError(
                f"Invalid LOG_LEVEL: {cls.LOG_LEVEL}. "
                f"Must be one of {valid_log_levels}"
            )
        
        # 验证数值配置
        if cls.CACHE_TTL < 0:
            raise ValueError(f"CACHE_TTL must be non-negative, got {cls.CACHE_TTL}")
        
        if cls.MAX_CACHE_SIZE <= 0:
            raise ValueError(f"MAX_CACHE_SIZE must be positive, got {cls.MAX_CACHE_SIZE}")
        
        if cls.TARGET_MCP_TIMEOUT <= 0:
            raise ValueError(f"TARGET_MCP_TIMEOUT must be positive, got {cls.TARGET_MCP_TIMEOUT}")
        
        if cls.TARGET_MCP_MAX_RETRIES < 0:
            raise ValueError(f"TARGET_MCP_MAX_RETRIES must be non-negative, got {cls.TARGET_MCP_MAX_RETRIES}")
        
        return True
    
    @classmethod
    def get_config_summary(cls) -> dict:
        """
        获取配置摘要
        
        Returns:
            dict: 配置信息字典
        """
        return {
            "server": {
                "name": cls.SERVER_NAME,
                "version": cls.SERVER_VERSION,
                "description": cls.SERVER_DESCRIPTION
            },
            "database": {
                "path": cls.DATABASE_PATH
            },
            "cache": {
                "dir": cls.CACHE_DIR,
                "ttl": cls.CACHE_TTL,
                "max_size_mb": cls.MAX_CACHE_SIZE
            },
            "logging": {
                "level": cls.LOG_LEVEL,
                "file": cls.LOG_FILE,
                "max_size_mb": cls.LOG_MAX_SIZE,
                "backup_count": cls.LOG_BACKUP_COUNT
            },
            "target_mcp": {
                "timeout": cls.TARGET_MCP_TIMEOUT,
                "max_retries": cls.TARGET_MCP_MAX_RETRIES
            },
            "data_generation": {
                "timeseries_points": cls.DEFAULT_TIMESERIES_POINTS,
                "time_interval": cls.DEFAULT_TIME_INTERVAL
            }
        }
