# NagaAgent 3.0

> 智能对话助手，支持多MCP服务、流式语音交互、GRAG知识图谱记忆系统、RESTful API接口、控制台托盘功能。

---

## 🚀 快速开始

### 1. 克隆项目
```bash
git clone [项目地址]
cd NagaAgent3.0
```

### 2. 一键配置

**Windows:**
```powershell
.\setup.ps1
```

**Mac:**
```bash
chmod +x setup_mac.sh
./setup_mac.sh
```

### 3. 启动应用

**Windows (普通模式):**
```powershell
.\start.bat
```

**Windows (托盘模式):**
```powershell
.\start_with_tray.bat
```

**Mac:**
```bash
./start_mac.sh
```

启动后将自动开启PyQt5界面和RESTful API服务器，可同时使用界面对话和API接口。

---

## 🖥️ 系统要求
- **Windows:** Windows 10/11 + PowerShell 5.1+
- **Mac:** macOS 10.15 (Catalina) 或更高版本 + Homebrew
- **通用:** Python 3.8+ (推荐 3.11)

---

## 🛠️ 依赖安装与环境配置

### Windows 环境
- 所有依赖见`requirements.txt`
- 推荐使用虚拟环境：`python -m venv .venv`
- 如遇`greenlet`、`pyaudio`等安装失败，需先装[Microsoft Visual C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/)
- 浏览器自动化需`playwright`，首次用需`python -m playwright install chromium`
- MCP工具依赖：`jmcomic`、`fastmcp`

**依赖安装命令：**
```powershell
# 激活虚拟环境
.venv\Scripts\Activate.ps1

# 安装依赖
pip install -r requirements.txt

# 安装浏览器驱动
python -m playwright install chromium

# 安装MCP工具依赖
pip install jmcomic fastmcp
```

### Mac 环境
- 系统依赖通过Homebrew安装：
  ```bash
  brew install python@3.11 portaudio
  brew install --cask google-chrome
  ```
- Python依赖安装：
  ```bash
  python3 -m venv .venv
  source .venv/bin/activate
  pip install -r requirements.txt
  python -m playwright install chromium
  ```

### 环境检查
```bash
python check_env.py
```

---

## ⚙️ 配置说明

### API 配置
修改 `config.json` 文件中的 `api` 部分：
```json
{
  "api": {
    "api_key": "your-api-key-here",
    "base_url": "https://api.deepseek.com/v1",
    "model": "deepseek-chat",
    "temperature": 0.7,
    "max_tokens": 2000,
    "max_history_rounds": 10
  }
}
```

### API服务器配置
```json
{
  "api_server": {
    "enabled": true,
    "host": "127.0.0.1",
    "port": 8000,
    "auto_start": true,
    "docs_enabled": true
  }
}
```

### GRAG知识图谱记忆系统配置
```json
{
  "grag": {
    "enabled": true,
    "auto_extract": true,
    "context_length": 5,
    "similarity_threshold": 0.6,
    "neo4j_uri": "neo4j://127.0.0.1:7687",
    "neo4j_user": "neo4j",
    "neo4j_password": "your_password",
    "neo4j_database": "neo4j"
  }
}
```

### 获取 API 密钥
1. 访问对应的LLM服务商官网（如DeepSeek、OpenAI等）
2. 注册账号并创建 API 密钥
3. 将密钥填入 `config.json` 文件的 `api.api_key` 字段

---

## 🌟 主要特性

### 核心功能
- **全局配置管理**: 所有变量统一在`config.py`管理，支持.env和环境变量
- **RESTful API接口**: 自动启动HTTP服务器，支持完整对话功能和流式输出
- **GRAG知识图谱记忆系统**: 基于Neo4j的五元组知识图谱，自动提取对话中的实体关系
- **HANDOFF工具调用循环**: 自动解析和执行LLM返回的工具调用，支持多轮递归调用
- **多Agent能力扩展**: 浏览器、文件、代码等多种Agent即插即用
- **跨平台兼容**: Windows/Mac自动适配，浏览器路径自动检测

### 语音交互
- **流式语音交互**: 基于Edge-TTS的OpenAI兼容语音合成
- **智能分句**: 支持pygame后台直接播放和智能分句
- **异步处理**: 文本显示和音频播放完全分离

