#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
会话启动时记录会话信息（SessionStart Hook）

功能：
1. 调用 session_manager.start_new_session() 强制开始新会话
   - SessionStart 语义：明确的"新会话开始"信号
   - 无论如何都会结束旧会话并创建新会话（即使 session_id 相同）
2. 异步执行，立即返回，不阻塞 Claude 启动

注意：
- 使用 start_new_session 而非 check_and_switch_session
- SessionStart = 强制新建，UserPromptSubmit = 智能判断
- 即使 SessionStart 未触发，UserPromptSubmit 也会创建 session（容错）
"""

import json
import logging
import sys
import os
from datetime import datetime
from pathlib import Path

# 导入公共工具（使用包导入）
from devlake_mcp.hooks.hook_utils import run_async
from devlake_mcp.session_manager import start_new_session
from devlake_mcp.logging_config import configure_logging
from devlake_mcp.constants import HOOK_LOG_DIR

# 配置日志（启动时调用一次）
configure_logging(log_dir=HOOK_LOG_DIR, log_file='session_start.log')
logger = logging.getLogger(__name__)


@run_async
def main():
    try:
        # 1. 从 stdin 读取 hook 输入
        input_data = json.load(sys.stdin)

        session_id = input_data.get('session_id')
        if not session_id:
            logger.warning('缺少 session_id，跳过')
            sys.exit(0)
            return  # 确保退出（测试时 sys.exit 被 mock）

        logger.debug(f'SessionStart Hook 触发 - session: {session_id}')

        # 2. 获取项目信息
        cwd = input_data.get('cwd', os.getcwd())

        # 3. 强制开始新会话（SessionStart 语义 = 新会话开始）
        try:
            start_new_session(
                session_id=session_id,
                cwd=cwd,
                ide_type='claude_code'
            )
            logger.info(f'SessionStart 完成 - session: {session_id}')
        except Exception as e:
            logger.error(f'会话管理失败: {e}')

        # 成功，静默退出
        sys.exit(0)

    except Exception as e:
        # 任何异常都静默失败，不阻塞 Claude
        logger.error(f'SessionStart Hook 执行失败: {e}', exc_info=True)
        sys.exit(0)


if __name__ == '__main__':
    main()
