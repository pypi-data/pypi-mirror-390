#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generation 生命周期管理模块

功能：
1. 管理 generation_id 的生命周期（创建、获取、结束）
2. 支持跨 hook 的 generation 追踪
3. 为每次 AI 交互分配唯一标识

设计：
- generation_id: 一次完整 AI 交互的唯一标识（UUID）
- 状态文件: ~/.devlake/generation_state.json
- 与 session_id 关联

使用方式：
    from devlake_mcp.generation_manager import start_generation, get_current_generation_id, end_generation

    # 在 UserPromptSubmit 中创建
    generation_id = start_generation(session_id)

    # 在 PostToolUse 中获取
    generation_id = get_current_generation_id(session_id)

    # 在 Stop 中结束
    end_generation(session_id)
"""

import json
import logging
import uuid
import os
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Union

from .utils import get_data_dir
from .enums import IDEType

# 配置日志
logger = logging.getLogger(__name__)


# ============================================================================
# 辅助函数
# ============================================================================

def _get_current_pid() -> int:
    """获取当前进程 PID"""
    return os.getpid()


def _get_generation_state_file(ide_type: IDEType) -> Path:
    """
    获取当前进程的 generation 状态文件路径（进程级隔离）

    Args:
        ide_type: IDE 类型枚举

    Returns:
        状态文件路径

    格式: ~/.devlake/generation_<ide_type>_<pid>.json
    例如: ~/.devlake/generation_claude_code_12345.json

    说明:
        使用进程级隔离 + 持久化存储确保：
        1. 不同 IDE 类型（Claude Code/Cursor）互不干扰
        2. 同一 IDE 的多个实例互不干扰
        3. 无需文件锁，每个进程有独立状态文件
        4. 状态文件不会被系统自动清理（使用 ~/.devlake 而非 /tmp）
    """
    pid = _get_current_pid()
    ide_type_str = ide_type.value
    filename = f'generation_{ide_type_str}_{pid}.json'
    return get_data_dir(persistent=True) / filename


# ============================================================================
# 状态文件管理（私有函数）
# ============================================================================

def _read_generation_state(ide_type: IDEType) -> Optional[Dict]:
    """
    从状态文件读取 generation 信息

    Args:
        ide_type: IDE 类型枚举

    Returns:
        Generation 状态字典，如果文件不存在或损坏返回 None

    状态格式:
        {
            "session_id": "abc-123",
            "generation_id": "gen-uuid-456",
            "started_at": "2025-01-08T10:00:00"
        }
    """
    try:
        state_file = _get_generation_state_file(ide_type)
        if state_file.exists():
            with open(state_file, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        logger.warning(f'读取 generation 状态文件失败: {e}')

    return None


def _write_generation_state(session_id: str, generation_id: str, ide_type: IDEType):
    """
    写入 generation 状态到文件

    Args:
        session_id: 会话 ID
        generation_id: Generation ID（UUID）
        ide_type: IDE 类型枚举
    """
    try:
        state = {
            'session_id': session_id,
            'generation_id': generation_id,
            'started_at': datetime.now().isoformat()
        }

        state_file = _get_generation_state_file(ide_type)

        # 确保目录存在
        state_file.parent.mkdir(parents=True, exist_ok=True)

        with open(state_file, 'w', encoding='utf-8') as f:
            json.dump(state, f, ensure_ascii=False, indent=2)

        logger.debug(f'Generation 状态已保存: session={session_id}, generation={generation_id}, 文件: {state_file.name}')
    except Exception as e:
        logger.error(f'保存 generation 状态失败: {e}')


def _clear_generation_state(ide_type: IDEType):
    """
    清空 generation 状态文件

    Args:
        ide_type: IDE 类型枚举
    """
    try:
        state_file = _get_generation_state_file(ide_type)
        if state_file.exists():
            state_file.unlink()
            logger.debug(f'Generation 状态文件已清空: {state_file.name}')
    except Exception as e:
        logger.warning(f'清空 generation 状态文件失败: {e}')


# ============================================================================
# 公开 API
# ============================================================================

def start_generation(session_id: str, ide_type: Union[IDEType, str] = IDEType.CLAUDE_CODE) -> str:
    """
    开始新的 generation（生成并保存 generation_id）

    Args:
        session_id: 会话 ID
        ide_type: IDE 类型 (IDEType 枚举或字符串，默认 Claude Code)

    Returns:
        新生成的 generation_id（UUID 字符串）

    用途：
        - 在 UserPromptSubmit Hook 中调用
        - 为每次用户输入分配唯一的 generation_id
        - 后续所有操作（工具调用、文件变更、响应）都关联到该 generation_id

    示例：
        generation_id = start_generation("session-123", ide_type=IDEType.CLAUDE_CODE)
        # generation_id: "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
    """
    if not session_id:
        logger.warning('session_id 为空，无法创建 generation')
        return ''

    # 转换为枚举类型（如果是字符串）
    ide_type_enum = IDEType.from_string(ide_type) if isinstance(ide_type, str) else ide_type

    # 生成 UUID 作为 generation_id
    generation_id = str(uuid.uuid4())

    # 保存到状态文件（进程级）
    _write_generation_state(session_id, generation_id, ide_type_enum)

    logger.info(f'新 generation 已创建: session={session_id}, generation={generation_id} ({ide_type_enum.value})')

    return generation_id


def get_current_generation_id(session_id: str, ide_type: Union[IDEType, str] = IDEType.CLAUDE_CODE) -> Optional[str]:
    """
    获取当前 session 的活跃 generation_id

    Args:
        session_id: 会话 ID
        ide_type: IDE 类型 (IDEType 枚举或字符串，默认 Claude Code)

    Returns:
        当前的 generation_id，如果不存在返回 None

    用途：
        - 在 PreToolUse/PostToolUse 中获取当前 generation_id
        - 在 Stop Hook 中获取 generation_id 以更新 prompt
        - 关联文件变更到具体的 prompt

    示例：
        generation_id = get_current_generation_id("session-123", ide_type=IDEType.CLAUDE_CODE)
        if generation_id:
            # 使用 generation_id 关联数据
            ...
    """
    if not session_id:
        logger.debug('session_id 为空，无法获取 generation_id')
        return None

    # 转换为枚举类型（如果是字符串）
    ide_type_enum = IDEType.from_string(ide_type) if isinstance(ide_type, str) else ide_type

    state = _read_generation_state(ide_type_enum)

    # 验证 session_id 是否匹配
    if state and state.get('session_id') == session_id:
        generation_id = state.get('generation_id')
        logger.debug(f'获取到 generation_id: {generation_id} (session: {session_id}, ide: {ide_type_enum.value})')
        return generation_id

    logger.debug(f'未找到匹配的 generation_id (session: {session_id}, ide: {ide_type_enum.value})')
    return None


def end_generation(session_id: str, ide_type: Union[IDEType, str] = IDEType.CLAUDE_CODE):
    """
    结束当前 generation（清空状态）

    Args:
        session_id: 会话 ID
        ide_type: IDE 类型 (IDEType 枚举或字符串，默认 Claude Code)

    用途：
        - 在 Stop Hook 中调用
        - 标记当前 generation 已完成
        - 清理状态文件，为下一次 generation 做准备

    注意：
        - 只有当 session_id 匹配时才清空状态
        - 如果 session_id 不匹配，不会清空（避免误删其他会话的状态）

    示例：
        end_generation("session-123", ide_type=IDEType.CLAUDE_CODE)
    """
    if not session_id:
        logger.warning('session_id 为空，无法结束 generation')
        return

    # 转换为枚举类型（如果是字符串）
    ide_type_enum = IDEType.from_string(ide_type) if isinstance(ide_type, str) else ide_type

    state = _read_generation_state(ide_type_enum)

    # 验证 session_id 是否匹配
    if state and state.get('session_id') == session_id:
        generation_id = state.get('generation_id')
        _clear_generation_state(ide_type_enum)
        logger.info(f'Generation 已结束: session={session_id}, generation={generation_id} ({ide_type_enum.value})')
    else:
        logger.debug(f'session_id 不匹配或状态不存在，跳过清理 (session: {session_id}, ide: {ide_type_enum.value})')


def clear_generation(ide_type: Union[IDEType, str] = IDEType.CLAUDE_CODE):
    """
    清空 generation 状态（强制清理）

    Args:
        ide_type: IDE 类型 (IDEType 枚举或字符串，默认 Claude Code)

    用途：
        - 手动清理状态（测试或调试）
        - 重置 generation 追踪

    注意：
        - 不验证 session_id，直接清空
        - 慎用，可能影响正在进行的交互
    """
    # 转换为枚举类型（如果是字符串）
    ide_type_enum = IDEType.from_string(ide_type) if isinstance(ide_type, str) else ide_type

    _clear_generation_state(ide_type_enum)
    logger.info(f'Generation 状态已强制清空 ({ide_type_enum.value})')
