# NagaAgent 3.0

> 智能对话助手，支持多MCP服务、流式语音交互、GRAG知识图谱记忆系统、RESTful API接口、极致精简代码风格。

---

## ⚡ 快速开始

### 1. 克隆项目
```bash
git clone [项目地址]
cd NagaAgent
```

### 2. 一键配置

**Windows:**
```powershell
.\setup.ps1
```

**Mac:**
```bash
chmod +x quick_deploy_mac.sh
./quick_deploy_mac.sh
```

### 3. 启动系统

**Windows:**
```powershell
.\start.bat
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
```powershell
# 推荐使用 uv（现代化包管理器）
uv sync
python -m playwright install edge

# 或者使用传统 pip
python -m venv .venv
.venv\Scripts\Activate
pip install -e .
python -m playwright install edge
```

### Mac 环境
```bash
# 安装基础依赖
brew install python@3.11 portaudio
brew install --cask microsoft-edge

# Python依赖安装
uv sync
python -m playwright install edge
```

### 环境检查
```bash
python check_env.py
```

---

## ⚙️ 配置说明

### 重要配置变更说明
**v3.0版本配置简化：**
- 移除了`config.json`中的`mcp_services`和`agent_services`静态配置字段
- 系统现在通过动态扫描`agent-manifest.json`文件自动发现和注册服务
- 所有服务信息通过动态服务池实时查询，无需手动维护服务列表

### API 密钥配置
直接修改 `config.json` 文件中的配置：
```json
{
  "api": {
    "api_key": "your_api_key_here",
    "base_url": "https://api.deepseek.com/v1",
    "model": "deepseek-chat"
  }
}
```

### MQTT设备控制配置
```json
{
  "mqtt": {
    "enabled": true,
    "broker": "your_mqtt_broker",
    "port": 1883,
    "topic": "device/control",
    "client_id": "nagaagent_mqtt",
    "username": "your_username",
    "password": "your_password"
  }
}
```

### 浏览器配置
```json
{
  "browser": {
    "playwright_headless": false,
    "edge_lnk_path": "C:\\Users\\YourName\\Desktop\\Microsoft Edge.lnk"
  }
}
```

---

## 🌟 主要特性

### 核心功能
- **全局配置统一管理**：所有配置通过`config.py`统一管理，支持.env和环境变量
- **RESTful API接口**：自动启动HTTP服务器，支持完整对话功能和流式输出
- **流式语音交互**：支持语音输入识别和语音输出合成
- **GRAG知识图谱记忆系统**：基于Neo4j的三元组知识图谱，自动提取对话中的实体关系
- **工具调用循环机制**：自动解析和执行LLM返回的工具调用，支持多轮递归调用

### 多Agent系统
- **动态Agent注册**：通过扫描`agent-manifest.json`文件自动发现和注册服务
- **AgentManager独立系统**：支持Agent的配置加载、会话管理、消息组装和LLM调用
- **MCP服务集成**：支持浏览器、文件、代码、天气、系统控制等多种MCP服务
- **MQTT设备控制**：支持通过MQTT协议远程控制智能设备
- **热插拔机制**：新增/删除Agent只需增删文件，无需重启主程序

### 前端UI
- **PyQt5动画界面**：支持PNG序列帧，loading动画流畅
- **Markdown渲染**：支持标题、粗体、斜体、代码块、表格等
- **流式输出**：前后端全链路流式输出，边生成边显示
- **响应式布局**：自动适配不同屏幕尺寸

### 开发友好
- **极致精简代码**：注释全中文，组件解耦，便于扩展
- **统一错误处理**：完善的错误处理和日志记录
- **跨平台兼容**：Windows/Mac自动适配，依赖智能安装
- **调试模式**：支持详细的调试日志输出

---

## 🗂️ 目录结构

```
NagaAgent/
├── main.py                     # 主入口
├── config.py                   # 全局配置
├── conversation_core.py        # 对话核心（含工具调用循环主逻辑）
├── apiserver/                  # API服务器模块
│   ├── api_server.py           # FastAPI服务器
│   └── start_server.py         # 启动脚本
├── mcpserver/                  # MCP服务模块
│   ├── mcp_manager.py          # MCP服务管理
│   ├── mcp_registry.py         # Agent注册与schema元数据
│   ├── agent_manager.py        # Agent管理器（独立系统）
│   ├── agent_registry.py       # Agent注册系统
│   └── agent_xxx/              # 各类自定义Agent
│       ├── agent_xxx.py        # Agent实现
│       └── agent-manifest.json # Agent配置文件
├── mqtt_tool/                  # MQTT设备控制工具
│   ├── device_switch.py        # MCP设备开关控制工具
│   └── README.md               # MQTT使用说明
├── summer_memory/              # GRAG知识图谱记忆系统
│   ├── memory_manager.py       # 记忆管理器
│   ├── extractor_ds_tri.py     # 三元组提取器
│   ├── graph.py                # Neo4j图谱操作
│   └── rag_query_tri.py        # 记忆查询
├── ui/                         # 前端UI
│   ├── pyqt_chat_window.py     # PyQt聊天窗口
│   └── response_utils.py       # 前端通用响应解析工具
├── voice/                      # 语音相关
│   ├── voice_config.py         # 语音配置
│   └── voice_handler.py        # 语音处理
├── setup.ps1                   # Windows配置脚本
├── start.bat                   # Windows启动脚本
├── setup_mac.sh                # Mac配置脚本
├── quick_deploy_mac.sh         # Mac一键部署脚本
└── check_env.py                # 跨平台环境检查
```

---

## 🔧 工具调用循环机制

### 系统概述
NagaAgent支持两种类型的工具调用：
- **MCP服务调用**：通过`agentType: mcp`调用MCP类型的Agent
- **Agent服务调用**：通过`agentType: agent`调用Agent类型的Agent

### TOOL_REQUEST格式

#### MCP服务调用格式
```
<<<[TOOL_REQUEST]>>>
agentType: 「始」mcp「末」
service_name: 「始」服务名称「末」
tool_name: 「始」工具名称「末」
param1: 「始」参数值1「末」
param2: 「始」参数值2「末」
<<<[END_TOOL_REQUEST]>>>
```

#### Agent服务调用格式
```
<<<[TOOL_REQUEST]>>>
agentType: 「始」agent「末」
agent_name: 「始」Agent名称「末」
query: 「始」用户任务内容「末」
<<<[END_TOOL_REQUEST]>>>
```

### 工具调用流程
1. **LLM输出TOOL_REQUEST格式**：LLM根据用户需求输出工具调用请求
2. **自动解析agentType**：系统首先解析agentType字段，确定调用类型
3. **路由到对应管理器**：
   - `mcp`类型 → 路由到MCPManager处理
   - `agent`类型 → 路由到AgentManager处理
4. **执行工具调用**：调用对应的服务执行具体任务
5. **结果返回LLM**：将工具执行结果返回给LLM
6. **循环处理**：重复步骤2-5，直到LLM输出普通文本或无工具调用

---

## 🤖 AgentManager 独立系统

### 系统概述
AgentManager是一个独立的Agent注册和调用系统，支持从配置文件动态加载Agent定义，提供统一的调用接口和完整的生命周期管理。

### 核心功能

#### 1. 配置管理
- **动态配置加载**：从`agent_configs/`目录自动扫描和加载Agent配置文件
- **配置验证**：自动验证Agent配置的完整性和有效性
- **热重载**：支持运行时重新加载配置，无需重启系统
- **环境变量支持**：支持从环境变量和`.env`文件加载敏感配置

#### 2. 会话管理
- **多会话支持**：每个Agent支持多个独立的会话上下文
- **历史记录**：自动维护对话历史，支持上下文召回
- **会话过期**：自动清理过期的会话数据，节省内存
- **会话隔离**：不同用户和不同Agent的会话完全隔离

#### 3. 智能占位符替换
支持多种类型的占位符替换：
- `{{AgentName}}` - Agent名称
- `{{CurrentTime}}` - 当前时间
- `{{CurrentDate}}` - 当前日期
- `{{ENV_VAR_NAME}}` - 环境变量

### 使用示例

#### 基本调用
```python
from mcpserver.agent_manager import get_agent_manager

