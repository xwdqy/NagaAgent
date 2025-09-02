"""voice 包初始化：请从 voice.input.* 与 voice.output.* 导入具体模块"""

# 语音输入相关导入 #
from .input.integration import (
    get_voice_integration,
    start_voice_listening,
    stop_voice_listening,
    is_voice_active
)

# 语音输出相关导入 #
from .output.voice_integration import get_voice_integration as get_tts_integration

__all__ = [
    "get_voice_integration",      # 语音输入集成 #
    "start_voice_listening",      # 启动语音监听 #
    "stop_voice_listening",       # 停止语音监听 #
    "is_voice_active",            # 检查语音状态 #
    "get_tts_integration"         # TTS集成（兼容性） #
]


