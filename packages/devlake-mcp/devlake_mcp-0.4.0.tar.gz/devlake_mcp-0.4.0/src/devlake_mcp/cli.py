#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DevLake MCP CLI 工具

提供命令行工具，用于初始化项目的 Claude Code 和 Cursor hooks 配置。

命令:
    devlake-mcp init         - 初始化 .claude/settings.json 配置（Claude Code）
    devlake-mcp init-cursor  - 初始化 ~/.cursor/hooks.json 配置（Cursor IDE）
    devlake-mcp --help       - 显示帮助信息
"""

import sys
import json
import subprocess
import shutil
from pathlib import Path


def print_help():
    """打印帮助信息"""
    help_text = """
DevLake MCP - AI 编程数据采集工具

用法:
    devlake-mcp <command> [options]

命令:
    init            初始化 Claude Code hooks 配置（.claude/settings.json）
    init-cursor     初始化 Cursor hooks 配置（~/.cursor/hooks.json）
    retry           手动触发重试失败的上传记录
    queue-status    查看失败队列状态和统计信息
    queue-clean     清理过期的失败记录
    info            显示详细的版本和功能支持信息
    --help, -h      显示此帮助信息
    --version, -v   显示版本号

示例:
    # Claude Code - 在项目根目录初始化 hooks 配置
    cd your-project
    devlake-mcp init

    # Cursor - 安装全局 hooks 配置
    devlake-mcp init-cursor

    # 强制覆盖已存在的配置
    devlake-mcp init --force
    devlake-mcp init-cursor --force

    # 手动重试失败的上传
    devlake-mcp retry

    # 查看失败队列状态
    devlake-mcp queue-status

    # 清理过期记录
    devlake-mcp queue-clean

    # 显示版本
    devlake-mcp --version

