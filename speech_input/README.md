# 语音输入模块 🎤

## 概述

语音输入模块是NagaAgent的独立语音识别功能模块，基于Windows Runtime Speech APIs，提供高质量的语音识别功能。

## 目录结构

```
speech_input/
├── __init__.py                    # 模块初始化文件
├── README.md                      # 本文件
├── SPEECH_INPUT_GUIDE.md          # 详细使用指南
├── speech_input_manager.py        # 语音输入管理器（主要接口）
└── windows_speech_input.py        # Windows Speech API实现
```

## 快速开始

### 1. 导入模块

```python
# 导入整个模块
import speech_input

# 或者导入特定功能
from speech_input import get_speech_input_manager, start_speech_listening
```

### 2. 基本使用

```python
from speech_input import get_speech_input_manager

# 获取语音输入管理器
manager = get_speech_input_manager()

# 定义回调函数
def on_text_received(text: str):
    print(f"收到语音输入: {text}")

def on_error_received(error: str):
    print(f"语音识别错误: {error}")

# 开始语音监听
if manager.start_listening(on_text_received, on_error_received):
    print("语音监听已启动")
else:
    print("启动语音监听失败")

# 停止语音监听
manager.stop_listening()
```

### 3. 便捷函数使用

```python
from speech_input import start_speech_listening, stop_speech_listening

# 开始监听
start_speech_listening(
    on_text=lambda text: print(f"语音: {text}"),
    on_error=lambda error: print(f"错误: {error}")
)

# 停止监听
stop_speech_listening()
```

## 支持的语音识别方案

### Windows Speech API
- Windows 11原生支持
- 无需额外配置
- 完全免费
- 高精度识别
- 支持多种语言

## 配置

在 `config.json` 中添加语音输入配置：

```json
{
  "speech_input": {
    "enabled": true,
    "auto_start": false,
    "language": "zh-CN",
    "confidence_threshold": 0.7,
    "timeout": 30,
    "continuous": true
  }
}
```

## 依赖

主要依赖包括：
- `winrt>=1.0.21033.1` - Windows Runtime支持

## 详细文档

更多详细信息请参考：
- [SPEECH_INPUT_GUIDE.md](SPEECH_INPUT_GUIDE.md) - 完整使用指南
- [故障排除](SPEECH_INPUT_GUIDE.md#故障排除) - 常见问题解决方案

## 版本信息

- 版本：1.0.0
- 作者：NagaAgent Team
- 许可证：GNU GPL v3.0