### UI界面
- **PyQt5动画与UI**: 支持PNG序列帧，loading动画极快
- **Markdown支持**: 聊天窗口支持Markdown语法，包括标题、粗体、斜体、代码块、表格等
- **主题自定义**: 聊天窗口背景透明度、用户名、主题树召回等全部可自定义

### 系统托盘功能
- **控制台托盘**: 使用`start_with_tray.bat`启动，可将终端窗口隐藏到系统托盘
- **自动隐藏**: 启动后3秒自动隐藏控制台窗口
- **任务栏隐藏**: 控制台窗口从任务栏完全隐藏
- **托盘操作**: 右键托盘图标查看菜单，双击显示窗口
- **自启动管理**: 支持注册表方式的自启动功能

### Agent系统
- **动态服务池查询**: 系统通过扫描`agent-manifest.json`文件自动发现和注册服务
- **AgentManager独立系统**: 支持Agent的配置加载、会话管理、消息组装和LLM调用
- **智能占位符替换**: 支持Agent配置、环境变量、时间信息等多种占位符
- **会话隔离与TTL管理**: 支持多用户多会话隔离，自动清理过期会话数据

---

## 🗂️ 目录结构
```
NagaAgent3.0/
├── main.py                     # 主入口
├── config.py                   # 全局配置
├── conversation_core.py        # 对话核心（含工具调用循环主逻辑）
├── apiserver/                  # API服务器模块
│   ├── api_server.py           # FastAPI服务器
│   ├── start_server.py         # 启动脚本
│   └── README.md               # API文档
├── mcpserver/
│   ├── mcp_manager.py          # MCP服务管理
│   ├── mcp_registry.py         # Agent注册与schema元数据
│   ├── agent_manager.py        # Agent管理器（独立系统）
│   ├── agent_xxx/              # 各类自定义Agent
│   │   └── agent-manifest.json # Agent配置文件
├── agent_configs/              # Agent配置文件目录
│   └── *.json                  # Agent配置文件
├── requirements.txt             # 项目依赖
├── setup.ps1                   # Windows配置脚本
├── start.bat                   # Windows启动脚本
├── start_with_tray.bat         # Windows托盘启动脚本
├── setup_mac.sh                # Mac配置脚本
├── check_env.py                # 跨平台环境检查
├── summer_memory/              # GRAG知识图谱记忆系统
│   ├── memory_manager.py       # 记忆管理器
│   ├── quintuple_extractor.py  # 五元组提取器
│   ├── quintuple_graph.py      # Neo4j图谱操作
│   ├── quintuple_rag_query.py  # 记忆查询
│   └── quintuple_visualize_v2.py  # 图谱可视化
├── logs/                       # 日志（含历史txt对话）
├── voice/                      # 语音相关
│   ├── tts_handler.py          # TTS处理器
│   └── voice_integration.py    # 语音集成
├── ui/                         # 前端UI
│   ├── pyqt_chat_window.py     # PyQt聊天窗口
│   ├── response_utils.py       # 前端通用响应解析工具
│   └── tray/                   # 系统托盘模块
│       ├── console_tray.py     # 控制台托盘功能
│       ├── auto_start.py       # 自启动管理
│       └── README.md           # 托盘使用说明
└── README.md                   # 项目说明
```

---

## 🔧 工具调用循环机制

### 系统概述
NagaAgent支持两种类型的工具调用：
- **MCP服务调用**: 通过`agentType: mcp`调用MCP类型的Agent
- **Agent服务调用**: 通过`agentType: agent`调用Agent类型的Agent

### 工具调用格式

#### MCP服务调用格式
```json
{
  "agentType": "mcp",
  "service_name": "MCP服务名称",
  "tool_name": "工具名称",
  "参数名": "参数值"
}
```

#### Agent服务调用格式
```json
{
  "agentType": "agent",
  "agent_name": "Agent名称",
  "prompt": "任务内容"
}
```

### 工具调用流程
1. **LLM输出JSON格式**: LLM根据用户需求输出工具调用请求
2. **自动解析agentType**: 系统首先解析agentType字段，确定调用类型
3. **路由到对应管理器**: 
   - `mcp`类型 → 路由到MCPManager处理
   - `agent`类型 → 路由到AgentManager处理