# 获取AgentManager实例
agent_manager = get_agent_manager()

# 调用Agent
result = await agent_manager.call_agent(
    agent_name="ExampleAgent",
    query="请帮我分析这份数据",
    session_id="user_123"
)
```

#### 工具调用格式
```
<<<[TOOL_REQUEST]>>>
agentType: 「始」agent「末」
agent_name: 「始」ExampleAgent「末」
query: 「始」用户任务内容「末」
<<<[END_TOOL_REQUEST]>>>
```

---

## 🌐 MQTT设备控制

### 功能特性
- **双设备控制**：支持同时控制两个独立设备
- **MQTT通信**：基于标准MQTT协议，支持多种MQTT服务器
- **自动重连**：智能自动重连机制，支持指数退避算法
- **编码处理**：自动处理UTF-8/GBK/Latin-1编码转换
- **状态反馈**：实时接收设备状态反馈

### 配置说明
```json
{
  "mqtt": {
    "enabled": true,
    "broker": "broker.emqx.io",
    "port": 1883,
    "topic": "device/switch",
    "client_id": "mcp_device_switch",
    "username": "",
    "password": ""
  }
}
```

### 使用示例
```python
from mqtt_tool.device_switch import device_manager

# 连接MQTT
device_manager.connect()

# 发送设备控制命令
success, message = device_manager.switch_devices(1, 0)  # 开启设备1，关闭设备2

