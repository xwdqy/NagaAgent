#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
语音输入功能测试脚本
测试Windows Speech API的语音识别功能
"""
import sys
import time
import logging
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_windows_speech_import():
    """测试Windows Speech API导入"""
    print("🔍 测试Windows Speech API导入...")
    
    try:
        import winrt.windows.media.speechrecognition as speechrecognition
        import winrt.windows.foundation as foundation
        import winrt.windows.globalization as globalization
        print("✅ Windows Speech API导入成功")
        return True
    except ImportError as e:
        print(f"❌ Windows Speech API导入失败: {e}")
        return False

def test_speech_input_module():
    """测试语音输入模块"""
    print("\n🔍 测试语音输入模块...")
    
    try:
        from speech_input import get_speech_input_manager, WindowsSpeechInput
        print("✅ 语音输入模块导入成功")
        
        # 测试WindowsSpeechInput类
        speech_input = WindowsSpeechInput()
        print(f"✅ WindowsSpeechInput实例创建成功")
        print(f"   可用性: {speech_input.is_available()}")
        print(f"   状态: {speech_input.get_status()}")
        
        return True
    except Exception as e:
        print(f"❌ 语音输入模块测试失败: {e}")
        return False

def test_speech_recognition():
    """测试语音识别功能"""
    print("\n🔍 测试语音识别功能...")
    
    try:
        from speech_input import get_speech_input_manager
        
        # 获取语音输入管理器
        manager = get_speech_input_manager()
        print(f"✅ 语音输入管理器获取成功")
        print(f"   可用性: {manager.is_available()}")
        print(f"   状态: {manager.get_status()}")
        
        if not manager.is_available():
            print("❌ 语音输入不可用，跳过识别测试")
            return False
        
        # 定义回调函数
        def on_text_received(text: str):
            print(f"🎤 识别到语音: {text}")
        
        def on_error_received(error: str):
            print(f"❌ 语音识别错误: {error}")
        
        def on_status_changed(status: dict):
            print(f"📊 状态变化: {status}")
        
        # 开始语音监听
        print("🎤 开始语音监听测试...")
        print("   请说话进行测试，按Ctrl+C停止")
        
        if manager.start_listening(on_text_received, on_error_received, on_status_changed):
            print("✅ 语音监听启动成功")
            
            try:
                # 运行30秒进行测试
                for i in range(30):
                    time.sleep(1)
                    if i % 10 == 0:
                        print(f"⏰ 测试进行中... {30-i}秒后自动停止")
            except KeyboardInterrupt:
                print("\n⏹️ 用户中断测试")
            finally:
                manager.stop_listening()
                print("✅ 语音监听已停止")
        else:
            print("❌ 语音监听启动失败")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ 语音识别测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🎤 语音输入功能测试开始")
    print("=" * 50)
    
    # 测试1: Windows Speech API导入
    if not test_windows_speech_import():
        print("\n❌ Windows Speech API导入失败，测试终止")
        return
    
    # 测试2: 语音输入模块
    if not test_speech_input_module():
        print("\n❌ 语音输入模块测试失败，测试终止")
        return
    
    # 测试3: 语音识别功能
    if not test_speech_recognition():
        print("\n❌ 语音识别功能测试失败")
        return
    
    print("\n" + "=" * 50)
    print("🎉 所有测试完成！")

if __name__ == "__main__":
    main()