4. **执行工具调用**: 调用对应的服务执行具体任务
5. **结果返回LLM**: 将工具执行结果返回给LLM
6. **循环处理**: 重复步骤2-5，直到LLM输出普通文本或无工具调用

### 配置参数
```python
# config.py中的工具调用循环配置
MAX_handoff_LOOP_STREAM = 5      # 流式模式最大工具调用循环次数
MAX_handoff_LOOP_NON_STREAM = 5  # 非流式模式最大工具调用循环次数
SHOW_handoff_OUTPUT = False      # 是否显示工具调用输出
```

---

## 🌐 多Agent与MCP服务

### 动态服务池查询功能

#### 核心查询方法
```python
from mcpserver.mcp_registry import (
    get_all_services_info,      # 获取所有服务信息
    get_service_info,           # 获取单个服务详情
    query_services_by_capability, # 按能力搜索服务
    get_service_statistics,     # 获取统计信息
    get_available_tools         # 获取服务工具列表
)
```

#### API端点
- `GET /mcp/services` - 获取所有服务列表和统计信息
- `GET /mcp/services/{service_name}` - 获取指定服务详情
- `GET /mcp/services/search/{capability}` - 按能力搜索服务
- `GET /mcp/services/{service_name}/tools` - 获取服务工具列表
- `GET /mcp/statistics` - 获取服务统计信息

### 典型用法示例
```python
# 读取文件内容
await s.mcp.handoff(
  service_name="file",
  task={"action": "read", "path": "test.txt"}
)

# 运行Python代码
await s.mcp.handoff(
  service_name="coder",
  task={"action": "run", "file": "main.py"}
)
```

---

## 🤖 AgentManager 独立系统

### 系统概述
AgentManager是一个独立的Agent注册和调用系统，支持从配置文件动态加载Agent定义，提供统一的调用接口和完整的生命周期管理。

### 核心功能

#### 1. 配置管理
- **动态配置加载**: 从`agent_configs/`目录自动扫描和加载Agent配置文件
- **配置验证**: 自动验证Agent配置的完整性和有效性
- **热重载**: 支持运行时重新加载配置，无需重启系统
- **环境变量支持**: 支持从环境变量和`.env`文件加载敏感配置

#### 2. 会话管理
- **多会话支持**: 每个Agent支持多个独立的会话上下文
- **历史记录**: 自动维护对话历史，支持上下文召回
- **会话过期**: 自动清理过期的会话数据，节省内存
- **会话隔离**: 不同用户和不同Agent的会话完全隔离

#### 3. 智能占位符替换
支持多种类型的占位符替换：

**Agent配置占位符**:
- `{{AgentName}}` - Agent名称
- `{{Description}}` - 描述信息
- `{{ModelId}}` - 模型ID
- `{{Temperature}}` - 温度参数
- `{{MaxTokens}}` - 最大输出token数
- `{{ModelProvider}}` - 模型提供商

**环境变量占位符**:
- `{{ENV_VAR_NAME}}` - 系统环境变量

**时间占位符**:
- `{{CurrentTime}}` - 当前时间 (HH:MM:SS)
- `{{CurrentDate}}` - 当前日期 (YYYY-MM-DD)
- `{{CurrentDateTime}}` - 完整时间 (YYYY-MM-DD HH:MM:SS)

### 配置文件格式

#### Agent配置文件示例
```json
{
  "ExampleAgent": {
    "model_id": "deepseek-chat",
    "name": "示例助手",
    "base_name": "ExampleAgent",
    "system_prompt": "你是{{AgentName}}，一个专业的{{Description}}。\n\n当前时间：{{CurrentDateTime}}\n模型：{{ModelId}}\n温度：{{Temperature}}\n\n请用中文回答，保持专业和友好的态度。",
    "max_output_tokens": 8192,
    "temperature": 0.7,
    "description": "智能助手，擅长回答各种问题",
    "model_provider": "openai",
    "api_base_url": "https://api.deepseek.com/v1",
    "api_key": "{{DEEPSEEK_API_KEY}}"
  }
}
```