# 获取连接状态
status = device_manager.get_connection_status()
```

### 消息格式
```json
{
  "device1": 1,
  "device2": 0,
  "timestamp": 1753018575.5008261
}
```

---

## 🌐 RESTful API 服务

### API接口说明
- **基础地址**: `http://127.0.0.1:8000`
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

#### MCP服务查询
```bash
# 获取所有服务列表
GET /mcp/services

# 获取指定服务详情
GET /mcp/services/{service_name}

# 按能力搜索服务
GET /mcp/services/search/{capability}
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

## 🔊 流式语音交互

### 功能特性
- **语音输入**：流式识别，自动转文字
- **语音输出**：流式合成，边播边出
- **多语言支持**：支持中文、英文等多种语言
- **实时处理**：低延迟的语音交互体验

### 配置说明
```json
{
  "tts": {
    "api_key": "your_api_key_here",
    "port": 5051,
    "default_voice": "zh-CN-XiaoxiaoNeural",
    "default_format": "mp3",
    "default_speed": 1.0,
    "default_language": "zh-CN"
  }
}
```

---

## 📝 前端UI与响应适配

### 核心特性
- **结构化JSON响应**：所有后端返回均为结构化JSON，前端通过`ui/response_utils.py`自动适配
- **多格式兼容**：优先显示`data.content`，其次`message`，最后原样返回
- **换行符处理**：PyQt前端自动将所有`\n`和`\\n`换行符转为`<br>`
- **Markdown渲染**：支持标题、粗体、斜体、代码块、表格等

### 自定义配置
- **背景透明度**：由`config.BG_ALPHA`统一控制，取值0~1
- **用户名**：自动识别电脑名，变量`config.USER_NAME`
- **动画效果**：侧栏切换、输入框隐藏等动画效果可自定义

---

## ❓ 常见问题

### 环境检查
```bash
python check_env.py
```

### Windows 环境
- Python版本/依赖/虚拟环境/浏览器驱动等问题，详见`setup.ps1`
- IDE报import错误，重启并选择正确解释器
- 语音依赖安装失败，先装C++ Build Tools

### Mac 环境
- Python版本过低：`brew install python@3.11`
- PyAudio安装失败：`brew install portaudio && pip install pyaudio`
- 权限问题：`chmod +x *.sh`

### API服务器问题
- 端口占用：修改`config.py`中的`API_SERVER_PORT`
- 代理干扰：临时禁用代理 `unset ALL_PROXY http_proxy https_proxy`
- 依赖缺失：确保安装了FastAPI和Uvicorn `pip install fastapi uvicorn[standard]`

### 工具调用问题
- 工具调用循环次数过多：调整`config.py`中的`MAX_handoff_LOOP_STREAM`和`MAX_handoff_LOOP_NON_STREAM`
- 工具调用失败：检查MCP服务是否正常运行，查看日志输出
- 格式错误：确保LLM输出严格遵循TOOL_REQUEST格式

### MQTT问题
- 连接失败：检查MQTT服务器地址和端口，确认网络连接
- 消息发送失败：检查topic配置和权限设置
- 编码问题：系统自动处理UTF-8/GBK/Latin-1编码转换

### AgentManager问题
- **Agent配置加载失败**：检查`agent_configs/`目录下的JSON文件格式是否正确
- **API调用失败**：确认API密钥配置正确，检查网络连接
- **会话历史丢失**：检查会话TTL配置，确认会话未过期
- **占位符替换失败**：确认环境变量已正确设置

### 最佳实践

#### 配置管理
1. **使用环境变量**：敏感信息如API密钥应使用环境变量
2. **合理设置参数**：根据任务需求调整temperature和max_output_tokens
3. **优化提示词**：使用占位符实现动态内容，提高灵活性
4. **会话管理**：合理设置会话TTL，避免内存泄漏

#### 性能优化
1. **缓存配置**：启用配置缓存，减少文件读取开销
2. **并发控制**：合理控制并发Agent调用数量
3. **资源清理**：定期清理过期会话和临时数据
4. **监控日志**：启用调试模式监控系统性能

#### 安全建议
1. **API密钥管理**：使用环境变量或密钥管理服务
2. **输入验证**：对用户输入进行验证和清理
3. **错误处理**：避免在错误信息中泄露敏感信息
4. **访问控制**：实现适当的访问控制机制

---

## 📝 许可证
MIT License

---

## 🔗 相关链接

- [项目地址](https://github.com/your-repo/NagaAgent)
- [API文档](http://127.0.0.1:8000/docs)
- [MQTT工具文档](mqtt_tool/README.md)
- [Agent配置指南](mcpserver/MANIFEST_STANDARDIZATION.md)

---

如需详细功能/API/扩展说明，见各模块注释与代码，所有变量唯一、注释中文、极致精简。 
