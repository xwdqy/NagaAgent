#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
语音输入管理器 - 集成到NagaAgent主系统
支持多种语音识别方案，提供统一的语音输入接口
"""
import asyncio
import logging
import threading
import time
from typing import Optional, Callable, Dict, Any, List
import sys
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import config

logger = logging.getLogger("SpeechInputManager")

# 导入语音输入模块
try:
    from .windows_speech_input import WindowsSpeechInput
    SPEECH_MODULES_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Windows Speech模块导入失败: {e}")
    SPEECH_MODULES_AVAILABLE = False

class SpeechInputManager:
    """语音输入管理器 - 统一管理所有语音输入功能"""
    
    def __init__(self):
        self.windows_speech = None
        self.current_provider = None
        self.is_listening = False
        
        # 回调函数
        self.on_text_received = None
        self.on_error_received = None
        self.on_status_changed = None
        
        # 初始化语音输入提供者
        self._init_speech_providers()
        
        # 语音输入配置
        self.speech_config = {
            "enabled": True,
            "auto_start": False,
            "language": "zh-CN",
            "confidence_threshold": 0.7,
            "timeout": 30,
            "continuous": True
        }
        
        # 从配置文件加载设置
        self._load_config()
    
    def _init_speech_providers(self):
        """初始化语音输入提供者"""
        if not SPEECH_MODULES_AVAILABLE:
            logger.warning("Windows Speech模块不可用")
            return
        
        try:
            # 初始化Windows Speech输入
            self.windows_speech = WindowsSpeechInput()
            if self.windows_speech.is_available():
                self.current_provider = self.windows_speech
                logger.info("Windows Speech输入初始化成功")
                return
        except Exception as e:
            logger.warning(f"Windows Speech输入初始化失败: {e}")
        
        logger.error("Windows Speech输入不可用")
    
    def _load_config(self):
        """从配置文件加载语音输入设置"""
        try:
            if hasattr(config, 'speech_input'):
                self.speech_config.update(config.speech_input)
                logger.info("语音输入配置加载成功")
        except Exception as e:
            logger.warning(f"加载语音输入配置失败: {e}")
    
    def start_listening(self, on_text: Callable[[str], None] = None,
                       on_error: Callable[[str], None] = None,
                       on_status: Callable[[Dict[str, Any]], None] = None) -> bool:
        """开始语音监听"""
        if not self.current_provider:
            logger.error("没有可用的语音输入提供者")
            return False
        
        if self.is_listening:
            logger.warning("已经在监听中")
            return True
        
        # 设置回调函数
        self.on_text_received = on_text
        self.on_error_received = on_error
        self.on_status_changed = on_status
        
        # 开始监听
        success = self.current_provider.start_listening(
            self._on_text_received,
            self._on_error_received
        )
        
        if success:
            self.is_listening = True
            self._notify_status_change()
            logger.info("语音监听已启动")
        
        return success
    
    def stop_listening(self):
        """停止语音监听"""
        if not self.is_listening:
            return
        
        if self.current_provider:
            self.current_provider.stop_listening()
        
        self.is_listening = False
        self._notify_status_change()
        logger.info("语音监听已停止")
    
    def _on_text_received(self, text: str):
        """处理接收到的文本"""
        if text and text.strip():
            logger.info(f"语音识别结果: {text}")
            
            # 调用用户回调函数
            if self.on_text_received:
                try:
                    self.on_text_received(text)
                except Exception as e:
                    logger.error(f"处理语音文本时出错: {e}")
    
    def _on_error_received(self, error: str):
        """处理识别错误"""
        logger.warning(f"语音识别错误: {error}")
        
        # 调用用户回调函数
        if self.on_error_received:
            try:
                self.on_error_received(error)
            except Exception as e:
                logger.error(f"处理语音错误时出错: {e}")
    
    def _notify_status_change(self):
        """通知状态变化"""
        if self.on_status_changed:
            try:
                status = self.get_status()
                self.on_status_changed(status)
            except Exception as e:
                logger.error(f"通知状态变化时出错: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """获取当前状态"""
        status = {
            "listening": self.is_listening,
            "enabled": self.speech_config["enabled"],
            "provider": None,
            "available_providers": []
        }
        
        if self.current_provider:
            if hasattr(self.current_provider, 'get_status'):
                status["provider"] = self.current_provider.get_status()
            else:
                status["provider"] = self.current_provider.__class__.__name__
        
        # 获取可用提供者列表
        if self.windows_speech and self.windows_speech.is_available():
            status["available_providers"].append("Windows Speech")
        
        return status
    
    def switch_provider(self, provider_name: str) -> bool:
        """切换语音输入提供者"""
        if provider_name == "Windows Speech" and self.windows_speech and self.windows_speech.is_available():
            if self.is_listening:
                self.stop_listening()
            self.current_provider = self.windows_speech
            logger.info("切换到Windows Speech提供者")
            return True
        
        logger.warning(f"未找到提供者: {provider_name}")
        return False
    
    def set_language(self, language_code: str) -> bool:
        """设置识别语言"""
        try:
            if self.current_provider and hasattr(self.current_provider, 'set_language'):
                success = self.current_provider.set_language(language_code)
                if success:
                    self.speech_config["language"] = language_code
                    logger.info(f"设置识别语言为: {language_code}")
                return success
        except Exception as e:
            logger.error(f"设置语言失败: {e}")
        
        return False
    
    def get_supported_languages(self) -> List[str]:
        """获取支持的语言列表"""
        try:
            if self.current_provider and hasattr(self.current_provider, 'get_supported_languages'):
                return self.current_provider.get_supported_languages()
        except Exception as e:
            logger.error(f"获取支持语言失败: {e}")
        
        # 默认返回常用语言
        return ["zh-CN", "en-US", "ja-JP", "ko-KR"]
    
    def is_available(self) -> bool:
        """检查语音输入是否可用"""
        return self.windows_speech and self.windows_speech.is_available()
    
    def get_config(self) -> Dict[str, Any]:
        """获取配置"""
        return self.speech_config.copy()
    
    def update_config(self, new_config: Dict[str, Any]):
        """更新配置"""
        self.speech_config.update(new_config)
        logger.info("语音输入配置已更新")

# 全局语音输入管理器实例
_speech_input_manager = None

def get_speech_input_manager() -> SpeechInputManager:
    """获取全局语音输入管理器实例"""
    global _speech_input_manager
    if _speech_input_manager is None:
        _speech_input_manager = SpeechInputManager()
    return _speech_input_manager

# 便捷函数
def start_speech_listening(on_text: Callable[[str], None] = None,
                          on_error: Callable[[str], None] = None,
                          on_status: Callable[[Dict[str, Any]], None] = None) -> bool:
    """开始语音监听"""
    manager = get_speech_input_manager()
    return manager.start_listening(on_text, on_error, on_status)

def stop_speech_listening():
    """停止语音监听"""
    manager = get_speech_input_manager()
    manager.stop_listening()

def get_speech_status() -> Dict[str, Any]:
    """获取语音输入状态"""
    manager = get_speech_input_manager()
    return manager.get_status()

# 使用示例
if __name__ == "__main__":
    def on_text_received(text: str):
        print(f"收到语音输入: {text}")
    
    def on_error_received(error: str):
        print(f"语音识别错误: {error}")
    
    def on_status_changed(status: Dict[str, Any]):
        print(f"状态变化: {status}")
    
    # 获取语音输入管理器
    manager = get_speech_input_manager()
    
    # 检查可用性
    if manager.is_available():
        print("语音输入可用")
        print(f"当前状态: {manager.get_status()}")
        
        # 开始监听
        if manager.start_listening(on_text_received, on_error_received, on_status_changed):
            print("开始语音监听，按Ctrl+C停止...")
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                manager.stop_listening()
                print("停止语音监听")
        else:
            print("启动语音监听失败")
    else:
        print("语音输入不可用")
