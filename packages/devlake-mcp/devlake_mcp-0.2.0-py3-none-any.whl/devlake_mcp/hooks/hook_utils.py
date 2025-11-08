#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Claude Code Hooks 公共工具模块

提供跨 hooks 脚本的通用功能：
- 错误日志记录
- 本地队列保存（降级方案）
- 统一的 logging 配置
- 异步执行包装

注意：临时目录等通用功能已移至 devlake_mcp.utils，避免重复代码
"""

import os
import sys
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Callable

# 导入通用工具函数（避免代码重复）
from devlake_mcp.utils import get_temp_dir, get_temp_file_path
from devlake_mcp.constants import HOOK_LOG_DIR

# 注意：hook_utils 是基础模块，不导入其他 hooks 模块以避免循环依赖


def log_error(log_file: str, context: str, error: Exception = None):
    """
    记录错误日志到文件

    Args:
        log_file: 日志文件名（如 'session_start_errors.log'）
        context: 错误上下文描述
        error: 异常对象（可选）

    示例:
        log_error('session_start.log', 'Failed to upload session', e)
    """
    try:
        print(f"[{datetime.now().isoformat()}] {context}\n")
        if error:
            print(f"Error: {str(error)}\n")
        print("---\n")
        log_path = Path(HOOK_LOG_DIR) / log_file
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(f"[{datetime.now().isoformat()}] {context}\n")
            if error:
                f.write(f"Error: {str(error)}\n")
            f.write("---\n")
    except:
        # 静默失败，避免影响主流程
        pass


def save_to_local_queue(queue_name: str, data: dict):
    """
    保存数据到本地队列（降级方案）

    用于 API 上传失败时的备份，后续可通过定时脚本重试上传

    Args:
        queue_name: 队列名称（如 'failed_session_uploads'）
        data: 要保存的数据字典

    文件格式:
        /tmp/claude_hooks/{queue_name}/{timestamp}.json
    """
    try:
        queue_dir = get_temp_dir() / queue_name
        queue_dir.mkdir(parents=True, exist_ok=True)

        # 使用时间戳作为文件名，确保唯一性
        filename = f"{int(datetime.now().timestamp() * 1000)}.json"
        queue_file = queue_dir / filename

        with open(queue_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except:
        # 静默失败
        pass


def cleanup_old_files(directory: str, max_age_hours: int = 24):
    """
    清理指定目录中的过期文件

    Args:
        directory: 目录名称（相对于临时目录）
        max_age_hours: 最大保留时间（小时）

    示例:
        cleanup_old_files('failed_session_uploads', max_age_hours=168)  # 7天
    """
    try:
        target_dir = get_temp_dir() / directory
        if not target_dir.exists():
            return

        now = datetime.now().timestamp()
        max_age_seconds = max_age_hours * 3600

        for file in target_dir.iterdir():
            if file.is_file():
                file_age = now - file.stat().st_mtime
                if file_age > max_age_seconds:
                    file.unlink()
    except:
        pass


def setup_logger(name: str, log_file: str = None, level: int = logging.DEBUG) -> logging.Logger:
    """
    配置统一的 logger

    Args:
        name: logger 名称（通常使用 __name__）
        log_file: 日志文件名（如 'stop_hook.log'），放在 .claude/logs/ 目录
        level: 日志级别（默认 DEBUG）

    Returns:
        配置好的 logger 实例

    示例:
        logger = setup_logger(__name__, 'session_start.log')
        logger.info('Session started')
        logger.error('Failed to upload', exc_info=True)
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # 避免重复添加 handler
    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # 文件 handler
    if log_file:
        log_dir = Path(HOOK_LOG_DIR)
        log_dir.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_dir / log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    # 控制台 handler（输出到 stderr，不干扰 stdout）
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger


def run_async(func: Callable):
    """
    异步执行装饰器，让 hook 立即返回，后台执行任务

    原理：
    - 使用 os.fork() 创建子进程（Unix-like 系统）
    - 父进程立即退出（返回给 Claude）
    - 子进程继续执行实际的 API 调用等耗时操作

    使用方法：
        @run_async
        def main():
            # 你的 hook 逻辑
            pass

        if __name__ == '__main__':
            main()

    优点：
    - hook 0 延迟，不阻塞 Claude 响应
    - API 调用慢或失败不影响用户体验
    - 子进程独立运行，父进程立即退出
    - 不需要序列化函数（避免 pickle 问题）

    注意：
    - 只在 Unix-like 系统（macOS/Linux）使用 fork
    - Windows 会降级为同步执行（因为 fork 不可用）
    """
    def wrapper(*args, **kwargs):
        # 检查是否支持 fork（Unix-like 系统）
        if sys.platform == 'win32' or not hasattr(os, 'fork'):
            # Windows 或不支持 fork 的系统，降级为同步执行
            func(*args, **kwargs)
            return

        # 使用 os.fork() 创建子进程
        try:
            pid = os.fork()
        except OSError:
            # fork 失败，降级为同步执行
            func(*args, **kwargs)
            return

        if pid > 0:
            # 父进程：立即退出
            sys.exit(0)
        else:
            # 子进程：执行实际的 hook 逻辑
            try:
                func(*args, **kwargs)
                sys.exit(0)
            except Exception:
                # 子进程中的异常不影响父进程
                sys.exit(1)

    return wrapper
