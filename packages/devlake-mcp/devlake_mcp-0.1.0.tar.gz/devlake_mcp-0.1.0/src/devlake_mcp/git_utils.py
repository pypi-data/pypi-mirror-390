#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Git 信息获取工具模块

提供 Git 仓库信息的获取功能：
- 当前分支
- 最新 commit hash
- Git 配置的用户名和邮箱
- 项目ID提取（namespace/name）
"""

import subprocess
import os
import re
from pathlib import Path
from typing import Optional


def get_git_info(cwd: str, timeout: int = 1, include_user_info: bool = True) -> dict:
    """
    获取当前项目的 Git 信息

    Args:
        cwd: 项目根目录路径
        timeout: Git 命令超时时间（秒），默认 1 秒
        include_user_info: 是否获取用户信息（git_author/git_email），默认 True
                          如果环境变量已缓存，可以设为 False 提升性能

    Returns:
        Git 信息字典：
        {
            "git_branch": "feature/ai-coding",       # 当前分支
            "git_commit": "abc123def456...",         # 最新 commit hash（完整）
            "git_author": "wangzhong",               # Git 配置的用户名（可选）
            "git_email": "wangzhong@example.com"     # Git 配置的邮箱（可选）
        }

        如果不是 Git 仓库或获取失败，返回 "unknown"

    示例:
        >>> git_info = get_git_info('/path/to/project')
        >>> print(git_info['git_branch'])
        feature/ai-coding

        >>> # 如果用户信息已缓存，可以跳过获取
        >>> git_info = get_git_info('/path/to/project', include_user_info=False)
    """
    git_info = {
        "git_branch": "unknown",
        "git_commit": "unknown",
        "git_author": "unknown",
        "git_email": "unknown"
    }

    try:
        # 1. 检查是否是 Git 仓库
        result = subprocess.run(
            ['git', 'rev-parse', '--is-inside-work-tree'],
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout
        )

        if result.returncode != 0:
            # 不是 Git 仓库
            return git_info

        # 2. 获取当前分支
        result = subprocess.run(
            ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        if result.returncode == 0:
            git_info['git_branch'] = result.stdout.strip()

        # 3. 获取最新 commit hash（完整 40 位）
        result = subprocess.run(
            ['git', 'rev-parse', 'HEAD'],
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        if result.returncode == 0:
            git_info['git_commit'] = result.stdout.strip()

        # 4. 获取 Git 配置的用户名（可选）
        if include_user_info:
            result = subprocess.run(
                ['git', 'config', 'user.name'],
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            if result.returncode == 0:
                git_info['git_author'] = result.stdout.strip()

            # 5. 获取 Git 配置的邮箱（可选）
            result = subprocess.run(
                ['git', 'config', 'user.email'],
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            if result.returncode == 0:
                git_info['git_email'] = result.stdout.strip()

    except subprocess.TimeoutExpired:
        # 超时，返回默认值
        pass
    except Exception:
        # 其他异常，静默失败
        pass

    return git_info


def get_current_branch(cwd: str, timeout: int = 1) -> str:
    """
    快速获取当前 Git 分支（简化版）

    Args:
        cwd: 项目根目录
        timeout: 超时时间（秒）

    Returns:
        分支名称，失败返回 'unknown'
    """
    try:
        result = subprocess.run(
            ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass

    return 'unknown'


def get_git_remote_url(cwd: str, timeout: int = 1) -> Optional[str]:
    """
    获取 Git remote URL

    Args:
        cwd: 项目路径
        timeout: 超时时间（秒）

    Returns:
        Git remote URL，失败返回 None
    """
    try:
        result = subprocess.run(
            ['git', 'config', '--get', 'remote.origin.url'],
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass

    return None


def extract_git_repo_path(git_remote_url: Optional[str], cwd: str) -> str:
    """
    从 Git remote URL 提取 git_repo_path (namespace/name)

    支持的格式：
    - https://github.com/yourorg/devlake.git -> yourorg/devlake
    - git@github.com:yourorg/devlake.git -> yourorg/devlake
    - https://gitlab.com/team/subteam/project.git -> team/subteam/project
    - git@gitlab.com:team/project.git -> team/project

    Args:
        git_remote_url: Git 远程仓库 URL
        cwd: 项目路径（作为 fallback）

    Returns:
        git_repo_path (namespace/name)
        如果无法提取，返回 'local/{directory_name}'
    """
    if not git_remote_url:
        # 没有 Git 仓库，使用 local/{dirname}
        return f"local/{Path(cwd).name}"

    # 去掉 .git 后缀（修复：使用 removesuffix 避免误删末尾字符）
    url = git_remote_url.removesuffix('.git')

    # 提取 namespace/name (支持多级 namespace)
    # 匹配格式：
    # - https://github.com/yourorg/devlake -> yourorg/devlake
    # - git@gitlab.com:team/project -> team/project
    # - https://gitlab.com/team/subteam/project -> team/subteam/project

    patterns = [
        # HTTPS 格式：https://domain.com/namespace/name
        r'https?://[^/]+/(.+)',
        # SSH 格式：git@domain.com:namespace/name
        r'git@[^:]+:(.+)',
    ]

    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)

    # 解析失败，降级到 local/{dirname}
    return f"local/{Path(cwd).name}"


def get_git_repo_path(cwd: str) -> str:
    """
    获取Git仓库路径 (namespace/name)

    Args:
        cwd: 项目路径

    Returns:
        git_repo_path，如 'yourorg/devlake'
    """
    git_remote_url = get_git_remote_url(cwd)
    return extract_git_repo_path(git_remote_url, cwd)


def get_git_root(cwd: str, timeout: int = 1) -> Optional[str]:
    """
    获取 Git 仓库根目录

    Args:
        cwd: 当前工作目录
        timeout: 超时时间（秒）

    Returns:
        Git 仓库根目录的绝对路径，失败返回 None
    """
    try:
        result = subprocess.run(
            ['git', 'rev-parse', '--show-toplevel'],
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass

    return None
