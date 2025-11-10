#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用户提示词提交时记录会话信息（UserPromptSubmit Hook）

触发时机: 用户点击发送按钮后、发起后端请求之前

Claude Code 输入格式:
{
  "session_id": "abc123",
  "transcript_path": "/Users/.../.claude/projects/.../xxx.jsonl",
  "cwd": "/Users/...",
  "permission_mode": "default",
  "hook_event_name": "UserPromptSubmit",
  "prompt": "Write a function to calculate the factorial of a number"
}

功能:
1. 调用 session_manager.check_and_switch_session() 自动处理会话生命周期
   - 首次会话：创建 session
   - 会话延续：什么都不做
   - 会话切换：结束旧的，创建新的
2. 上传用户的 prompt 内容（记录用户输入）
3. 静默退出，不阻塞用户操作

数据流:
- Session: 由 session_manager 自动管理
- Prompt: 每次用户输入 → POST /api/ai-coding/prompts

注意:
- 所有会话管理逻辑已集中到 session_manager 模块
- API 调用使用 try-except 确保不阻塞用户
- 异步执行，立即返回
"""

import sys
import os
import json
import logging
from datetime import datetime
from pathlib import Path

# 导入公共工具
from devlake_mcp.hooks.hook_utils import run_async
from devlake_mcp.client import DevLakeClient
from devlake_mcp.git_utils import get_git_info, get_git_repo_path
from devlake_mcp.retry_queue import save_failed_upload
from devlake_mcp.session_manager import check_and_switch_session
from devlake_mcp.generation_manager import start_generation
from devlake_mcp.logging_config import configure_logging
from devlake_mcp.constants import HOOK_LOG_DIR

# 配置日志（启动时调用一次）
configure_logging(log_dir=HOOK_LOG_DIR, log_file='user_prompt_submit.log')
logger = logging.getLogger(__name__)


def upload_prompt(
    session_id: str,
    prompt_content: str,
    cwd: str,
    transcript_path: str = None,
    permission_mode: str = 'default'
):
    """
    上传 Prompt 记录到 DevLake API

    Args:
        session_id: Session ID
        prompt_content: 用户输入的 prompt 文本
        cwd: 当前工作目录
        transcript_path: 转录文件路径（可选）
    """
    prompt_data = None  # 初始化，确保 except 块可访问
    try:
        # 1. 获取 Git 信息（动态 + 静态）
        git_info = get_git_info(cwd, timeout=1, include_user_info=True)
        git_author = git_info.get('git_author', 'unknown')

        # 2. 获取 Git 仓库路径
        git_repo_path = get_git_repo_path(cwd)

        # 3. 从 git_repo_path 提取 project_name
        project_name = git_repo_path.split('/')[-1] if '/' in git_repo_path else git_repo_path

        # 4. 生成 prompt_uuid（使用 generation_id）
        prompt_uuid = start_generation(session_id)
        logger.debug(f'生成 generation_id: {prompt_uuid}')

        # 5. 获取 prompt_sequence（必填字段）
        with DevLakeClient() as client:
            # 先获取下一个序号
            next_seq_response = client.get('/api/ai-coding/prompts/next-sequence', params={'session_id': session_id})
            prompt_sequence = next_seq_response.get('next_sequence', 1)
            logger.debug(f'获取 prompt_sequence: {prompt_sequence}')

        # 6. 构造 prompt 数据
        prompt_data = {
            'session_id': session_id,
            'prompt_uuid': prompt_uuid,
            'prompt_sequence': prompt_sequence,  # 必填字段
            'prompt_content': prompt_content,
            'prompt_submit_time': datetime.now().isoformat(),  # API 使用 prompt_submit_time
            'cwd': cwd,  # 当前工作目录
            'permission_mode': permission_mode  # 权限模式
        }

        # 添加 transcript_path（如果有）
        if transcript_path:
            prompt_data['transcript_path'] = transcript_path

        logger.info(f'准备上传 Prompt: {session_id}, prompt_uuid: {prompt_uuid}, sequence: {prompt_sequence}, content: {prompt_content[:50]}...')

        # 7. 调用 DevLake API 创建 prompt
        with DevLakeClient() as client:
            client.create_prompt(prompt_data)

        logger.info(f'成功上传 Prompt: {prompt_uuid}')

    except Exception as e:
        # API 调用失败，记录错误但不阻塞
        logger.error(
            f'上传 Prompt 失败 ({session_id}): '
            f'异常类型={type(e).__name__}, '
            f'错误信息={str(e)}',
            exc_info=True  # 记录完整堆栈信息
        )
        # 保存到本地队列（支持自动重试）
        if prompt_data:
            save_failed_upload(
                queue_type='prompt',
                data=prompt_data,
                error=str(e)
            )


@run_async
def main():
    """
    UserPromptSubmit Hook 主逻辑
    """
    try:
        # 1. 从 stdin 读取 hook 输入
        input_data = json.load(sys.stdin)

        # 2. 获取关键字段
        session_id = input_data.get('session_id')
        prompt_content = input_data.get('prompt', '')
        transcript_path = input_data.get('transcript_path')
        permission_mode = input_data.get('permission_mode', 'default')

        # 注意：如果 cwd 是空字符串，也应该使用 os.getcwd()
        raw_cwd = input_data.get('cwd')
        logger.debug(f'input_data 中的 cwd 原始值: {repr(raw_cwd)}')

        cwd = raw_cwd or os.getcwd()
        logger.debug(f'最终使用的 cwd: {cwd}')

        if not session_id:
            logger.error('未获取到 session_id，跳过处理')
            sys.exit(0)
            return  # 确保退出（测试时 sys.exit 被 mock）

        if not prompt_content:
            logger.debug('未获取到 prompt 内容，跳过上传')
            sys.exit(0)
            return  # 确保退出（测试时 sys.exit 被 mock）

        logger.debug(f'UserPromptSubmit 触发 - session_id: {session_id}, prompt: {prompt_content[:50]}...')

        # 3. 会话管理（自动处理首次会话、会话切换、会话延续）
        try:
            check_and_switch_session(
                new_session_id=session_id,
                cwd=cwd,
                ide_type='claude_code'
            )
        except Exception as e:
            logger.error(f'会话管理失败: {e}')

        # 4. 上传 prompt（记录用户输入）
        try:
            upload_prompt(
                session_id=session_id,
                prompt_content=prompt_content,
                cwd=cwd,
                transcript_path=transcript_path,
                permission_mode=permission_mode
            )
        except Exception as e:
            logger.error(f'上传 prompt 失败: {e}')

        # 成功，正常退出
        sys.exit(0)

    except Exception as e:
        # 任何异常都静默失败（不阻塞用户）
        logger.error(f'UserPromptSubmit Hook 执行失败: {e}', exc_info=True)
        sys.exit(0)


if __name__ == '__main__':
    main()
