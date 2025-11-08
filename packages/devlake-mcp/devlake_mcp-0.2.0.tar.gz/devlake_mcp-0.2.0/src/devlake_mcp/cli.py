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
    --help, -h      显示此帮助信息
    --version, -v   显示版本信息

示例:
    # Claude Code - 在项目根目录初始化 hooks 配置
    cd your-project
    devlake-mcp init

    # Cursor - 安装全局 hooks 配置
    devlake-mcp init-cursor

    # 强制覆盖已存在的配置
    devlake-mcp init --force
    devlake-mcp init-cursor --force

    # 显示版本
    devlake-mcp --version

更多信息请访问: https://github.com/engineering-efficiency/devlake-mcp
"""
    print(help_text)


def print_version():
    """打印版本信息"""
    from devlake_mcp import __version__
    print(f"DevLake MCP v{__version__}")


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


def main():
    """CLI 主入口"""
    # 解析命令行参数
    if len(sys.argv) < 2:
        print("❌ 错误：缺少命令参数")
        print_help()
        sys.exit(1)

    command = sys.argv[1]

    # 处理命令
    if command in ['--help', '-h', 'help']:
        print_help()
    elif command in ['--version', '-v', 'version']:
        print_version()
    elif command == 'init':
        # 检查是否有 --force 参数
        force = '--force' in sys.argv or '-f' in sys.argv
        init_command(force=force)
    elif command == 'init-cursor':
        # 检查是否有 --force 参数
        force = '--force' in sys.argv or '-f' in sys.argv
        init_cursor_command(force=force)
    else:
        print(f"❌ 错误：未知命令: {command}")
        print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()