### 使用示例

#### 基本调用
```python
from mcpserver.agent_manager import get_agent_manager

# 获取AgentManager实例
agent_manager = get_agent_manager()

# 调用Agent
result = await agent_manager.call_agent(
    agent_name="ExampleAgent",
    prompt="请帮我分析这份数据",
    session_id="user_123"
)
```

#### 便捷函数调用
```python
from mcpserver.agent_manager import call_agent, list_agents, get_agent_info

# 便捷调用
result = await call_agent("ExampleAgent", "你好")

# 获取Agent列表
agents = list_agents()
```

---

## 📋 Agent Manifest标准化

### 标准化规范
所有Agent必须使用标准化的`agent-manifest.json`配置文件，确保一致性和可维护性。

#### 必需字段
- `name`: Agent唯一标识符
- `displayName`: 显示名称
- `version`: 版本号（x.y.z格式）
- `description`: 功能描述
- `author`: 作者或模块名称
- `agentType`: Agent类型（mcp/agent）
- `entryPoint`: 入口点配置（module和class）

### 创建新Agent

#### 创建MCP类型Agent
1. 在`mcpserver/`目录下创建新的Agent目录
2. 复制`AGENT_MANIFEST_TEMPLATE.json`到Agent目录
3. 修改manifest文件内容
4. 创建Agent实现类
5. 重启系统自动注册

#### 创建Agent类型Agent
1. 在`agent_configs/`目录下创建配置文件
2. 定义Agent配置（模型、提示词等）
3. 配置环境变量（API密钥等）
4. 重启系统自动加载

---

## 🖥️ 系统托盘功能

### 功能特性
- **控制台托盘**: 将终端窗口隐藏到系统托盘，支持自动隐藏
- **任务栏隐藏**: 控制台窗口从任务栏完全隐藏
- **托盘图标**: 系统托盘显示应用图标，支持右键菜单
- **自启动管理**: 支持注册表方式的自启动功能
- **托盘消息**: 支持状态通知和消息提示

### 使用方法

#### 托盘模式启动
```bash
# Windows
.\start_with_tray.bat
```

#### 托盘菜单功能
- **显示控制台**: 从托盘恢复控制台窗口显示
- **隐藏控制台**: 隐藏控制台窗口到托盘
- **开机自启动**: 切换自启动状态
- **退出**: 完全退出应用

### 技术实现
- **窗口钩子**: 监听控制台窗口的关闭事件，拦截关闭操作
- **窗口样式**: 使用`WS_EX_TOOLWINDOW`样式让窗口不在任务栏显示
- **自动隐藏**: 启动后3秒自动隐藏控制台窗口
- **托盘集成**: 使用PyQt5实现系统托盘功能

### 注意事项
1. **权限要求**: 自启动功能需要管理员权限
2. **依赖安装**: 需要安装`PyQt5`库
3. **图标文件**: 默认使用`ui/window_icon.png`作为托盘图标
4. **启动方式**: 使用`start_with_tray.bat`启动以启用托盘功能

---

## 🌐 RESTful API 服务

NagaAgent内置完整的RESTful API服务器，启动时自动开启，支持所有对话功能：

### API接口说明

- **基础地址**: `http://127.0.0.1:8000` (可在config.py中配置)
- **交互式文档**: `http://127.0.0.1:8000/docs`
- **OpenAPI规范**: `http://127.0.0.1:8000/openapi.json`

### 主要接口

#### 健康检查
```bash
GET /health
```

#### 对话接口
```bash
# 普通对话
POST /chat
{
  "message": "你好，娜迦",
  "session_id": "optional-session-id"
}

# 流式对话 (Server-Sent Events)
POST /chat/stream
{
  "message": "请介绍一下人工智能的发展历程"
}
```

#### 系统管理接口
```bash
# 获取系统信息
GET /system/info

# 切换开发者模式
POST /system/devmode

# 获取记忆统计
GET /memory/stats
```

---

