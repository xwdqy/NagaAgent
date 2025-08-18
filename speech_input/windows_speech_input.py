#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Windows语音输入模块 - 基于Windows Runtime Speech APIs
支持实时语音识别和语音转文本功能
"""
import asyncio
import logging
import threading
import time
from typing import Optional, Callable, Dict, Any
import sys
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import config

logger = logging.getLogger("WindowsSpeechInput")

try:
    import winrt.windows.media.speechrecognition as speechrecognition
    import winrt.windows.foundation as foundation
    import winrt.windows.globalization as globalization
    WINDOWS_SPEECH_AVAILABLE = True
except ImportError:
    logger.warning("Windows Speech Runtime不可用，请确保在Windows 10/11环境下运行")
    WINDOWS_SPEECH_AVAILABLE = False

class WindowsSpeechInput:
    """Windows语音输入类 - 基于Windows Runtime Speech APIs"""
    
    def __init__(self):
        self.speech_recognizer = None
        self.is_listening = False
        self.is_initialized = False
        self.on_text_callback = None
        self.on_error_callback = None
        self.current_language = "zh-CN"  # 默认中文
        
        # 语音识别配置
        self.recognition_config = {
            "language": "zh-CN",
            "continuous": True,  # 连续识别
            "timeout": 30,  # 超时时间（秒）
            "confidence_threshold": 0.7  # 置信度阈值
        }
        
        if WINDOWS_SPEECH_AVAILABLE:
            self._init_speech_recognizer()
        else:
            logger.error("Windows Speech Runtime不可用")
    
    def _init_speech_recognizer(self):
        """初始化语音识别器"""
        try:
            # 创建语言对象
            language = globalization.Language(self.recognition_config["language"])
            
            # 创建语音识别器
            self.speech_recognizer = speechrecognition.SpeechRecognizer(language)
            
            # 设置识别模式
            self.speech_recognizer.continuous_recognition_session.auto_stop_silence_timeout = foundation.TimeSpan.from_seconds(3)
            
            # 绑定事件处理器
            self.speech_recognizer.continuous_recognition_session.result_received += self._on_result_received
            self.speech_recognizer.continuous_recognition_session.completed += self._on_recognition_completed
            
            self.is_initialized = True
            logger.info("Windows语音识别器初始化成功")
            
        except Exception as e:
            logger.error(f"初始化语音识别器失败: {e}")
            self.is_initialized = False
    
    def _on_result_received(self, sender, args):
        """处理语音识别结果"""
        try:
            if args.result.confidence >= self.recognition_config["confidence_threshold"]:
                recognized_text = args.result.text
                logger.info(f"识别到文本: {recognized_text}")
                
                if self.on_text_callback:
                    # 在新线程中调用回调函数
                    threading.Thread(
                        target=self.on_text_callback,
                        args=(recognized_text,),
                        daemon=True
                    ).start()
            else:
                logger.debug(f"识别置信度过低: {args.result.confidence}")
                
        except Exception as e:
            logger.error(f"处理识别结果时出错: {e}")
    
    def _on_recognition_completed(self, sender, args):
        """处理识别完成事件"""
        try:
            if args.status != speechrecognition.SpeechRecognitionResultStatus.SUCCESS:
                error_msg = f"语音识别失败: {args.status}"
                logger.warning(error_msg)
                
                if self.on_error_callback:
                    threading.Thread(
                        target=self.on_error_callback,
                        args=(error_msg,),
                        daemon=True
                    ).start()
                    
        except Exception as e:
            logger.error(f"处理识别完成事件时出错: {e}")
    
    def start_listening(self, on_text: Callable[[str], None] = None, 
                       on_error: Callable[[str], None] = None):
        """开始语音监听"""
        if not self.is_initialized:
            logger.error("语音识别器未初始化")
            return False
        
        if self.is_listening:
            logger.warning("已经在监听中")
            return True
        
        try:
            # 设置回调函数
            if on_text:
                self.on_text_callback = on_text
            if on_error:
                self.on_error_callback = on_error
            
            # 开始连续识别
            self.speech_recognizer.continuous_recognition_session.start_async()
            self.is_listening = True
            
            logger.info("开始语音监听")
            return True
            
        except Exception as e:
            logger.error(f"开始语音监听失败: {e}")
            return False
    
    def stop_listening(self):
        """停止语音监听"""
        if not self.is_listening:
            return
        
        try:
            self.speech_recognizer.continuous_recognition_session.stop_async()
            self.is_listening = False
            logger.info("停止语音监听")
            
        except Exception as e:
            logger.error(f"停止语音监听失败: {e}")
    
    def set_language(self, language_code: str):
        """设置识别语言"""
        try:
            # 重新初始化识别器
            if self.is_listening:
                self.stop_listening()
            
            self.recognition_config["language"] = language_code
            self._init_speech_recognizer()
            
            logger.info(f"设置识别语言为: {language_code}")
            
        except Exception as e:
            logger.error(f"设置语言失败: {e}")
    
    def get_supported_languages(self) -> list:
        """获取支持的语言列表"""
        try:
            languages = speechrecognition.SpeechRecognizer.supported_topic_languages
            return [lang.language_tag for lang in languages]
        except Exception as e:
            logger.error(f"获取支持语言失败: {e}")
            return ["zh-CN", "en-US"]  # 默认返回
    
    def is_available(self) -> bool:
        """检查语音识别是否可用"""
        return WINDOWS_SPEECH_AVAILABLE and self.is_initialized
    
    def get_status(self) -> Dict[str, Any]:
        """获取当前状态"""
        return {
            "available": self.is_available(),
            "listening": self.is_listening,
            "language": self.recognition_config["language"],
            "initialized": self.is_initialized
        }

# 使用示例
if __name__ == "__main__":
    def on_text_received(text: str):
        print(f"收到语音输入: {text}")
    
    def on_error_received(error: str):
        print(f"语音识别错误: {error}")
    
    # 创建语音输入实例
    speech_input = WindowsSpeechInput()
    
    if speech_input.is_available():
        # 开始监听
        speech_input.start_listening(on_text_received, on_error_received)
        
        try:
            print("正在监听语音输入，按Ctrl+C停止...")
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            speech_input.stop_listening()
            print("停止语音监听")
    else:
        print("语音识别不可用")
