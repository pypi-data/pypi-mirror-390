#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
日志配置模块（简化版）

提供符合 Python logging 最佳实践的配置函数。

使用方法：
    # 在应用/hook 启动时调用一次
    from devlake_mcp.logging_config import configure_logging
    configure_logging(log_dir='.claude/logs', log_file='hook.log')

    # 之后各个模块直接用标准方式
    import logging
    logger = logging.getLogger(__name__)
    logger.info('message')
"""

import os
import logging
from pathlib import Path
from typing import Optional

from .constants import VALID_LOG_LEVELS, DEFAULT_LOG_LEVEL


def configure_logging(
    log_dir: Optional[str] = None,
    log_file: Optional[str] = None
):
    """
    配置全局 logging（在应用启动时调用一次）

    根据环境变量配置日志行为：
    - DEVLAKE_MCP_LOGGING_ENABLED: 是否启用（默认 true）
    - DEVLAKE_MCP_LOG_LEVEL: 日志级别（默认 INFO）

    Args:
        log_dir: 日志文件目录（可选）
        log_file: 日志文件名（可选）

    示例：
        >>> from devlake_mcp.logging_config import configure_logging
        >>> configure_logging(log_dir='.claude/logs', log_file='hook.log')
        >>>
        >>> import logging
        >>> logger = logging.getLogger(__name__)
        >>> logger.info('Hello')
    """
    # 读取环境变量
    enabled = os.getenv('DEVLAKE_MCP_LOGGING_ENABLED', 'true').lower() in ('true', '1', 'yes')
    level_str = os.getenv('DEVLAKE_MCP_LOG_LEVEL', DEFAULT_LOG_LEVEL).upper()

    # 获取日志级别
    level = VALID_LOG_LEVELS.get(level_str, VALID_LOG_LEVELS[DEFAULT_LOG_LEVEL])

    # 如果禁用，使用 NullHandler
    if not enabled:
        logging.basicConfig(
            level=level,
            handlers=[logging.NullHandler()]
        )
        return

    # 准备 handlers
    handlers = []
    formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # 文件 handler（如果提供了 log_dir 和 log_file）
    if log_dir and log_file:
        try:
            Path(log_dir).mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(
                Path(log_dir) / log_file,
                encoding='utf-8'
            )
            file_handler.setFormatter(formatter)
            file_handler.setLevel(level)
            handlers.append(file_handler)
        except Exception as e:
            # 创建文件 handler 失败，只用控制台
            print(f"警告：无法创建日志文件 {log_dir}/{log_file}: {e}")

    # 控制台 handler（总是添加）
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(level)
    handlers.append(console_handler)

    # 配置全局 logging
    logging.basicConfig(
        level=level,
        handlers=handlers,
        force=True  # 覆盖已有配置
    )

    # 抑制第三方库的 DEBUG 日志
    for lib in ['urllib3', 'urllib3.connectionpool', 'requests']:
        logging.getLogger(lib).setLevel(logging.WARNING)
