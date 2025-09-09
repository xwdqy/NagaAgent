#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统环境检测模块
检测Python版本、虚拟环境、依赖包等系统环境
"""

import os
import sys
import subprocess
import importlib
import platform
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional

class SystemChecker:
    """系统环境检测器"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent  # 指向项目根目录
        self.venv_path = self.project_root / ".venv"
        self.requirements_file = self.project_root / "requirements.txt"
        self.config_file = self.project_root / "config.json"
        self.results = {}
        
    def check_all(self) -> Dict[str, bool]:
        """执行所有检测项目"""
        print("🔍 开始系统环境检测...")
        print("=" * 50)
        
        checks = [
            ("Python版本", self.check_python_version),
            ("虚拟环境", self.check_virtual_environment),
            ("依赖文件", self.check_requirements_file),
            ("核心依赖", self.check_core_dependencies),
            ("可选依赖", self.check_optional_dependencies),
            ("配置文件", self.check_config_files),
            ("目录结构", self.check_directory_structure),
            ("权限检查", self.check_permissions)
        ]
        
        all_passed = True
        for name, check_func in checks:
            print(f"📋 检测 {name}...")
            try:
                result = check_func()
                self.results[name] = result
                if result:
                    print(f"✅ {name}: 通过")
                else:
                    print(f"❌ {name}: 失败")
                    all_passed = False
            except Exception as e:
                print(f"⚠️ {name}: 检测异常 - {e}")
                self.results[name] = False
                all_passed = False
            print()
        
        print("=" * 50)
        if all_passed:
            print("🎉 系统环境检测全部通过！")
        else:
            print("⚠️ 系统环境检测发现问题，请查看上述信息")
        
        return self.results
    
    def check_python_version(self) -> bool:
        """检测Python版本"""
        version = sys.version_info
        print(f"   当前Python版本: {version.major}.{version.minor}.{version.micro}")
        
        # 要求Python 3.8+
        if version.major < 3 or (version.major == 3 and version.minor < 8):
            print(f"   ❌ Python版本过低，需要3.8+，当前{version.major}.{version.minor}")
            return False
        
        print(f"   ✅ Python版本符合要求")
        return True
    
    def check_virtual_environment(self) -> bool:
        """检测虚拟环境"""
        # 检查是否在虚拟环境中
        in_venv = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
        
        if not in_venv:
            print(f"   ⚠️ 未检测到虚拟环境")
            print(f"   建议使用虚拟环境运行项目")
            
            # 检查是否存在.venv目录
            if self.venv_path.exists():
                print(f"   📁 发现.venv目录: {self.venv_path}")
                print(f"   💡 请运行: .venv\\Scripts\\activate (Windows) 或 source .venv/bin/activate (Linux/Mac)")
                return False
            else:
                print(f"   💡 建议创建虚拟环境: python -m venv .venv")
                return False
        
        print(f"   ✅ 虚拟环境: {sys.prefix}")
        return True
    
    def check_requirements_file(self) -> bool:
        """检测依赖文件"""
        if not self.requirements_file.exists():
            print(f"   ❌ 未找到requirements.txt文件: {self.requirements_file}")
            return False
        
        print(f"   ✅ 依赖文件存在: {self.requirements_file}")
        return True
    
    def check_core_dependencies(self) -> bool:
        """检测核心依赖包"""
        core_deps = [
            "PyQt5",
            "requests", 
            "pydantic",
            "asyncio",
            "json",
            "pathlib"
        ]
        
        missing_deps = []
        for dep in core_deps:
            try:
                importlib.import_module(dep)
                print(f"   ✅ {dep}")
            except ImportError:
                print(f"   ❌ {dep}: 未安装")
                missing_deps.append(dep)
        
        if missing_deps:
            print(f"   💡 请安装缺失的依赖: pip install {' '.join(missing_deps)}")
            return False
        
        return True
    
    def check_optional_dependencies(self) -> bool:
        """检测可选依赖包"""
        optional_deps = [
            ("fastapi", "API服务器"),
            ("uvicorn", "API服务器"),
            ("neo4j", "知识图谱"),
            ("onnxruntime", "语音服务"),
            ("websockets", "WebSocket支持"),
            ("crawl4ai", "网页爬取"),
            ("playwright", "浏览器自动化")
        ]
        
        missing_optional = []
        for dep, desc in optional_deps:
            try:
                importlib.import_module(dep)
                print(f"   ✅ {dep} ({desc})")
            except ImportError:
                print(f"   ⚠️ {dep} ({desc}): 未安装")
                missing_optional.append((dep, desc))
        
        if missing_optional:
            print(f"   💡 可选依赖缺失，某些功能可能不可用:")
            for dep, desc in missing_optional:
                print(f"      - {dep}: {desc}")
        
        return True  # 可选依赖不影响启动
    
    def check_config_files(self) -> bool:
        """检测配置文件"""
        config_files = [
            ("config.json", "主配置文件"),
            ("config.json.example", "配置示例文件")
        ]
        
        all_exist = True
        for file_name, desc in config_files:
            file_path = self.project_root / file_name
            if file_path.exists():
                print(f"   ✅ {file_name} ({desc})")
            else:
                print(f"   ❌ {file_name} ({desc}): 不存在")
                all_exist = False
        
        if not all_exist:
            print(f"   💡 请确保配置文件存在")
        
        return all_exist
    
    def check_directory_structure(self) -> bool:
        """检测目录结构"""
        required_dirs = [
            ("ui", "用户界面"),
            ("apiserver", "API服务器"),
            ("mcpserver", "MCP服务器"),
            ("summer_memory", "记忆系统"),
            ("voice", "语音模块"),
            ("logs", "日志目录")
        ]
        
        all_exist = True
        for dir_name, desc in required_dirs:
            dir_path = self.project_root / dir_name
            if dir_path.exists() and dir_path.is_dir():
                print(f"   ✅ {dir_name}/ ({desc})")
            else:
                print(f"   ❌ {dir_name}/ ({desc}): 不存在")
                all_exist = False
        
        return all_exist
    
    def check_permissions(self) -> bool:
        """检测文件权限"""
        try:
            # 检查项目根目录读写权限
            test_file = self.project_root / ".test_permission"
            test_file.write_text("test")
            test_file.unlink()
            
            # 检查logs目录权限
            logs_dir = self.project_root / "logs"
            if logs_dir.exists():
                test_log = logs_dir / ".test_permission"
                test_log.write_text("test")
                test_log.unlink()
            
            print(f"   ✅ 文件权限正常")
            return True
            
        except Exception as e:
            print(f"   ❌ 文件权限异常: {e}")
            return False
    
    def get_system_info(self) -> Dict[str, str]:
        """获取系统信息"""
        return {
            "操作系统": platform.system(),
            "系统版本": platform.version(),
            "架构": platform.machine(),
            "Python版本": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "Python路径": sys.executable,
            "项目路径": str(self.project_root),
            "虚拟环境": "是" if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix) else "否"
        }
    
    def print_system_info(self):
        """打印系统信息"""
        print("🖥️ 系统信息:")
        print("-" * 30)
        info = self.get_system_info()
        for key, value in info.items():
            print(f"   {key}: {value}")
        print()
    
    def suggest_fixes(self):
        """建议修复方案"""
        print("🔧 修复建议:")
        print("-" * 30)
        
        if not self.results.get("虚拟环境", True):
            print("1. 创建并激活虚拟环境:")
            print("   python -m venv .venv")
            print("   .venv\\Scripts\\activate  # Windows")
            print("   source .venv/bin/activate  # Linux/Mac")
            print()
        
        if not self.results.get("核心依赖", True):
            print("2. 安装核心依赖:")
            print("   pip install -r requirements.txt")
            print()
        
        if not self.results.get("配置文件", True):
            print("3. 复制配置文件:")
            print("   copy config.json.example config.json  # Windows")
            print("   cp config.json.example config.json  # Linux/Mac")
            print()
        
        if not self.results.get("目录结构", True):
            print("4. 检查项目完整性:")
            print("   确保所有必要的目录和文件都存在")
            print()

    def is_check_passed(self) -> bool:
        """检查是否已经通过过系统检测"""
        if not self.config_file.exists():
            return False
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
                system_check = config_data.get('system_check', {})
                return system_check.get('passed', False)
        except Exception:
            return False
    
    def save_check_status(self, passed: bool):
        """保存检测状态到config.json"""
        try:
            # 读取现有配置
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
            else:
                config_data = {}
            
            # 更新system_check配置
            config_data['system_check'] = {
                'passed': passed,
                'timestamp': platform.system(),
                'python_version': f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
                'project_path': str(self.project_root)
            }
            
            # 保存配置
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️ 保存检测状态失败: {e}")
    
    def should_skip_check(self) -> bool:
        """判断是否应该跳过检测"""
        return self.is_check_passed()
    
    def reset_check_status(self):
        """重置检测状态，强制下次启动时重新检测"""
        try:
            # 读取现有配置
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                
                # 删除system_check配置
                if 'system_check' in config_data:
                    del config_data['system_check']
                
                # 保存配置
                with open(self.config_file, 'w', encoding='utf-8') as f:
                    json.dump(config_data, f, ensure_ascii=False, indent=2)
                
                print("✅ 检测状态已重置，下次启动时将重新检测")
            else:
                print("⚠️ 配置文件不存在")
        except Exception as e:
            print(f"⚠️ 重置检测状态失败: {e}")

def run_system_check(force_check: bool = False) -> bool:
    """运行系统检测"""
    checker = SystemChecker()
    
    # 检查是否已经通过过检测（除非强制检测）
    if not force_check and checker.should_skip_check():
        print("✅ 系统环境检测已通过，跳过检测")
        return True
    
    # 打印系统信息
    checker.print_system_info()
    
    # 执行检测
    results = checker.check_all()
    
    # 保存检测结果
    all_passed = all(results.values())
    checker.save_check_status(all_passed)
    
    # 如果有问题，提供修复建议
    if not all_passed:
        checker.suggest_fixes()
        return False
    
    return True

def reset_system_check():
    """重置系统检测状态"""
    checker = SystemChecker()
    checker.reset_check_status()

if __name__ == "__main__":
    # 独立运行时的测试
    success = run_system_check()
    sys.exit(0 if success else 1)
