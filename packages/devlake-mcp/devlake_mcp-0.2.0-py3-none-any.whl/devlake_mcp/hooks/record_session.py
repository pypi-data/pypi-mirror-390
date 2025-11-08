#!/usr/bin/env python3
"""
记录 AI 编码会话信息（SessionEnd Hook）

触发时机：会话真正结束时（/clear、logout、退出程序等）
触发频率：每个会话只触发一次

功能：
1. 统计对话轮次（从 transcript）
2. 更新会话记录（PATCH /api/ai-coding/sessions/{session_id}）
3. 上传 transcript 完整内容（POST /api/ai-coding/transcripts）
4. API 后端自动计算会话时长

注意：
- 不要放在 Stop hook 中，那会在每次对话结束时触发（多次调用）
- SessionEnd 才是真正的会话结束，只触发一次
"""

import json
import sys
import os
from datetime import datetime
from pathlib import Path

# 导入公共工具（使用包导入）
from devlake_mcp.hooks.transcript_utils import count_user_messages, read_transcript_content
from devlake_mcp.hooks.hook_utils import log_error
from devlake_mcp.client import DevLakeClient


def main():
    try:
        # 1. 从 stdin 读取 hook 输入
        input_data = json.load(sys.stdin)

        hook_event_name = input_data.get('hook_event_name')
        if hook_event_name != 'SessionEnd':
            sys.exit(0)

        session_id = input_data.get('session_id')
        if not session_id:
            sys.exit(0)

        transcript_path = input_data.get('transcript_path', '')

        # 2. 统计对话轮次
        conversation_rounds = count_user_messages(transcript_path)

        # 3. 更新 session 记录（原有逻辑）
        update_data = {
            'session_id': session_id,
            'session_end_time': datetime.now().isoformat(),
            'conversation_rounds': conversation_rounds
        }

        try:
            client = DevLakeClient()
            client.update_session(session_id, update_data)
        except Exception as e:
            log_error('record_session_errors.log', f'Failed to update session {session_id}', e)

        # 4. 上传 transcript 内容（新增）
        if transcript_path and os.path.exists(transcript_path):
            try:
                # 读取 transcript 内容
                transcript_content = read_transcript_content(transcript_path)
                transcript_size = os.path.getsize(transcript_path)

                transcript_data = {
                    'session_id': session_id,
                    'transcript_path': transcript_path,
                    'transcript_content': transcript_content,
                    'transcript_size': transcript_size,
                    'message_count': conversation_rounds,
                    'upload_time': datetime.now().isoformat()
                }

                # POST /api/ai-coding/transcripts
                client = DevLakeClient()
                client.create_transcript(transcript_data)
            except Exception as e:
                log_error('transcript_upload_errors.log', f'Failed to upload transcript for {session_id}', e)

        # 成功，静默退出
        sys.exit(0)

    except Exception as e:
        # 任何异常都静默失败，不阻塞 Claude
        try:
            log_error('record_session_errors.log', 'SessionEnd hook failed', e)
        except:
            pass
        sys.exit(0)


if __name__ == '__main__':
    main()
