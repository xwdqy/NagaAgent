# Office-Word-MCP-Server
对 `Office-Word-MCP-Server-main`（Word MCP）目录结构和各子文件夹/脚本的功能做详细解读如下：

---

## 顶层结构

```
Office-Word-MCP-Server-main/
├── word_document_server/      # Word文档操作的主功能模块
├── office_word_mcp_server/    # 入口包装，便于MCP集成
├── requirements.txt           # 依赖包
├── pyproject.toml             # 构建配置
├── setup_mcp.py               # 一键安装/配置脚本
├── mcp-config.json            # MCP服务配置
├── README.md                  # 项目说明
├── Dockerfile                 # 容器化支持
└── ...（其他辅助文件）
```

---

## 1. `word_document_server/`  —— **Word文档操作核心模块**

### 主要作用
- 实现所有Word文档的创建、编辑、内容提取、格式化、保护等功能
- 以“工具函数”方式暴露，供MCP主服务注册为工具

### 主要子模块及功能

#### `core/`
- **footnotes.py**：脚注/尾注的插入、转换、查找、格式化
- **protection.py**：文档保护（加密、签名、限制编辑、验证等）
- **styles.py**：样式管理（标题、表格、段落、字体等自定义样式）
- **tables.py**：表格操作（边框、样式、复制等）
- **unprotect.py**：解除文档保护
- **__init__.py**：包初始化

#### `tools/`
- **content_tools.py**：内容添加（标题、段落、表格、图片、分页符、目录等）
- **document_tools.py**：文档级操作（创建、复制、合并、获取信息、提取文本/结构/大纲、列出文档等）
- **extended_document_tools.py**：扩展功能（获取指定段落、查找文本、转PDF等）
- **footnote_tools.py**：脚注/尾注相关的高级操作
- **format_tools.py**：文本/表格格式化（加粗、颜色、样式、表格美化等）
- **protection_tools.py**：文档保护相关的工具（加密、签名、验证、解除保护等）
- **__init__.py**：包初始化

#### `utils/`
- **document_utils.py**：文档属性、结构、文本提取、查找替换等底层工具
- **extended_document_utils.py**：段落文本、查找等扩展底层工具
- **file_utils.py**：文件操作（可写性检测、复制、扩展名处理等）
- **__init__.py**：包初始化

#### 其他
- **main.py**：MCP服务主入口，注册所有工具，定义MCP协议接口，启动服务
- **__init__.py**：包初始化

---

## 2. `office_word_mcp_server/`  —— **MCP服务包装**

- **__init__.py**：导入并暴露 `word_document_server.main.run_server`，作为MCP服务的标准入口，便于通过 `python -m` 或 MCP协议直接启动。

---

## 3. 其他顶层文件

- **requirements.txt**：依赖包列表（如 `python-docx`, `fastmcp` 等）
- **pyproject.toml**：构建和元数据配置
- **setup_mcp.py**：一键安装/配置脚本，支持虚拟环境、依赖安装、MCP配置生成等
- **mcp-config.json**：MCP服务配置文件，描述如何以MCP协议启动本服务
- **Dockerfile**：容器化部署支持
- **README.md**：详细的功能说明、用法、API文档等

---

## 4. 主要功能一览（通过各脚本实现）

- **文档管理**：创建、复制、合并、列出、获取信息、转PDF
- **内容添加**：标题、段落、表格、图片、分页符、目录
- **内容提取**：全文、指定段落、结构、大纲、查找文本
- **文本格式化**：加粗、斜体、下划线、颜色、字体、样式
- **表格格式化**：边框、底纹、表头、样式
- **脚注/尾注**：插入、转换、查找、格式化
- **文档保护**：加密、限制编辑、数字签名、验证、解除保护
- **文件操作**：可写性检测、复制、扩展名处理
- **MCP协议**：所有功能以MCP工具形式暴露，支持标准MCP客户端调用

---

## 5. 典型调用方式

- 通过 MCP 工具调用，如 `create_document`, `add_paragraph`, `add_footnote_to_document`, `protect_document`, `convert_to_pdf` 等
- 每个工具函数都可单独被MCP客户端（如Claude Desktop、API等）远程调用，实现自动化文档处理