## 📝 前端UI与响应适配
- **所有后端返回均为结构化JSON**: 前端通过`ui/response_utils.py`的`extract_message`方法自动适配多种返回格式
- **优先显示逻辑**: 优先显示`data.content`，其次`message`，最后原样返回，兼容所有Agent
- **换行符自动适配**: PyQt前端自动将所有`\n`和`\\n`换行符转为`<br>`，多行内容显示无障碍
- **UI动画**: 侧栏点击切换时，侧栏宽度、主聊天区宽度、输入框高度均采用同步动画
- **主题自定义**: UI动画、主题、昵称、透明度等全部可在`config.py`和`pyqt_chat_window.py`灵活配置

---

## 🔊 流式语音交互
- **支持语音输入**: 流式识别，自动转文字
- **支持语音输出**: 流式合成，边播边出
- **完全异步处理**: 重构语音集成系统，文本显示和音频播放完全分离
- **消除重复播放**: 移除流式分句和最终文本的重复播放问题
- **前端即时显示**: 前端立即显示文本，不再等待音频处理完成
- **依赖与配置**: 详见`voice/voice_config.py`和README相关章节

---

## 📝 其它亮点
- **记忆权重动态调整**: 支持AI/人工标记important，权重/阈值/清理策略全部在`config.py`统一管理
- **主题归类自动化**: 主题归类、召回、权重提升、清理等全部自动化
- **检索日志自动记录**: 参数可调，GRAG配置示例见`config.py`
- **历史对话兼容升级**: 支持将旧版txt对话内容一键导入GRAG知识图谱记忆系统
- **工具调用循环自动执行机制**: 支持多轮递归调用，最大循环次数可配置
- **所有Agent的注册元数据已集中在`mcpserver/mcp_registry.py`**: 主流程和管理器极简，扩展维护更方便
- **自动注册/热插拔Agent机制**: 新增/删除Agent只需增删py文件，无需重启主程序
- **Agent Manifest标准化**: 统一的`agent-manifest.json`格式，支持完整的字段验证和类型检查
- **动态服务池查询**: 系统通过扫描`agent-manifest.json`文件自动发现和注册服务，无需手动配置静态服务列表
- **AgentManager独立系统**: 支持Agent的配置加载、会话管理、消息组装和LLM调用，提供完整的Agent生命周期管理
- **智能占位符替换**: 支持Agent配置、环境变量、时间信息等多种占位符，实现动态提示词生成
- **完整消息序列构建**: 自动组装系统消息、历史消息和用户消息，确保对话上下文完整性
- **多模型提供商支持**: 支持OpenAI、DeepSeek、Anthropic等多种LLM提供商，每个Agent可独立配置
- **会话隔离与TTL管理**: 支持多用户多会话隔离，自动清理过期会话数据
- **统一工具调用接口**: MCP和Agent类型服务通过统一的JSON格式调用，支持混合调用场景

---

## 🆙 历史对话兼容升级
- **支持将旧版txt对话内容一键导入GRAG知识图谱记忆系统**: 兼容主题、分层、五元组等所有新特性
- **激活指令**:
  ```
  #夏园系统兼容升级
  ```
- **系统会自动遍历logs目录下所有txt日志**: 列出所有历史对话内容并编号，输出到终端和`summer_memory/history_dialogs.json`
- **用户可查看编号后，选择导入方式**:
  - 全部导入：
    ```
    python summer_memory/main.py import all
    ```
  - 选择性导入（如第1、3、5-8条）：
    ```
    python summer_memory/main.py import 1,3,5-8
    ```
- **兼容过程自动判重**: 已入库内容不会重复导入，支持断点续跑
- **兼容内容全部走AI自动主题归类与分层**: 完全与新系统一致
- **详细进度、结果和异常均有反馈**: 安全高效

---

## 🔧 最新更新 (v3.0.5)

### 系统托盘功能增强
- **控制台托盘功能**: 实现真正的"最小化到托盘"功能
- **窗口钩子**: 监听控制台窗口的关闭事件，拦截关闭操作
- **任务栏隐藏**: 使用`WS_EX_TOOLWINDOW`样式让窗口不在任务栏显示
- **自动隐藏**: 启动后3秒自动隐藏控制台窗口
- **托盘消息**: 支持托盘消息通知和状态提示

