#!/usr/bin/env python3
"""
WebSockets依赖升级脚本
修复websockets.legacy弃用警告
"""

import subprocess
import sys
import os

def run_command(command):
    """运行命令并返回结果"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=True)
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr

def upgrade_websockets():
    """升级websockets相关依赖"""
    print("🔧 开始升级WebSockets相关依赖...")
    
    # 升级websockets到最新版本
    print("📦 升级websockets...")
    success, output = run_command("pip install --upgrade websockets>=12.0")
    if success:
        print("✅ websockets升级成功")
    else:
        print(f"❌ websockets升级失败: {output}")
    
    # 升级uvicorn到最新版本
    print("📦 升级uvicorn...")
    success, output = run_command("pip install --upgrade 'uvicorn[standard]>=0.35.0'")
    if success:
        print("✅ uvicorn升级成功")
    else:
        print(f"❌ uvicorn升级失败: {output}")
    
    # 清理缓存
    print("🧹 清理pip缓存...")
    run_command("pip cache purge")
    
    print("🎉 WebSockets依赖升级完成！")
    print("💡 现在可以重新启动服务，弃用警告应该已经消失")

if __name__ == "__main__":
    upgrade_websockets()
