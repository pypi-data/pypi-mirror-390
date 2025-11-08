#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
会话启动时记录会话信息（SessionStart Hook）

功能：
1. 获取会话基本信息（session_id, user_id, project）
2. 获取 Git 信息（branch, commit, author）
3. 直接上传到 API（POST /api/ai-coding/sessions）
4. 失败时记录错误日志（不阻塞）
5. 异步执行，立即返回，不阻塞 Claude 启动
"""

import json
import sys
import os
from datetime import datetime
from pathlib import Path

# 导入公共工具（使用包导入）
from devlake_mcp.git_utils import get_git_info
from devlake_mcp.hooks.hook_utils import setup_logger, run_async, save_to_local_queue
from devlake_mcp.client import DevLakeClient

# 配置日志
logger = setup_logger(__name__, 'session_start.log')


@run_async
def main():
    try:
        # 1. 从 stdin 读取 hook 输入
        input_data = json.load(sys.stdin)

        session_id = input_data.get('session_id')
        if not session_id:
            logger.warning('缺少 session_id，跳过')
            sys.exit(0)

        logger.debug(f'SessionStart Hook 触发 - session: {session_id}')

        # 2. 获取项目信息
        cwd = input_data.get('cwd', os.getcwd())

        # 3. 获取用户信息
        user_name = os.getenv('USER', 'unknown')

        # 4. 获取动态 Git 信息（branch 和 commit，不获取用户信息）
        git_info = get_git_info(cwd, timeout=1, include_user_info=False)
        git_branch = git_info.get('git_branch', 'unknown')
        git_commit = git_info.get('git_commit', 'unknown')

        # 5. 从环境变量读取静态信息
        git_repo_path = os.getenv('GIT_REPO_PATH', 'unknown')
        git_email = os.getenv('GIT_EMAIL', 'unknown')
        git_author = os.getenv('GIT_AUTHOR', 'unknown')

        # 6. 从 git_repo_path 提取 project_name（取最后的部分）
        # 例如：yourorg/devlake -> devlake, team/subteam/project -> project
        project_name = git_repo_path.split('/')[-1] if '/' in git_repo_path else git_repo_path

        logger.info(f'准备创建 Session: {session_id}, git_repo_path: {git_repo_path}, '
                   f'project_name: {project_name}, branch: {git_branch}, commit: {git_commit[:8]}')

        # 7. 构造会话数据
        session_data = {
            'session_id': session_id,
            'user_name': user_name,
            'ide_type': 'claude_code',
            'model_name': os.getenv('CLAUDE_MODEL', 'claude-sonnet-4-5'),
            'git_repo_path': git_repo_path,        # ✅ Git仓库路径 (namespace/name)
            'project_name': project_name,          # ✅ 从 git_repo_path 提取
            'session_start_time': datetime.now().isoformat(),
            'conversation_rounds': 0,
            'is_adopted': 0,
            'git_branch': git_branch,              # Git 分支（动态）
            'git_commit': git_commit,              # Git commit（动态）
            'git_author': git_author,              # Git 作者（环境变量）
            'git_email': git_email                 # Git 邮箱（环境变量）
        }

        # 8. 上传到 API
        try:
            client = DevLakeClient()
            client.create_session(session_data)
            logger.info(f'成功创建 Session: {session_id}')
        except Exception as e:
            # 上传失败，记录错误日志并保存到本地队列
            logger.error(f'创建 Session 失败 ({session_id}): {e}')
            save_to_local_queue('failed_session_uploads', session_data)

        # 成功，静默退出
        sys.exit(0)

    except Exception as e:
        # 任何异常都静默失败，不阻塞 Claude
        logger.error(f'SessionStart Hook 执行失败: {e}', exc_info=True)
        sys.exit(0)


if __name__ == '__main__':
    main()