### MCP工具依赖
- **新增依赖**: 添加`jmcomic`和`fastmcp`依赖到`requirements.txt`
- **虚拟环境安装**: 确保依赖安装到虚拟环境中
- **依赖验证**: 提供依赖安装验证脚本

### 技术改进
- **窗口监控**: 添加窗口状态监控线程，实时检测窗口显示/隐藏状态
- **样式管理**: 保存和恢复原始窗口样式，确保功能稳定性
- **错误处理**: 增强窗口操作和托盘功能的错误处理机制

---

## ❓ 常见问题

### 环境检查
```bash
python check_env.py
```

### Windows 环境
- **Python版本/依赖/虚拟环境/浏览器驱动等问题**: 详见`setup.ps1`与本README
- **IDE报import错误**: 重启并选择正确解释器
- **语音依赖安装失败**: 先装C++ Build Tools
- **MCP工具依赖缺失**: 运行`pip install jmcomic fastmcp`

### Mac 环境
- **Python版本过低**: `brew install python@3.11`
- **PyAudio安装失败**: `brew install portaudio && pip install pyaudio`
- **权限问题**: `chmod +x *.sh`

### API服务器问题
- **端口占用**: 修改`config.py`中的`API_SERVER_PORT`
- **代理干扰**: 临时禁用代理 `unset ALL_PROXY http_proxy https_proxy`
- **依赖缺失**: 确保安装了FastAPI和Uvicorn `pip install fastapi uvicorn[standard]`
- **无法访问**: 检查防火墙设置，确保端口未被阻塞

### 工具调用问题
- **工具调用循环次数过多**: 调整`config.py`中的`MAX_handoff_LOOP_STREAM`和`MAX_handoff_LOOP_NON_STREAM`
- **工具调用失败**: 检查MCP服务是否正常运行，查看日志输出
- **格式错误**: 确保LLM输出严格遵循JSON格式

### GRAG记忆系统问题
- **Neo4j连接失败**: 检查Neo4j服务是否启动，确认连接参数正确
- **记忆查询无结果**: 检查五元组是否正确提取和存储
- **性能问题**: 调整`config.py`中的GRAG相关参数

### 系统托盘问题
- **托盘图标不显示**: 检查图标文件是否存在，确认PyQt5安装正确
- **控制台托盘不工作**: 确认使用`start_with_tray.bat`启动
- **自启动失败**: 确认管理员权限，检查注册表权限
- **窗口最小化问题**: 检查托盘集成是否正确，确认事件处理函数

### AgentManager问题
- **Agent配置加载失败**: 检查`agent_configs/`目录下的JSON文件格式是否正确
- **API调用失败**: 确认API密钥配置正确，检查网络连接
- **会话历史丢失**: 检查会话TTL配置，确认会话未过期
- **占位符替换失败**: 确认环境变量已正确设置
- **内存占用过高**: 调整`max_history_rounds`参数，减少历史消息数量

### 通用问题
- **浏览器无法启动**: 检查playwright安装与网络
- **主题树/索引/参数/密钥全部在`config.py`统一管理**
- **聊天输入`#devmode`进入开发者模式**: 后续对话不写入GRAG记忆，仅用于工具调用测试

### 最佳实践

#### Agent配置最佳实践
1. **使用环境变量**: 敏感信息如API密钥应使用环境变量
2. **合理设置参数**: 根据任务需求调整temperature和max_output_tokens
3. **优化提示词**: 使用占位符实现动态内容，提高灵活性
4. **会话管理**: 合理设置会话TTL，避免内存泄漏

#### 性能优化建议
1. **缓存配置**: 启用配置缓存，减少文件读取开销
2. **并发控制**: 合理控制并发Agent调用数量
3. **资源清理**: 定期清理过期会话和临时数据
4. **监控日志**: 启用调试模式监控系统性能

#### 安全建议
1. **API密钥管理**: 使用环境变量或密钥管理服务
2. **输入验证**: 对用户输入进行验证和清理
3. **错误处理**: 避免在错误信息中泄露敏感信息
4. **访问控制**: 实现适当的访问控制机制

---

## 📝 许可证
MIT License

---

如需详细功能/API/扩展说明，见各模块注释与代码，所有变量唯一、注释中文、极致精简。 
