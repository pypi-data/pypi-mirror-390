# DevLake MCP Server

一个基于 [FastMCP](https://gofastmcp.com) 框架的 DevLake MCP 服务器，允许 AI 助手（如 Claude）与 DevLake 进行交互。

## 功能特性

- 🚀 基于强大的 FastMCP 框架（第三方）
- 📦 支持通过 pipx 安装
- 🔧 可扩展的工具系统
- 💻 与 Claude Desktop、Cursor 等 MCP 客户端兼容
- 🔐 支持认证和中间件（FastMCP 高级功能）
- 🌐 支持多种传输协议（STDIO、HTTP、SSE）

## 为什么选择 FastMCP？

我们使用 [jlowin/fastmcp](https://github.com/jlowin/fastmcp) 而不是官方 MCP SDK：

- ✅ 更简洁优雅的 API 设计
- ✅ 生产环境就绪
- ✅ 内置认证和授权支持
- ✅ 强大的中间件系统
- ✅ 支持 HTTP/SSE 传输
- ✅ 可集成 OpenAPI 和 FastAPI
- ✅ 活跃的社区维护

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

### 方式 3: 本地开发

```bash
# 安装 uv（如果还没有安装）
curl -LsSf https://astral.sh/uv/install.sh | sh

# 创建虚拟环境并安装依赖
uv venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
uv pip install -e ".[dev]"
```

## 使用方法

### 作为命令行工具运行

安装后，可以直接运行服务器：

```bash
devlake-mcp
```

### 与 Claude Desktop 集成

1. 找到 Claude Desktop 配置文件：
   - **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

2. 添加服务器配置：

```json
{
  "mcpServers": {
    "devlake": {
      "command": "devlake-mcp"
    }
  }
}
```

如果从源码运行：

```json
{
  "mcpServers": {
    "devlake": {
      "command": "uv",
      "args": [
        "--directory",
        "/绝对路径/到/devlake-mcp",
        "run",
        "devlake-mcp"
      ]
    }
  }
}
```

3. 重启 Claude Desktop

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

### 与 Cursor 集成

1. 打开 Cursor 设置（Settings）
2. 进入 MCP 标签页
3. 点击 "Add new global MCP server"
4. 添加配置：

```json
{
  "devlake": {
    "command": "devlake-mcp",
    "description": "DevLake MCP Server for querying DevLake data"
  }
}
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

## 开发指南

### 添加新工具

在 `src/devlake_mcp/server.py` 中使用 `@mcp.tool` 装饰器定义新工具：

```python
@mcp.tool
def your_tool_name(param1: str, param2: int) -> dict:
    """
    工具描述（AI 会看到这个）

    Args:
        param1: 参数1的描述
        param2: 参数2的描述

    Returns:
        dict: 返回值描述
    """
    # 你的工具逻辑
    return {"result": "success"}
```

### 添加资源（Resources）

资源用于暴露静态或动态数据：

```python
@mcp.resource("config://settings")
def get_settings() -> dict:
    """提供配置信息"""
    return {"theme": "dark", "version": "1.0"}
```

### 添加提示（Prompts）

提示用于引导 AI 的交互：

```python
@mcp.prompt
def analyze_data(data_type: str) -> str:
    """生成数据分析提示"""
    return f"请分析以下 {data_type} 类型的数据..."
```

### 运行测试

```bash
# 安装开发依赖
uv pip install -e ".[dev]"

# 运行测试
pytest

# 运行测试并显示输出
pytest -s
```

### 代码格式化

```bash
# 使用 black 格式化代码
black src/

# 使用 ruff 检查代码
ruff check src/
```

## 项目结构

```
devlake-mcp/
├── src/
│   └── devlake_mcp/
│       ├── __init__.py      # 包初始化
│       ├── __main__.py      # CLI 入口点
│       └── server.py        # MCP 服务器实现
├── tests/                   # 测试文件
├── pyproject.toml          # 项目配置和依赖
├── README.md               # 本文件
└── .gitignore              # Git 忽略文件
```

## 技术栈

- **FastMCP**: 强大的第三方 MCP 框架 (by jlowin)
- **Python 3.9+**: 需要 Python 3.9 或更高版本

## FastMCP 高级功能

### HTTP 传输

```python
if __name__ == "__main__":
    mcp.run(transport="http", port=8000)
```

### 添加认证

```python
from fastmcp.server.auth import GoogleProvider

auth = GoogleProvider(
    client_id="your-client-id",
    client_secret="your-client-secret"
)

mcp = FastMCP("devlake-mcp", auth=auth)
```

### 使用中间件

```python
from fastmcp.server.middleware import Middleware

class LoggingMiddleware(Middleware):
    async def __call__(self, context, call_next):
        print(f"Request: {context.method}")
        result = await call_next(context)
        print(f"Response: {result}")
        return result

mcp.add_middleware(LoggingMiddleware())
```

### 从 OpenAPI 生成工具

```python
import httpx

async def setup():
    async with httpx.AsyncClient() as client:
        response = await client.get("https://api.example.com/openapi.json")
        spec = response.json()

    mcp = FastMCP.from_openapi(
        spec,
        name="API Server",
        base_url="https://api.example.com"
    )
```

## 故障排查

### pipx 安装失败

确保包中定义了 entry point：
```bash
# 检查 pyproject.toml 中的 [project.scripts] 部分
cat pyproject.toml | grep -A 2 "\[project.scripts\]"
```

### Claude Desktop 无法连接

1. 检查配置文件路径是否正确
2. 确保命令路径使用绝对路径
3. 重启 Claude Desktop
4. 查看 Claude Desktop 的日志文件

### 开发模式下找不到模块

```bash
# 确保在虚拟环境中
source .venv/bin/activate

# 重新安装
pip install -e .
```

## 贡献

欢迎贡献！请随时提交 Issue 或 Pull Request。

## 许可证

MIT License

## 相关资源

- [Model Context Protocol 官方文档](https://modelcontextprotocol.io)
- [FastMCP 官方文档](https://gofastmcp.com)
- [FastMCP GitHub](https://github.com/jlowin/fastmcp)
- [Claude Desktop](https://claude.ai/download)
- [Cursor 编辑器](https://cursor.sh)
