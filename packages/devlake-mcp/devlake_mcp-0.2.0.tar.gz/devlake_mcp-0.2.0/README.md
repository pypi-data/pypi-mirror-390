# DevLake MCP Server

一个基于 [FastMCP](https://gofastmcp.com) 框架的 DevLake MCP 服务器，允许 AI 助手（如 Claude）与 DevLake 进行交互。


## 安装

### 方式 1: 使用 pipx（推荐）

pipx 会在隔离环境中安装 Python 应用程序：

```bash
# 安装 pipx（如果还没有安装）
# macOS
brew install pipx

# Linux
python3 -m pip install --user pipx
python3 -m pipx ensurepath

# 使用 pipx 安装 devlake-mcp
pipx install devlake-mcp
```

### 方式 2: 从源码安装

```bash
# 克隆仓库
git clone https://github.com/yourusername/devlake-mcp.git
cd devlake-mcp

# 使用 pip 安装（开发模式）
pip install -e .

# 或使用 uv（推荐用于开发）
uv pip install -e .
```


## 使用方法

### 作为命令行工具运行

安装后，可以直接运行服务器：

```bash
devlake-mcp
```

### 与 Claude Desktop 集成
claude mcp add devlake-mcp devlake-mcp
```

### Cursor Hooks 支持

DevLake MCP 现在支持 Cursor IDE！通过 Cursor hooks，可以自动采集 AI 编程数据，与 Claude Code 完全兼容。

**快速安装**：

```bash
# 使用 CLI 命令安装（推荐）
devlake-mcp init-cursor

# 强制覆盖已有配置
devlake-mcp init-cursor --force
```

**功能特性**：
- ✅ 自动 session 管理（30 分钟不活动自动新建 session）
- ✅ 文件变更记录（before/after diff）
- ✅ Shell 命令支持（vim/nano/echo> 等）
- ✅ 与 Claude Code 数据格式完全兼容

**详细文档**：查看 [CURSOR_HOOKS.md](CURSOR_HOOKS.md) 了解完整配置和使用指南。


## 环境变量配置

在使用前，需要配置 DevLake API 连接信息。

### 方式 1: 使用 .env 文件（推荐）

```bash
# 复制示例配置文件
cp .env.example .env

# 编辑配置文件，填写实际值
vim .env
```

`.env` 文件内容：
```bash
# DevLake API 地址（必需）
DEVLAKE_BASE_URL=http://devlake.test.chinawayltd.com

# API 超时时间（秒，默认 30）
DEVLAKE_TIMEOUT=30

# API 认证 Token（可选）
# DEVLAKE_API_TOKEN=your-token-here
```

### 方式 2: 直接设置环境变量

```bash
export DEVLAKE_BASE_URL="http://devlake.test.chinawayltd.com"
export DEVLAKE_TIMEOUT=30
```

### Git 配置（必需）

工具会自动从 Git 配置读取用户信息，请确保已配置：

```bash
# 配置 Git 用户信息
git config user.name "Your Name"
git config user.email "your.email@example.com"

# 配置仓库远程地址
git remote add origin <repository-url>
```


## 可用工具

当前服务器提供 3 个核心工具，用于记录 AI 编程会话和文件变更：

### `record_session`
记录 AI 会话的元数据和统计信息。

**参数**：
- `session_id` (string, 可选): 会话 ID，不提供则自动生成 UUID
- `metadata` (dict, 可选): 会话元数据，支持字段：
  - `user_intent`: 用户意图描述
  - `model`: 模型名称（如 "claude-sonnet-4-5"）
  - `ide`: IDE 类型（如 "cursor", "claude-code"）
  - `project_path`: 项目路径

**返回**：
```json
{
  "success": true,
  "session_id": "uuid-xxx",
  "timestamp": "2025-01-07T10:00:00Z",
  "git_info": {
    "git_repo_path": "yourorg/devlake",
    "git_branch": "main",
    "git_author": "Your Name"
  }
}
```

**示例**：
```
调用 record_session 工具，metadata 设置为 {"ide": "cursor", "model": "claude-sonnet-4-5"}
```

---

### `before_edit_file`
在文件变更前调用，记录文件的当前状态。

**参数**：
- `session_id` (string, 必需): 会话唯一标识
- `file_paths` (list[string], 必需): 即将变更的文件绝对路径列表

**返回**：
```json
{
  "success": true,
  "session_id": "session-123",
  "files_snapshot": {
    "/path/to/file.py": {
      "exists": true,
      "line_count": 100,
      "size": 2048
    }
  }
}
```

**示例**：
```
调用 before_edit_file 工具，session_id 为 "session-123"，file_paths 为 ["/path/to/file.py"]
```

---

### `after_edit_file`
在文件变更后调用，上传变更数据到 DevLake API。

**参数**：
- `session_id` (string, 必需): 会话唯一标识（与 before_edit_file 一致）
- `file_paths` (list[string], 必需): 已变更的文件绝对路径列表

**返回**：
```json
{
  "success": true,
  "session_id": "session-123",
  "uploaded_count": 1,
  "changes": [
    {
      "file_path": "src/main.py",
      "change_type": "edit",
      "file_type": "py"
    }
  ]
}
```

**工作流程**：
```
1. before_edit_file() - 记录文件变更前状态
2. [执行文件变更操作]
3. after_edit_file() - 对比差异并上传
```

**示例**：
```
调用 after_edit_file 工具，session_id 为 "session-123"，file_paths 为 ["/path/to/file.py"]
```

## 相关资源

- [Model Context Protocol 官方文档](https://modelcontextprotocol.io)
- [FastMCP 官方文档](https://gofastmcp.com)
- [FastMCP GitHub](https://github.com/jlowin/fastmcp)
- [Claude Desktop](https://claude.ai/download)
- [Cursor 编辑器](https://cursor.sh)
