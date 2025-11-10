#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
会话生命周期管理模块

功能：
1. 跟踪当前活跃的 session_id/conversation_id
2. 检测会话切换（ID变化）
3. 自动创建新会话（调用 API）
4. 自动结束旧会话（调用 API 更新 session_end_time）
5. 支持 Cursor 和 Claude Code 两种模式

使用方式：
    from devlake_mcp.session_manager import start_new_session, check_and_switch_session

    # 1. SessionStart hook：强制开始新会话
    start_new_session(
        session_id=session_id,
        cwd=cwd,
        ide_type='claude_code'
    )
    # 无论如何都会创建新会话（结束旧的 + 创建新的）

    # 2. UserPromptSubmit hook：智能判断
    check_and_switch_session(
        new_session_id=session_id,
        cwd=cwd,
        ide_type='claude_code'
    )
    # 会智能处理：
    # - 首次会话：创建 session
    # - 会话延续：什么都不做
    # - 会话切换：结束旧的，创建新的
"""

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict

from .client import DevLakeClient
from .utils import get_temp_dir
from .retry_queue import save_failed_upload
from .git_utils import get_git_info, get_git_repo_path
from .version_utils import detect_platform_info
import os

# 配置日志
logger = logging.getLogger(__name__)

# 状态文件路径
STATE_FILE = get_temp_dir() / 'active_session.json'


# ============================================================================
# 状态文件管理
# ============================================================================

def _read_state() -> Optional[Dict]:
    """
    从状态文件读取当前会话信息

    Returns:
        会话状态字典，如果文件不存在或损坏返回 None

    状态格式:
        {
            "session_id": "abc-123",
            "ide_type": "cursor",
            "started_at": "2025-01-08T10:00:00"
        }
    """
    try:
        if STATE_FILE.exists():
            with open(STATE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        logger.warning(f'读取会话状态文件失败: {e}')

    return None


def _write_state(session_id: str, ide_type: str):
    """
    写入会话状态到文件

    Args:
        session_id: 会话 ID
        ide_type: IDE 类型 ('cursor' 或 'claude_code')
    """
    try:
        state = {
            'session_id': session_id,
            'ide_type': ide_type,
            'started_at': datetime.now().isoformat()
        }

        # 确保目录存在
        STATE_FILE.parent.mkdir(parents=True, exist_ok=True)

        with open(STATE_FILE, 'w', encoding='utf-8') as f:
            json.dump(state, f, ensure_ascii=False, indent=2)

        logger.debug(f'会话状态已保存: {session_id} ({ide_type})')
    except Exception as e:
        logger.error(f'保存会话状态失败: {e}')


def _clear_state():
    """清空状态文件"""
    try:
        if STATE_FILE.exists():
            STATE_FILE.unlink()
            logger.debug('会话状态文件已清空')
    except Exception as e:
        logger.warning(f'清空会话状态文件失败: {e}')


# ============================================================================
# 公开 API
# ============================================================================

def get_active_session() -> Optional[str]:
    """
    获取当前活跃的 session_id

    Returns:
        当前活跃的 session_id，如果没有活跃会话返回 None
    """
    state = _read_state()
    return state.get('session_id') if state else None


def set_active_session(session_id: str, ide_type: str = 'claude_code'):
    """
    设置当前活跃会话

    Args:
        session_id: 会话 ID
        ide_type: IDE 类型 ('cursor' 或 'claude_code')
    """
    _write_state(session_id, ide_type)


def _create_session_record(session_id: str, cwd: str, ide_type: str = 'claude_code'):
    """
    创建 session 记录（上传到 DevLake API）

    Args:
        session_id: Session ID
        cwd: 当前工作目录
        ide_type: IDE 类型
    """
    session_data = None
    try:
        # 1. 获取 Git 信息（动态 + 静态）
        git_info = get_git_info(cwd, timeout=1, include_user_info=True)
        git_branch = git_info.get('git_branch', 'unknown')
        git_commit = git_info.get('git_commit', 'unknown')
        git_author = git_info.get('git_author', 'unknown')
        git_email = git_info.get('git_email', 'unknown')

        # 2. 获取 Git 仓库路径（namespace/name）
        git_repo_path = get_git_repo_path(cwd)

        # 3. 从 git_repo_path 提取 project_name
        project_name = git_repo_path.split('/')[-1] if '/' in git_repo_path else git_repo_path

        # 4. 检测平台信息和版本
        platform_info = detect_platform_info(ide_type=ide_type)

        # 5. 构造 session 数据
        session_data = {
            'session_id': session_id,
            'user_name': git_author,
            'ide_type': ide_type,
            'model_name': os.getenv('CLAUDE_MODEL', 'claude-sonnet-4-5'),
            'git_repo_path': git_repo_path,
            'project_name': project_name,
            'cwd': cwd,
            'session_start_time': datetime.now().isoformat(),
            'conversation_rounds': 0,
            'is_adopted': 0,
            'git_branch': git_branch,
            'git_commit': git_commit,
            'git_author': git_author,
            'git_email': git_email,
            # 新增：版本信息
            'devlake_mcp_version': platform_info['devlake_mcp_version'],
            'ide_version': platform_info['ide_version'],
            'data_source': platform_info['data_source']
        }

        logger.info(
            f'准备创建 Session: {session_id}, '
            f'repo: {git_repo_path}, branch: {git_branch}, '
            f'ide: {ide_type} {platform_info["ide_version"] or "unknown"}, '
            f'devlake-mcp: {platform_info["devlake_mcp_version"]}'
        )
        logger.debug(f'session_data 内容: {json.dumps(session_data, ensure_ascii=False, indent=2)}')

        # 5. 调用 DevLake API 创建 session
        with DevLakeClient() as client:
            client.post('/api/ai-coding/sessions', session_data)

        logger.info(f'成功创建 Session: {session_id}')

    except Exception as e:
        # API 调用失败，记录错误但不阻塞
        logger.error(f'创建 Session 失败 ({session_id}): {e}')
        # 保存到本地队列（支持自动重试）
        if session_data:
            save_failed_upload(
                queue_type='session',
                data=session_data,
                error=str(e)
            )


def start_new_session(session_id: str, cwd: str, ide_type: str = 'claude_code'):
    """
    强制开始新会话（SessionStart 专用）

    Args:
        session_id: 会话 ID
        cwd: 当前工作目录（用于获取 Git 信息）
        ide_type: IDE 类型 ('claude_code' 或 'cursor')

    行为:
        1. 如果有活跃会话，先结束它（无论 session_id 是否相同）
        2. 创建新会话并设置为活跃

    用途:
        SessionStart hook 调用，明确表示"新会话开始"
    """
    # 参数验证
    if not session_id:
        logger.warning('session_id 为空，跳过')
        return

    # 读取当前状态
    state = _read_state()

    # 如果有活跃会话，先结束它
    if state:
        old_session_id = state.get('session_id')
        old_ide_type = state.get('ide_type', 'unknown')

        if old_session_id == session_id:
            logger.info(f'重新开始会话（相同 ID）: {session_id}')
        else:
            logger.info(f'结束旧会话: {old_session_id} → 开始新会话: {session_id}')

        # 结束旧会话
        end_session(old_session_id, old_ide_type)

    # 创建新会话
    logger.info(f'创建新会话: {session_id} ({ide_type})')
    _create_session_record(session_id, cwd, ide_type)
    set_active_session(session_id, ide_type)


def check_and_switch_session(
    new_session_id: str,
    cwd: str,
    ide_type: str = 'claude_code'
) -> bool:
    """
    检查会话切换，智能处理会话生命周期（UserPromptSubmit 专用）

    Args:
        new_session_id: 新的 session_id (Claude Code) 或 conversation_id (Cursor)
        cwd: 当前工作目录（用于获取 Git 信息）
        ide_type: IDE 类型 ('claude_code' 或 'claude')

    Returns:
        bool: 是否发生了会话切换（True 表示切换，False 表示首次或延续）

    行为:
        1. 如果是首次会话：创建 session 并设置为活跃 → 返回 False
        2. 如果是同一会话：什么都不做（会话延续） → 返回 False
        3. 如果会话切换：结束旧会话，创建并设置新会话 → 返回 True

    用途:
        UserPromptSubmit hook 调用，智能判断是否需要创建会话
    """
    # 参数验证
    if not new_session_id:
        logger.warning('new_session_id 为空，跳过会话管理')
        return False

    # 读取当前状态
    state = _read_state()

    # 情况1：首次会话
    if not state:
        logger.info(f'首次会话: {new_session_id} ({ide_type})')
        _create_session_record(new_session_id, cwd, ide_type)
        set_active_session(new_session_id, ide_type)
        return False

    current_session_id = state.get('session_id')
    current_ide_type = state.get('ide_type', 'unknown')

    # 情况2：同一会话
    if current_session_id == new_session_id:
        logger.debug(f'会话延续: {new_session_id}')
        return False

    # 情况3：会话切换
    logger.info(
        f'检测到会话切换: {current_session_id} ({current_ide_type}) '
        f'-> {new_session_id} ({ide_type})'
    )

    # 结束旧会话
    end_session(current_session_id, current_ide_type)

    # 创建新会话
    _create_session_record(new_session_id, cwd, ide_type)

    # 保存新会话状态
    set_active_session(new_session_id, ide_type)

    return True


def end_session(session_id: str, ide_type: str = 'claude_code'):
    """
    结束指定会话（更新 session_end_time）

    Args:
        session_id: 要结束的会话 ID
        ide_type: IDE 类型 ('cursor' 或 'claude_code')

    行为:
        1. 调用 DevLake API 更新 session_end_time
        2. 如果 API 调用失败，保存到重试队列
        3. 不抛出异常，静默失败
    """
    try:
        # 构造更新数据
        update_data = {
            'session_end_time': datetime.now().isoformat()
        }

        logger.info(f'准备结束会话: {session_id} ({ide_type})')

        # 调用 DevLake API
        with DevLakeClient() as client:
            client.update_session(session_id, update_data)

        logger.info(f'会话已结束: {session_id}')

    except Exception as e:
        # API 调用失败，记录错误并保存到重试队列
        logger.error(f'结束会话失败 ({session_id}): {e}')

        # 保存到重试队列（支持自动重试）
        save_failed_upload(
            queue_type='session_end',
            data={
                'session_id': session_id,
                'ide_type': ide_type,
                **update_data
            },
            error=str(e)
        )


def clear_session():
    """
    清空当前会话状态

    用途：
    - 手动清理状态（测试或调试）
    - 重置会话跟踪
    """
    _clear_state()
    logger.info('当前会话状态已清空')
