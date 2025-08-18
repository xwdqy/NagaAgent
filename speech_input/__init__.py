#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
语音输入模块 - NagaAgent语音输入功能
基于Windows Runtime Speech APIs的语音识别模块
"""

from .speech_input_manager import (
    get_speech_input_manager,
    start_speech_listening,
    stop_speech_listening,
    get_speech_status,
    SpeechInputManager
)

from .windows_speech_input import WindowsSpeechInput

__version__ = "1.0.0"
__author__ = "NagaAgent Team"

__all__ = [
    "get_speech_input_manager",
    "start_speech_listening", 
    "stop_speech_listening",
    "get_speech_status",
    "SpeechInputManager",
    "WindowsSpeechInput"
]
