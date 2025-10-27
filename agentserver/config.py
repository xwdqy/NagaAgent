#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agent Server配置文件 - 重构版
提供客观、实用的配置管理
"""

from dataclasses import dataclass
from typing import Optional

# ============ 服务器配置 ============

# 从主配置读取端口
try:
    from system.config import get_server_port
    AGENT_SERVER_PORT = get_server_port("agent_server")
except ImportError:
    AGENT_SERVER_PORT = 8001  # 回退默认值

# ============ 任务调度器配置 ============

@dataclass
class TaskSchedulerConfig:
    """任务调度器配置"""
    # 记忆管理阈值
    max_steps: int = 15                    # 最大保存步骤数
    compression_threshold: int = 7          # 压缩触发阈值
    keep_last_steps: int = 4               # 压缩后保留的详细步骤数
    
    # 显示相关阈值
    key_facts_compression_limit: int = 5    # 压缩提示中的关键事实数量
    key_facts_summary_limit: int = 10       # 摘要中的关键事实数量
    compressed_memory_summary_limit: int = 3 # 任务摘要中的压缩记忆数量
    compressed_memory_global_limit: int = 2  # 全局摘要中的压缩记忆数量
    key_findings_display_limit: int = 3     # 关键发现显示数量
    failed_attempts_display_limit: int = 3  # 失败尝试显示数量
    
    # 输出长度限制
    output_summary_length: int = 256        # 关键事实中的输出摘要长度
    step_output_display_length: int = 512   # 步骤显示中的输出长度
    
    # 性能配置
    enable_auto_compression: bool = True    # 是否启用自动压缩
    compression_timeout: int = 30           # 压缩超时时间（秒）
    max_compression_retries: int = 3        # 最大压缩重试次数

# 默认任务调度器配置实例
DEFAULT_TASK_SCHEDULER_CONFIG = TaskSchedulerConfig()

# ============ Agent管理器配置 ============

@dataclass
class AgentManagerConfig:
    """Agent管理器配置"""
    # 会话管理
    default_session_timeout: int = 3600     # 默认会话超时时间（秒）
    max_session_history: int = 100          # 最大会话历史记录数
    
    # 任务执行
    max_concurrent_agents: int = 5          # 最大并发Agent数
    agent_timeout: int = 300                # Agent执行超时时间（秒）
    
    # 缓存配置
    enable_agent_cache: bool = True         # 是否启用Agent缓存
    cache_ttl: int = 1800                   # 缓存生存时间（秒）

# 默认Agent管理器配置实例
DEFAULT_AGENT_MANAGER_CONFIG = AgentManagerConfig()

# ============ 电脑控制Agent配置 ============

@dataclass
class ComputerControlConfig:
    """电脑控制Agent配置"""
    # 执行配置
    max_execution_time: int = 60            # 最大执行时间（秒）
    enable_screenshot: bool = True          # 是否启用截图功能
    screenshot_quality: int = 80            # 截图质量（1-100）
    
    # 安全配置
    enable_safety_checks: bool = True       # 是否启用安全检查
    blocked_commands: list = None           # 被阻止的命令列表
    
    def __post_init__(self):
        if self.blocked_commands is None:
            self.blocked_commands = [
                "rm -rf /", "format c:", "del /f /s /q c:\\",
                "shutdown", "reboot", "halt"
            ]

# 默认电脑控制配置实例
DEFAULT_COMPUTER_CONTROL_CONFIG = ComputerControlConfig()

# ============ 全局配置管理 ============

@dataclass
class AgentServerConfig:
    """Agent服务器全局配置"""
    # 服务器配置
    host: str = "0.0.0.0"
    port: int = None
    
    # 子模块配置
    task_scheduler: TaskSchedulerConfig = None
    agent_manager: AgentManagerConfig = None
    computer_control: ComputerControlConfig = None
    
    # 日志配置
    log_level: str = "INFO"
    enable_debug_logs: bool = False
    
    def __post_init__(self):
        # 设置默认端口
        if self.port is None:
            self.port = AGENT_SERVER_PORT
        
        # 设置默认子配置
        if self.task_scheduler is None:
            self.task_scheduler = DEFAULT_TASK_SCHEDULER_CONFIG
        if self.agent_manager is None:
            self.agent_manager = DEFAULT_AGENT_MANAGER_CONFIG
        if self.computer_control is None:
            self.computer_control = DEFAULT_COMPUTER_CONTROL_CONFIG

# 全局配置实例
config = AgentServerConfig()

# ============ 配置访问函数 ============

def get_task_scheduler_config() -> TaskSchedulerConfig:
    """获取任务调度器配置"""
    return config.task_scheduler

def get_agent_manager_config() -> AgentManagerConfig:
    """获取Agent管理器配置"""
    return config.agent_manager

def get_computer_control_config() -> ComputerControlConfig:
    """获取电脑控制配置"""
    return config.computer_control

def update_config(**kwargs):
    """更新配置"""
    for key, value in kwargs.items():
        if hasattr(config, key):
            setattr(config, key, value)
        else:
            raise ValueError(f"未知配置项: {key}")

# ============ 向后兼容 ============

# 保持向后兼容的配置常量
AGENT_SERVER_HOST = config.host
AGENT_SERVER_PORT = config.port
