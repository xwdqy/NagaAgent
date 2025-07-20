# Word子Agent集成说明

## 概述

本集成方案将 Office Word MCP Server 作为多 Agent 系统中的一个独立子 Agent 进行集成。通过创建一个专门的 Word 子 Agent，避免了在主 Agent 中直接注册大量 Word 工具导致的提示词过长问题。

## 架构设计

```
主 Agent (处理一般任务)
    ↓
AgentManager (任务分发器)
    ↓
Word 子 Agent (专门处理 Word 任务)
    ↓
Word MCP Server (提供 Word 工具)
```

### 核心组件

1. **Word 子 Agent** (`mcpserver/word_agent/word_agent.py`)
   - 专门的 LLM 实例，专门处理 Word 相关任务
   - 通过 `handle_handoff` 方法接收任务
   - 直接调用 Word MCP 服务的工具

2. **AgentManager 增强** (`mcpserver/agent_manager.py`)
   - 新增 `_is_word_related_task` 方法识别 Word 任务
   - 新增 `_handoff_to_word_agent` 方法转交任务
   - 使用统一的 `call_agent` 方法进行任务调用

3. **Word MCP Server** (`mcpserver/Office-Word-MCP-Server-main/`)
   - 标准的 MCP 服务，通过 FastMCP 暴露工具
   - 提供完整的 Word 文档操作功能

## 文件结构

```
mcpserver/
├── word_agent/                    # Word子Agent包
│   ├── __init__.py               # 包初始化
│   └── word_agent.py             # Word子Agent实现
├── Office-Word-MCP-Server-main/   # Word MCP服务
│   ├── agent-manifest.json       # Agent配置文件
│   ├── word_document_server/     # Word服务核心
│   └── ...
├── agent_manager.py              # Agent管理器（已增强）
├── mcp_registry.py               # MCP服务注册表
└── mcp_manager.py                # MCP管理器
```

## 配置说明

### 1. Agent配置文件

`mcpserver/Office-Word-MCP-Server-main/agent-manifest.json`:

```json
{
  "name": "word-document-server",
  "displayName": "Word文档处理助手",
  "agentType": "agent",
  "entryPoint": {
    "module": "mcpserver.word_agent.word_agent",
    "class": "WordAgent"
  },
  "systemPrompt": "你是一个专业的Microsoft Word文档处理助手...",
  "capabilities": {
    "invocationCommands": [
      {
        "command": "create_document",
        "description": "创建新的Word文档",
        "example": "..."
      }
      // ... 更多命令
    ]
  }
}
```

### 2. 统一API配置

所有 Agent 使用 `config.py` 中的统一配置：

```python
# config.py
OPENAI_API_KEY = "your-api-key"
OPENAI_BASE_URL = "https://api.deepseek.com/v1"
DEFAULT_MODEL = "deepseek-chat"
```

## 调用流程

### 1. 任务识别

当用户请求 Word 相关任务时：

```python
# AgentManager 识别任务类型
if self._is_word_related_task(action, action_args):
    return await self._handoff_to_word_agent(action_args)
```

### 2. 任务转交

AgentManager 将任务转交给 Word 子 Agent：

```python
# 从MCP注册表获取Word Agent
word_agent = MCP_REGISTRY.get("word-document-server")
result = await word_agent.handle_handoff(action_args)
```

### 3. 工具调用

Word 子 Agent 调用 Word MCP 服务的工具：

```python
# 直接调用MCP工具
if self._is_direct_mcp_call(action):
    return await self._call_mcp_tool(task)

# 或使用LLM分析任务
return await self._process_with_llm(task)
```

## 支持的操作

Word 子 Agent 支持以下 Word 相关操作：

### 文档管理
- `create_document` - 创建新文档
- `copy_document` - 复制文档
- `get_document_info` - 获取文档信息
- `get_document_text` - 提取文档文本
- `get_document_outline` - 获取文档大纲
- `list_available_documents` - 列出可用文档
- `convert_to_pdf` - 转换为PDF

### 内容添加
- `add_heading` - 添加标题
- `add_paragraph` - 添加段落
- `add_table` - 添加表格
- `add_picture` - 添加图片
- `add_page_break` - 添加分页符
- `add_footnote_to_document` - 添加脚注
- `add_endnote_to_document` - 添加尾注