更多信息请访问: https://github.com/engineering-efficiency/devlake-mcp
"""
    print(help_text)


def print_version():
    """打印简洁的版本号（标准格式）"""
    from devlake_mcp import __version__
    print(f"devlake-mcp {__version__}")


def print_info():
    """打印详细的版本和功能支持信息"""
    from devlake_mcp import __version__
    from devlake_mcp.compat import get_version_info

    info = get_version_info()

    print("=" * 60)
    print("DevLake MCP - 版本信息")
    print("=" * 60)
    print(f"DevLake MCP: v{__version__}")
    print(f"Python: {info['python_version']}")

    # 显示功能状态
    print("\n功能支持:")
    print(f"  - Hooks 模式: {'✓' if info['features']['hooks'] else '✗'}")

    if info['mcp_available']:
        print(f"  - MCP Server: ✓ (FastMCP {info['fastmcp_version']})")
    elif info['mcp_supported']:
        print(f"  - MCP Server: ✗ (未安装 fastmcp)")
    else:
        print(f"  - MCP Server: ✗ (需要 Python 3.10+)")

    # 显示建议
    if info['recommended_action'] != "✓ 所有功能可用":
        print(f"\n建议: {info['recommended_action']}")

    print("=" * 60)


def get_settings_template() -> dict:
    """
    获取 settings.json 模板

    Returns:
        dict: settings.json 配置字典
    """
    return {
        "hooks": {
            "Stop": [
                {
                    "hooks": [
                        {
                            "type": "command",
                            "command": "python3 -m devlake_mcp.hooks.stop",
                            "timeout": 5
                        }
                    ]
                }
            ],
            "SubagentStop": [
                {
                    "hooks": [
                        {
                            "type": "command",
                            "command": "python3 -m devlake_mcp.hooks.stop",
                            "timeout": 5
                        }
                    ]
                }
            ],
            "UserPromptSubmit": [
                {
                    "hooks": [
                        {
                            "type": "command",
                            "command": "python3 -m devlake_mcp.hooks.user_prompt_submit",
                            "timeout": 5
                        }
                    ]
                }
            ],
            "PreToolUse": [
                {
                    "matcher": "Write|Edit|NotebookEdit",
                    "hooks": [
                        {
                            "type": "command",
                            "command": "python3 -m devlake_mcp.hooks.pre_tool_use",
                            "timeout": 5
                        }
                    ]
                }
            ],
            "PostToolUse": [
                {
                    "matcher": "Write|Edit|NotebookEdit",
                    "hooks": [
                        {
                            "type": "command",
                            "command": "python3 -m devlake_mcp.hooks.post_tool_use",
                            "timeout": 5
                        }
                    ]
                }
            ],
            "SessionStart": [
                {
                    "hooks": [
                        {
                            "type": "command",
                            "command": "python3 -m devlake_mcp.hooks.session_start",
                            "timeout": 5
                        }
                    ]
                }
            ],
            "SessionEnd": [
                {
                    "hooks": [
                        {
                            "type": "command",
                            "command": "python3 -m devlake_mcp.hooks.record_session",
                            "timeout": 5
                        }
                    ]
                }
            ]
        }
    }


def create_settings_file(force: bool = False) -> bool:
    """
    创建 .claude/settings.json 配置文件

    Args:
        force: 是否强制覆盖已存在的文件

    Returns:
        bool: 是否成功创建
    """
    claude_dir = Path.cwd() / ".claude"
    settings_file = claude_dir / "settings.json"

    # 检查文件是否已存在
    if settings_file.exists() and not force:
        print(f"⚠️  配置文件已存在: {settings_file}")
        response = input("是否覆盖？ [y/N]: ")
        if response.lower() not in ['y', 'yes']:
            print("❌ 已取消")
            return False
        print()

    # 创建 .claude 目录
    claude_dir.mkdir(parents=True, exist_ok=True)

    # 获取模板并写入文件
    settings = get_settings_template()

    with open(settings_file, 'w', encoding='utf-8') as f:
        json.dump(settings, f, indent=2, ensure_ascii=False)

    print(f"✅ 创建配置文件: {settings_file}")
    return True


def init_command(force: bool = False):
    """
    初始化项目的 Claude Code hooks 配置

    Args:
        force: 是否强制覆盖已存在的文件
    """
    print("\n🚀 开始初始化 DevLake MCP hooks 配置...\n")

    # 1. 检查是否在 Git 仓库中（可选）
    if not Path(".git").exists():
        print("⚠️  警告：当前目录不是 Git 仓库，建议在项目根目录执行此命令。")
        response = input("是否继续？ [y/N]: ")
        if response.lower() not in ['y', 'yes']:
            print("❌ 已取消")
            sys.exit(0)
        print()

    # 2. 创建 settings.json 文件
    success = create_settings_file(force)

    if not success:
        sys.exit(0)

    # 3. 显示完成信息
    print(f"\n✨ 初始化完成！")

    # 4. 显示下一步提示
    print("\n📝 下一步：")
    print("   1. 配置 Git 用户信息（如果未配置）：")
    print("      git config user.email 'your-email@example.com'")
    print("      git config user.name 'Your Name'")
    print()
    print("   2. 配置 Git 远程仓库（如果未配置）：")
    print("      git remote add origin <repository-url>")
    print()
    print("   3. 安装 devlake-mcp 包（如果未安装）：")
    print("      pip install devlake-mcp")
    print()
    print("   4. 配置 DevLake API 地址（可选）：")
    print("      export DEVLAKE_BASE_URL='http://your-devlake-api.com'")
    print()
    print("   5. 开始使用 Claude Code，hooks 会自动工作！")
    print()


def get_cursor_hooks_template() -> dict:
    """
    获取 Cursor hooks.json 模板

    Returns:
        dict: hooks.json 配置字典
    """
    return {
        "beforeSubmitPrompt": [
            {
                "command": "python3 -m devlake_mcp.hooks.cursor.before_submit_prompt"
            }
        ],
        "afterAgentResponse": [
            {
                "command": "python3 -m devlake_mcp.hooks.cursor.after_agent_response"
            }
        ],
        "beforeReadFile": [
            {
                "command": "python3 -m devlake_mcp.hooks.cursor.before_read_file"
            }
        ],
        "beforeShellExecution": [
            {
                "command": "python3 -m devlake_mcp.hooks.cursor.before_shell_execution"
            }
        ],
        "afterShellExecution": [
            {
                "command": "python3 -m devlake_mcp.hooks.cursor.after_shell_execution"
            }
        ],
        "afterFileEdit": [
            {
                "command": "python3 -m devlake_mcp.hooks.cursor.after_file_edit"
            }
        ],
        "stop": [
            {
                "command": "python3 -m devlake_mcp.hooks.cursor.stop_hook"
            }
        ]
    }


def check_python3():
    """检查 Python 3 是否可用"""
    if not shutil.which('python3'):
        print("❌ 错误：未找到 python3，请先安装 Python 3")
        sys.exit(1)
    print("✅ Python 3 已安装")


def check_devlake_mcp_installed():
    """检查 devlake-mcp 模块是否已安装"""
    try:
        import devlake_mcp
        print("✅ devlake-mcp 模块已安装")
        return True
    except ImportError:
        print("❌ 错误：devlake-mcp 模块未安装")
        print()
        print("请先安装 devlake-mcp：")
        print("  pipx install devlake-mcp")
        print("  或")
        print("  pip install -e .")
        sys.exit(1)


def check_git_config():
    """检查 Git 配置"""
    try:
        result = subprocess.run(['git', 'config', 'user.name'], capture_output=True, text=True)
        git_user = result.stdout.strip()

        result = subprocess.run(['git', 'config', 'user.email'], capture_output=True, text=True)
        git_email = result.stdout.strip()

        if not git_user or not git_email:
            print()
            print("⚠️  警告：Git 用户信息未配置")
            print("请配置 Git 用户信息：")
            print("  git config --global user.name \"Your Name\"")
            print("  git config --global user.email \"your.email@example.com\"")
            return False

        print(f"✅ Git 配置已设置 ({git_user} <{git_email}>)")
        return True
    except FileNotFoundError:
        print("⚠️  警告：未找到 git 命令")
        return False


def create_cursor_hooks_file(force: bool = False) -> bool:
    """
    创建 ~/.cursor/hooks.json 配置文件

    Args:
        force: 是否强制覆盖已存在的文件

    Returns:
        bool: 是否成功创建
    """
    cursor_dir = Path.home() / ".cursor"
    hooks_file = cursor_dir / "hooks.json"

    # 检查文件是否已存在
    if hooks_file.exists() and not force:
        print(f"⚠️  配置文件已存在: {hooks_file}")

        # 备份现有文件
        backup_file = cursor_dir / "hooks.json.backup"
        shutil.copy2(hooks_file, backup_file)
        print(f"✅ 已备份现有配置: {backup_file}")

        response = input("是否覆盖？ [y/N]: ")
        if response.lower() not in ['y', 'yes']:
            print("❌ 已取消")
            return False
        print()

    # 创建 .cursor 目录
    cursor_dir.mkdir(parents=True, exist_ok=True)

    # 获取模板并写入文件
    hooks = get_cursor_hooks_template()

    with open(hooks_file, 'w', encoding='utf-8') as f:
        json.dump(hooks, f, indent=2, ensure_ascii=False)

    print(f"✅ 创建配置文件: {hooks_file}")
    return True


def init_cursor_command(force: bool = False):
    """
    初始化 Cursor hooks 配置

    Args:
        force: 是否强制覆盖已存在的文件
    """
    print("\n🚀 开始初始化 Cursor hooks 配置...\n")
    print("=" * 60)

    # 1. 检查 Python 3
    check_python3()

    # 2. 检查 devlake-mcp 模块
    check_devlake_mcp_installed()

    # 3. 检查 Git 配置（警告但不阻止）
    check_git_config()

    print("=" * 60)
    print()

    # 4. 创建 hooks.json 文件
    success = create_cursor_hooks_file(force)

    if not success:
        sys.exit(0)

    # 5. 显示完成信息
    print("\n✨ Cursor hooks 初始化完成！")

    # 6. 显示下一步提示
    print("\n📝 下一步：")
    print("   1. 重启 Cursor IDE")
    print("   2. 在 Cursor 设置中查看 Hooks 选项卡，确认 hooks 已激活")
    print("   3. 配置 DevLake API 地址（在项目根目录创建 .env 文件）：")
    print("      echo 'DEVLAKE_BASE_URL=http://your-devlake-api.com' > .env")
    print()
    print("   4. 开始使用 Cursor Agent，hooks 会自动采集数据！")
    print()
    print("📚 详细文档：")
    print("   - 使用指南：CURSOR_HOOKS.md")
    print("   - 故障排查：查看 .cursor/logs/cursor_*.log")
    print()


def retry_command():
    """手动触发重试失败的上传记录"""
    from devlake_mcp.retry_queue import retry_failed_uploads, get_retry_config

    print("\n🔄 开始重试失败的上传记录...\n")

    config = get_retry_config()
    if not config['enabled']:
        print("⚠️  重试功能已禁用（DEVLAKE_RETRY_ENABLED=false）")
        print("   如需启用，请设置环境变量：")
        print("   export DEVLAKE_RETRY_ENABLED=true")
        return

    print(f"配置：")
    print(f"  - 最大重试次数：{config['max_attempts']}")
    print(f"  - 记录保留天数：{config['cleanup_days']}")
    print()

    # 执行重试（不限制数量）
    stats = retry_failed_uploads(max_parallel=999)

    # 显示结果
    print("\n📊 重试统计：")
    print(f"  - 检查记录数：{stats['checked']}")
    print(f"  - 尝试重试数：{stats['retried']}")
    print(f"  - 重试成功数：{stats['succeeded']} ✅")
    print(f"  - 重试失败数：{stats['failed']} ❌")
    print(f"  - 跳过记录数：{stats['skipped']} ⏭️")
    print()

    if stats['succeeded'] > 0:
        print(f"✨ 成功重试 {stats['succeeded']} 条记录！")
    elif stats['retried'] == 0:
        print("💡 没有需要重试的记录")
    else:
        print("⚠️  部分记录重试失败，将在下次自动重试")


def queue_status_command():
    """查看失败队列状态和统计信息"""
    from devlake_mcp.retry_queue import get_queue_statistics, get_retry_config

    print("\n📊 失败队列状态\n")

    config = get_retry_config()
    stats = get_queue_statistics()

    # 显示配置
    print("⚙️  重试配置：")
    print(f"  - 启用状态：{'✅ 已启用' if config['enabled'] else '❌ 已禁用'}")
    print(f"  - 最大重试次数：{config['max_attempts']}")
    print(f"  - 记录保留天数：{config['cleanup_days']}")
    print(f"  - Hook 触发检查：{'✅ 已启用' if config['check_on_hook'] else '❌ 已禁用'}")
    print()

    # 显示总体统计
    summary = stats['summary']
    print("📈 总体统计：")
    print(f"  - 总记录数：{summary['total']}")
    print(f"  - 待重试数：{summary['pending']}")
    print(f"  - 已达最大重试次数：{summary['max_retried']}")
    print()

    # 显示各队列详情
    if summary['total'] > 0:
        print("📋 队列详情：")
        for queue_type in ['session', 'prompt', 'file_change']:
            queue_stats = stats[queue_type]
            if queue_stats['total'] > 0:
                queue_name = {
                    'session': 'Session 会话',
                    'prompt': 'Prompt 提示',
                    'file_change': '文件变更'
                }[queue_type]
                print(f"  - {queue_name}：总数 {queue_stats['total']}, "
                      f"待重试 {queue_stats['pending']}, "
                      f"已达上限 {queue_stats['max_retried']}")
        print()

    if summary['total'] == 0:
        print("✨ 队列为空，没有失败记录！")
    elif summary['pending'] > 0:
        print(f"💡 提示：有 {summary['pending']} 条记录待重试")
        print("   可运行 'devlake-mcp retry' 手动触发重试")


def queue_clean_command():
    """清理过期的失败记录"""
    from devlake_mcp.retry_queue import cleanup_expired_failures, get_retry_config

    print("\n🧹 清理过期的失败记录...\n")

    config = get_retry_config()
    max_age_hours = config['cleanup_days'] * 24

    print(f"清理条件：")
    print(f"  - 超过 {config['cleanup_days']} 天的记录")
    print(f"  - 已达最大重试次数 ({config['max_attempts']}) 的记录")
    print()

    # 执行清理
    cleaned_count = cleanup_expired_failures(max_age_hours=max_age_hours)

    # 显示结果
    if cleaned_count > 0:
        print(f"✅ 已清理 {cleaned_count} 条过期记录")
    else:
        print("💡 没有需要清理的记录")


def main():
    """CLI 主入口

    无参数运行时启动 MCP 服务器，有参数时执行 CLI 命令。
    """
    # 无参数时启动 MCP 服务器（用于 Claude Desktop 集成）
    if len(sys.argv) < 2:
        from devlake_mcp.server import main as server_main
        server_main()
        return

    command = sys.argv[1]

    # 处理命令
    if command in ['--help', '-h', 'help']:
        print_help()
    elif command in ['--version', '-v', 'version']:
        print_version()
    elif command == 'info':
        print_info()
    elif command == 'init':
        # 检查是否有 --force 参数
        force = '--force' in sys.argv or '-f' in sys.argv
        init_command(force=force)
    elif command == 'init-cursor':
        # 检查是否有 --force 参数
        force = '--force' in sys.argv or '-f' in sys.argv
        init_cursor_command(force=force)
    elif command == 'retry':
        retry_command()
    elif command == 'queue-status':
        queue_status_command()
    elif command == 'queue-clean':
        queue_clean_command()
    else:
        print(f"❌ 错误：未知命令: {command}")
        print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()