---

## 总结

- **word_document_server/**：Word文档所有底层与高级操作的实现
- **office_word_mcp_server/**：MCP服务标准入口包装
- **setup_mcp.py**：一键安装与配置
- **main.py**：MCP服务主入口，注册所有工具
- **每个子文件夹/脚本都围绕Word文档的不同操作场景设计，功能极其丰富，支持自动化、批量、远程文档处理**

[![smithery badge](https://smithery.ai/badge/@GongRzhe/Office-Word-MCP-Server)](https://smithery.ai/server/@GongRzhe/Office-Word-MCP-Server)

一个用于创建、读取和操作Microsoft Word文档的模型上下文协议(MCP)服务器。该服务器使AI助手能够通过标准化接口处理Word文档，提供丰富的文档编辑功能。

<a href="https://glama.ai/mcp/servers/@GongRzhe/Office-Word-MCP-Server">
  <img width="380" height="200" src="https://glama.ai/mcp/servers/@GongRzhe/Office-Word-MCP-Server/badge" alt="Office Word Server MCP server" />
</a>

![](https://badge.mcpx.dev?type=server "MCP Server")

## 概述

Office-Word-MCP-Server实现了[模型上下文协议](https://modelcontextprotocol.io/)，将Word文档操作作为工具和资源暴露出来。它作为AI助手和Microsoft Word文档之间的桥梁，允许文档创建、内容添加、格式化和分析。

该服务器采用模块化架构，将关注点分离为核心功能、工具和实用程序，使其高度可维护且可扩展，便于未来增强。

### 示例

#### 提示

![image](https://github.com/user-attachments/assets/f49b0bcc-88b2-4509-bf50-995b9a40038c)

#### 输出

![image](https://github.com/user-attachments/assets/ff64385d-3822-4160-8cdf-f8a484ccc01a)

## 功能特性

### 文档管理

- 创建带有元数据的新Word文档
- 提取文本并分析文档结构
- 查看文档属性和统计信息
- 列出目录中可用的文档
- 创建现有文档的副本
- 将多个文档合并为单个文档
- 将Word文档转换为PDF格式

### 内容创建

- 添加不同级别的标题
- 插入带有可选样式的段落
- 创建带有自定义数据的表格
- 添加具有比例缩放的图片
- 插入分页符
- 向文档添加脚注和尾注
- 将脚注转换为尾注
- 自定义脚注和尾注样式

### 富文本格式化

- 格式化特定文本段落（粗体、斜体、下划线）
- 更改文本颜色和字体属性
- 将自定义样式应用于文本元素
- 在文档中搜索和替换文本

### 表格格式化

- 使用边框和样式格式化表格
- 创建具有不同格式的表头行
- 应用单元格底纹和自定义边框
- 构建表格以提高可读性

### 高级文档操作

- 删除段落
- 创建自定义文档样式
- 在整个文档中应用一致的格式
- 对特定范围的文本进行详细控制的格式化

### 文档保护

- 为文档添加密码保护
- 实现带有可编辑区域的限制编辑
- 为文档添加数字签名
- 验证文档的真实性和完整性

## 安装

### 通过Smithery安装

要通过[Smithery](https://smithery.ai/server/@GongRzhe/Office-Word-MCP-Server)为Claude Desktop自动安装Office Word文档服务器：

```bash
npx -y @smithery/cli install @GongRzhe/Office-Word-MCP-Server --client claude
```

### 前置要求

- Python 3.8或更高版本
- pip包管理器

### 基本安装

```bash
# 克隆仓库
git clone https://github.com/GongRzhe/Office-Word-MCP-Server.git
cd Office-Word-MCP-Server

# 安装依赖
pip install -r requirements.txt
```

### 使用安装脚本

或者，您可以使用提供的安装脚本，它会处理：

- 检查前置要求
- 设置虚拟环境
- 安装依赖
- 生成MCP配置

```bash
python setup_mcp.py
```

## 与Claude Desktop的使用

### 配置

#### 方法1：本地安装后

1. 安装后，将服务器添加到您的Claude Desktop配置文件中：

```json
{
  "mcpServers": {
    "word-document-server": {
      "command": "python",
      "args": ["/path/to/word_mcp_server.py"]
    }
  }
}
```

#### 方法2：无需安装（使用uvx）

1. 您也可以通过使用uvx包管理器配置Claude Desktop使用服务器，而无需本地安装：

```json
{
  "mcpServers": {
    "word-document-server": {
      "command": "uvx",
      "args": ["--from", "office-word-mcp-server", "word_mcp_server"]
    }
  }
}
```

2. 配置文件位置：

   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`

3. 重启Claude Desktop以加载配置。

### 示例操作

配置完成后，您可以要求Claude执行以下操作：

- "创建一个名为'report.docx'的新文档，包含标题页"
- "向我的文档添加标题和三个段落"
- "插入一个4x4的销售数据表格"
- "将第2段中的'important'一词格式化为粗体和红色"
- "搜索并替换所有'old term'实例为'new term'"
- "为章节标题创建自定义样式"
- "对文档中的表格应用格式化"

## API参考

### 文档创建和属性

```python
create_document(filename, title=None, author=None)
get_document_info(filename)
get_document_text(filename)
get_document_outline(filename)
list_available_documents(directory=".")
copy_document(source_filename, destination_filename=None)
convert_to_pdf(filename, output_filename=None)
```

### 内容添加

```python
add_heading(filename, text, level=1)
add_paragraph(filename, text, style=None)
add_table(filename, rows, cols, data=None)
add_picture(filename, image_path, width=None)
add_page_break(filename)
```

### 内容提取

```python
get_document_text(filename)
get_paragraph_text_from_document(filename, paragraph_index)
find_text_in_document(filename, text_to_find, match_case=True, whole_word=False)
```

### 文本格式化

```python
format_text(filename, paragraph_index, start_pos, end_pos, bold=None,
            italic=None, underline=None, color=None, font_size=None, font_name=None)
search_and_replace(filename, find_text, replace_text)
delete_paragraph(filename, paragraph_index)
create_custom_style(filename, style_name, bold=None, italic=None,
                    font_size=None, font_name=None, color=None, base_style=None)
```

### 表格格式化

```python
format_table(filename, table_index, has_header_row=None,
             border_style=None, shading=None)
```

## 故障排除

### 常见问题

1. **缺少样式**

   - 某些文档可能缺少标题和表格操作所需的样式
   - 服务器将尝试创建缺少的样式或使用直接格式化
   - 为获得最佳结果，请使用具有标准Word样式的模板

2. **权限问题**

   - 确保服务器有权读取/写入文档路径
   - 使用`copy_document`函数创建锁定文档的可编辑副本
   - 如果操作失败，请检查文件所有权和权限

3. **图片插入问题**
   - 对图片文件使用绝对路径
   - 验证图片格式兼容性（推荐JPEG、PNG）
   - 检查图片文件大小和权限

### 调试

通过设置环境变量启用详细日志记录：

```bash
export MCP_DEBUG=1  # Linux/macOS
set MCP_DEBUG=1     # Windows
```

## 贡献

欢迎贡献！请随时提交Pull Request。

1. Fork仓库
2. 创建您的功能分支（`git checkout -b feature/amazing-feature`）
3. 提交您的更改（`git commit -m 'Add some amazing feature'`）
4. 推送到分支（`git push origin feature/amazing-feature`）
5. 打开Pull Request

## 许可证

本项目采用MIT许可证 - 详情请参阅LICENSE文件。

## 致谢

- [模型上下文协议](https://modelcontextprotocol.io/)提供协议规范
- [python-docx](https://python-docx.readthedocs.io/)提供Word文档操作
- [FastMCP](https://github.com/modelcontextprotocol/python-sdk)提供Python MCP实现

---

_注意：此服务器与您系统上的文档文件交互。在Claude Desktop或其他MCP客户端中确认请求的操作之前，请始终验证这些操作是否合适。_
