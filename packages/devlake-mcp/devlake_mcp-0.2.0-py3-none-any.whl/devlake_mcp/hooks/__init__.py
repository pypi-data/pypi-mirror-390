#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DevLake MCP - Claude Code Hooks 模块

提供完整的 Claude Code hooks 功能，用于收集 AI 编码数据并上报到 DevLake。

使用方法：
    from devlake_mcp.hooks import session_start
    session_start.main()

所有可用的 hooks:
    - session_start: 会话启动时触发
    - pre_tool_use: 工具执行前触发
    - post_tool_use: 工具执行后触发
    - stop: Claude 完成回复时触发
    - record_session: 会话结束时触发
"""

# 自动初始化 Git 环境变量（hooks 模块导入时执行）
from devlake_mcp.config import DevLakeConfig
DevLakeConfig.from_env(include_git=True)

# 导入所有 hook 模块
from devlake_mcp.hooks import (
    hook_utils,
    session_start,
    pre_tool_use,
    post_tool_use,
    stop,
    record_session,
)

__all__ = [
    # 工具模块
    "hook_utils",
    # Hook 模块
    "session_start",
    "pre_tool_use",
    "post_tool_use",
    "stop",
    "record_session",
]

__version__ = "0.1.0"
