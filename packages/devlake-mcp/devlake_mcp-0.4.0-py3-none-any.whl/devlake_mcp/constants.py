#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DevLake MCP 常量配置

集中管理所有魔法值，提高代码可维护性。
"""

from typing import Set

# ============================================================================
# Git 配置
# ============================================================================

# Git 命令超时时间（秒）
GIT_COMMAND_TIMEOUT: int = 1


# ============================================================================
# 文件过滤配置
# ============================================================================

# 敏感文件模式（包含这些关键词的文件不采集）
SENSITIVE_FILE_PATTERNS: list[str] = [
    '.env',
    '.env.',           # .env.local, .env.production 等
    '.secret',
    '.secrets',
    '.key',
    '.pem',
    '.crt',
    '.p12',
    '.pfx',
    'credentials',
    'password',
    '.npmrc',          # npm 配置
    '.pypirc',         # PyPI 配置
    'id_rsa',          # SSH 私钥
    'id_dsa',
    'id_ecdsa',
    'id_ed25519',
]

# 敏感目录（这些目录下的文件不采集）
SENSITIVE_DIRS: list[str] = [
    '.ssh',
    '.gnupg',
    '.aws',
    '.azure',
    '.config',
    'node_modules',    # 前端依赖
    '.venv',           # Python 虚拟环境
    'venv',
    '__pycache__',
    '.git',            # Git 元数据
]

# 二进制文件扩展名（这些文件不采集）
BINARY_FILE_EXTENSIONS: Set[str] = {
    # 图片
    '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.ico', '.svg', '.webp',
    # 压缩包
    '.zip', '.tar', '.gz', '.bz2', '.rar', '.7z', '.xz',
    # 文档
    '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
    # 可执行文件
    '.exe', '.dll', '.so', '.dylib', '.app', '.dmg',
    # 编译产物
    '.class', '.pyc', '.pyo', '.o', '.a', '.jar',
    # 音视频
    '.mp3', '.mp4', '.avi', '.mov', '.wav', '.flac',
    # 字体
    '.ttf', '.otf', '.woff', '.woff2', '.eot',
}


# ============================================================================
# API 配置
# ============================================================================

# API 请求超时时间（秒）
API_REQUEST_TIMEOUT: int = 5

# API 默认基础 URL
DEFAULT_API_BASE_URL: str = "http://devlake.test.chinawayltd.com"

# 最大内容大小（字节）- 10MB
MAX_CONTENT_SIZE: int = 10 * 1024 * 1024


# ============================================================================
# 临时文件配置
# ============================================================================

# 临时文件最大保留时间（小时）
TEMP_FILE_MAX_AGE_HOURS: int = 24

# 临时目录默认名称
TEMP_DIR_NAME: str = 'devlake_mcp'


# ============================================================================
# Hooks 配置
# ============================================================================

# Hook 执行超时时间（秒）
HOOK_EXECUTION_TIMEOUT: int = 5

# Hook 日志目录
HOOK_LOG_DIR: str = '.claude/logs'  # Claude Code hooks 日志目录
CURSOR_HOOK_LOG_DIR: str = '.cursor/logs'  # Cursor hooks 日志目录

# 默认 IDE 类型
DEFAULT_IDE_TYPE: str = 'claude_code'

# 默认模型名称
DEFAULT_MODEL_NAME: str = 'claude-sonnet-4-5'


# ============================================================================
# Generation 配置
# ============================================================================

# Generation 状态文件名
GENERATION_STATE_FILE_NAME: str = 'generation_state.json'

# Generation 状态最大保留时间（小时）- 超过此时间的状态可以被清理
GENERATION_STATE_MAX_AGE_HOURS: int = 24


# ============================================================================
# Transcript 压缩配置
# ============================================================================

# Transcript 压缩阈值（字节）- 超过此大小才进行压缩
# 1MB = 1 * 1024 * 1024 bytes * 0.5
TRANSCRIPT_COMPRESSION_THRESHOLD: int = 1 * 1024 * 1024 * 0.5

# Transcript 压缩算法
TRANSCRIPT_COMPRESSION_ALGORITHM: str = 'gzip'


# ============================================================================
# 日志配置
# ============================================================================

# 日志级别映射（字符串 -> logging 常量）
VALID_LOG_LEVELS: dict[str, int] = {
    'DEBUG': 10,     # logging.DEBUG
    'INFO': 20,      # logging.INFO
    'WARNING': 30,   # logging.WARNING
    'ERROR': 40,     # logging.ERROR
    'CRITICAL': 50,  # logging.CRITICAL
}

# 默认日志级别
DEFAULT_LOG_LEVEL: str = 'INFO'
