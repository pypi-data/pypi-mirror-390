#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP 工具函数模块

提供跨工具的通用功能：
- 临时目录和文件管理
- 内容压缩（gzip + base64）
- 文件过滤（排除敏感文件和二进制文件）
"""

import os
import gzip
import base64
import hashlib
import tempfile
from pathlib import Path
from typing import Optional


def get_temp_dir() -> Path:
    """
    获取跨平台的临时目录

    优先级：
    1. 环境变量 DEVLAKE_MCP_TEMP_DIR
    2. 系统临时目录 + /devlake_mcp

    Returns:
        临时目录路径
        - Windows: C:\\Users\\xxx\\AppData\\Local\\Temp\\devlake_mcp
        - macOS:   /var/folders/xxx/T/devlake_mcp
        - Linux:   /tmp/devlake_mcp
    """
    custom_dir = os.getenv('DEVLAKE_MCP_TEMP_DIR')
    if custom_dir:
        temp_dir = Path(custom_dir)
    else:
        temp_dir = Path(tempfile.gettempdir()) / 'devlake_mcp'

    temp_dir.mkdir(parents=True, exist_ok=True)
    return temp_dir


def get_temp_file_path(session_id: str, file_path: str) -> str:
    """
    生成临时文件路径（用于存储 before_content）

    Args:
        session_id: 会话ID
        file_path: 文件路径

    Returns:
        临时文件路径（格式：{temp_dir}/{session_id}_{file_hash}.before）
    """
    # 使用文件路径的 hash 作为文件名（避免路径过长）
    file_hash = hashlib.md5(file_path.encode()).hexdigest()[:16]

    # 获取跨平台临时目录
    temp_dir = get_temp_dir()

    # 临时文件名：{session_id}_{file_hash}.before
    temp_file = temp_dir / f"{session_id}_{file_hash}.before"

    return str(temp_file)


def compress_content(content: str) -> str:
    """
    压缩内容（gzip + base64）

    Args:
        content: 原始内容

    Returns:
        base64 编码的 gzip 压缩内容
    """
    try:
        if not content:
            return ''
        compressed = gzip.compress(content.encode('utf-8'))
        return base64.b64encode(compressed).decode('ascii')
    except Exception:
        return ''


def should_collect_file(file_path: str) -> bool:
    """
    判断是否应该采集该文件

    排除规则：
    1. 敏感文件：.env, .secret, .key
    2. 二进制文件：图片、压缩包、可执行文件等

    Args:
        file_path: 文件路径

    Returns:
        True 表示应该采集，False 表示跳过
    """
    # 排除敏感文件
    sensitive_patterns = ['.env', '.secret', '.key']
    file_path_lower = file_path.lower()

    for pattern in sensitive_patterns:
        if pattern in file_path_lower:
            return False

    # 排除二进制文件（通过后缀判断）
    binary_extensions = {
        '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.ico',
        '.pdf', '.zip', '.tar', '.gz', '.rar',
        '.exe', '.dll', '.so', '.dylib',
        '.class', '.pyc', '.pyo'
    }

    file_ext = Path(file_path).suffix.lower()
    if file_ext in binary_extensions:
        return False

    return True


def get_file_type(file_path: str) -> str:
    """
    获取文件类型（扩展名）

    Args:
        file_path: 文件路径

    Returns:
        文件扩展名（不含点），如果没有扩展名返回 'unknown'
    """
    return Path(file_path).suffix.lstrip('.') or 'unknown'


def read_file_content(file_path: str) -> str:
    """
    读取文件内容

    Args:
        file_path: 文件路径

    Returns:
        文件内容，读取失败返回空字符串
    """
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
    except Exception:
        pass

    return ''