### 内容编辑
- `format_text` - 格式化文本
- `search_and_replace` - 搜索替换
- `delete_paragraph` - 删除段落
- `create_custom_style` - 创建自定义样式
- `format_table` - 格式化表格

### 内容提取
- `get_paragraph_text_from_document` - 获取指定段落
- `find_text_in_document` - 查找文本

### 文档保护
- `protect_document` - 保护文档
- `unprotect_document` - 解除保护
- `customize_footnote_style` - 自定义脚注样式

## 测试方法

### 1. 运行集成测试

```bash
python test_word_agent_integration.py
```

### 2. 测试用例

测试脚本包含以下测试用例：

1. **创建文档测试**
   ```python
   test_action = {
       "action": "create_document",
       "filename": "test_report.docx",
       "title": "测试报告",
       "author": "测试用户"
   }
   ```

2. **添加内容测试**
   ```python
   test_action = {
       "action": "add_heading",
       "filename": "test_report.docx",
       "text": "项目概述",
       "level": 1
   }
   ```

3. **格式化测试**
   ```python
   test_action = {
       "action": "format_text",
       "filename": "test_report.docx",
       "paragraph_index": 0,
       "start_pos": 0,
       "end_pos": 10,
       "bold": True
   }
   ```

## 优势

### 1. 提示词优化
- 主 Agent 的提示词不会因为大量 Word 工具而变得过长
- Word 子 Agent 有专门的提示词，专注于 Word 任务

### 2. 职责分离
- 主 Agent 负责一般任务和任务分发
- Word 子 Agent 专门处理 Word 相关任务
- Word MCP Server 提供底层工具

### 3. 可扩展性
- 可以轻松添加其他专门的子 Agent（如 Excel、PowerPoint 等）
- 每个子 Agent 都有自己的 LLM 和专门领域

### 4. 统一管理
- 所有 Agent 通过 AgentManager 统一管理
- 使用统一的 API 配置
- 支持动态注册和发现

## 故障排除

### 1. Word MCP 服务未找到

**问题**: `Word MCP服务未找到或未正确注册`

**解决方案**:
1. 检查 `agent-manifest.json` 配置是否正确
2. 确保 Word MCP Server 已正确安装
3. 检查 MCP 注册表是否正确扫描

### 2. Word 子 Agent 初始化失败

**问题**: `Word子Agent不支持handle_handoff方法`

**解决方案**:
1. 检查 `WordAgent` 类是否正确实现 `handle_handoff` 方法
2. 确保 `entryPoint` 配置指向正确的模块和类

### 3. API 调用失败

**问题**: `LLM客户端未初始化`

**解决方案**:
1. 检查 `config.py` 中的 API 配置
2. 确保 API 密钥和基础 URL 正确
3. 检查网络连接

### 4. 工具调用失败

**问题**: `Word MCP服务不支持动作: xxx`

**解决方案**:
1. 检查工具名称是否正确
2. 确保 Word MCP Server 已注册该工具
3. 查看工具参数是否正确

## 使用示例

### 1. 创建文档并添加内容

```python
# 通过 AgentManager 调用
agent_manager = get_agent_manager()

# 创建文档
result1 = await agent_manager.call_agent("any_agent", 
    "请创建一个名为report.docx的文档，标题为项目报告")

# 添加标题
result2 = await agent_manager.call_agent("any_agent", 
    "请在report.docx文档中添加一个一级标题：项目概述")

# 添加段落
result3 = await agent_manager.call_agent("any_agent", 
    "请在report.docx文档中添加一个段落：这是项目概述的内容。")
```

### 2. 直接使用 Word 子 Agent

```python
from mcpserver.word_agent.word_agent import WordAgent

word_agent = WordAgent()

# 直接调用工具
result = await word_agent.call_tool("create_document", 
                                   filename="test.docx", 
                                   title="测试文档")

# 获取可用工具
tools = word_agent.get_available_tools()
print(f"可用工具: {tools}")
```

## 总结

这个集成方案成功地将 Office Word MCP Server 作为独立的子 Agent 集成到多 Agent 系统中，实现了：

1. **模块化设计** - 每个组件职责明确
2. **提示词优化** - 避免主 Agent 提示词过长
3. **统一管理** - 通过 AgentManager 统一管理所有 Agent
4. **可扩展性** - 易于添加其他专门的子 Agent
5. **标准化接口** - 使用标准的 MCP 协议和 Agent 接口

通过这种设计，系统既保持了功能的完整性，又实现了良好的架构分离和可维护性。 