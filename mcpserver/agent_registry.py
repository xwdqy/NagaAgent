#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agent注册器 - 负责Agent的注册、发现和管理
承接MCP Registry的转接，统一管理所有Agent类型
"""

import os
import json
import asyncio
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

# 配置日志
logger = logging.getLogger("AgentRegistry")
logger.setLevel(logging.INFO)

# 如果没有处理器，添加一个
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(levelname)s - %(name)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

@dataclass
class AgentConfig:
    """Agent配置类"""
    id: str  # 模型ID
    name: str  # Agent名称（中文名）
    base_name: str  # 基础名称（英文）
    system_prompt: str  # 系统提示词
    max_output_tokens: int = 40000  # 最大输出token数
    temperature: float = 0.7  # 温度参数
    description: str = ""  # 描述信息
    model_provider: str = "openai"  # 模型提供商
    api_base_url: str = ""  # API基础URL
    api_key: str = ""  # API密钥
    execution_method: Dict[str, str] = None  # 自定义执行方法

class AgentRegistry:
    """Agent注册器"""
    
    def __init__(self, config_dir: str = "agent_configs"):
        """
        初始化Agent注册器
        
        Args:
            config_dir: Agent配置文件目录
        """
        self.config_dir = Path(config_dir)
        self.agents: Dict[str, AgentConfig] = {}
        
        # 确保配置目录存在
        self.config_dir.mkdir(exist_ok=True)
        
        # 加载Agent配置
        self._load_agent_configs()
        
        # 显示已加载的Agent信息
        self._log_registered_agents()
    
    def _load_agent_configs(self):
        """从配置文件加载Agent定义"""
        # 扫描配置文件目录
        config_files = list(self.config_dir.glob("*.json"))
        
        for config_file in config_files:
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                
                # 解析Agent配置
                for agent_key, agent_data in config_data.items():
                    if self._validate_agent_config(agent_data):
                        agent_config = AgentConfig(
                            id=agent_data.get('model_id', ''),
                            name=agent_data.get('name', agent_key),
                            base_name=agent_data.get('base_name', agent_key),
                            system_prompt=agent_data.get('system_prompt', f'You are a helpful AI assistant named {agent_data.get("name", agent_key)}.'),
                            max_output_tokens=agent_data.get('max_output_tokens', 40000),
                            temperature=agent_data.get('temperature', 0.7),
                            description=agent_data.get('description', f'Assistant {agent_data.get("name", agent_key)}.'),
                            model_provider=agent_data.get('model_provider', 'openai'),
                            api_base_url=agent_data.get('api_base_url', ''),
                            api_key=agent_data.get('api_key', '')
                        )
                        
                        self.agents[agent_key] = agent_config
                
            except Exception as e:
                logger.error(f"加载配置文件 {config_file} 失败: {e}")
    
    def _validate_agent_config(self, config: Dict[str, Any]) -> bool:
        """验证Agent配置"""
        # 支持新旧两种格式的必需字段
        required_fields = ['modelId', 'model_id', 'name', 'displayName']
        has_required = False
        
        for field in required_fields:
            if field in config and config[field]:
                has_required = True
                break
        
        if not has_required:
            logger.warning(f"Agent配置缺少必需字段: 需要modelId/model_id或name/displayName中的至少一个")
            return False
        return True
    
    def _replace_placeholders(self, text: str) -> str:
        """替换配置中的占位符，支持环境变量和config配置"""
        if not text:
            return ""
        
        processed_text = str(text)
        
        # 从config获取配置
        try:
            from config import load_config
            config = load_config()
            
            # 替换API相关占位符
            processed_text = processed_text.replace("{{API_KEY}}", config.api.api_key)
            processed_text = processed_text.replace("{{BASE_URL}}", config.api.base_url)
            processed_text = processed_text.replace("{{MODEL_NAME}}", config.api.model)
        except Exception as e:
            logger.warning(f"从config加载配置失败: {e}")
        
        # 环境变量占位符替换
        import os
        import re
        
        # 匹配 {{ENV_VAR_NAME}} 格式的环境变量
        env_pattern = r'\{\{([A-Z_][A-Z0-9_]*)\}\}'
        for match in re.finditer(env_pattern, processed_text):
            env_var_name = match.group(1)
            env_value = os.getenv(env_var_name, '')
            processed_text = processed_text.replace(f"{{{{{env_var_name}}}}}", env_value)
        
        return processed_text
    
    def register_agent_from_manifest(self, agent_name: str, agent_config: Dict[str, Any]) -> bool:
        """从manifest注册Agent
        
        Args:
            agent_name: Agent名称
            agent_config: Agent配置字典
            
        Returns:
            bool: 注册是否成功
        """
        try:
            # 验证配置
            if not self._validate_agent_config(agent_config):
                logger.warning(f"Agent配置验证失败: {agent_name}")
                return False
            
            # 创建AgentConfig对象
            agent_config_obj = AgentConfig(
                id=self._replace_placeholders(agent_config.get('modelId', agent_config.get('model_id', ''))),
                name=agent_config.get('displayName', agent_config.get('name', agent_name)),
                base_name=agent_name,
                system_prompt=self._replace_placeholders(agent_config.get('systemPrompt', agent_config.get('system_prompt', f'You are a helpful AI assistant named {agent_config.get("displayName", agent_config.get("name", agent_name))}.'))),
                max_output_tokens=agent_config.get('maxOutputTokens', agent_config.get('max_output_tokens', 8192)),
                temperature=agent_config.get('temperature', 0.7),
                description=self._replace_placeholders(agent_config.get('description', f'Assistant {agent_config.get("displayName", agent_config.get("name", agent_name))}.')),
                model_provider=agent_config.get('modelProvider', agent_config.get('model_provider', 'openai')),
                api_base_url=self._replace_placeholders(agent_config.get('apiBaseUrl', agent_config.get('api_base_url', ''))),
                api_key=self._replace_placeholders(agent_config.get('apiKey', agent_config.get('api_key', ''))),
                execution_method=agent_config.get('executionMethod', None)
            )
            
            # 注册到agents字典
            self.agents[agent_name] = agent_config_obj
            logger.info(f"已从manifest注册Agent: {agent_name} ({agent_config_obj.name})")
            
            return True
            
        except Exception as e:
            logger.error(f"从manifest注册Agent失败 {agent_name}: {e}")
            return False
    
    def get_agent_config(self, agent_name: str) -> Optional[AgentConfig]:
        """获取Agent配置
        
        Args:
            agent_name: Agent名称
            
        Returns:
            Optional[AgentConfig]: Agent配置对象
        """
        return self.agents.get(agent_name)
    
    def get_all_agents(self) -> Dict[str, AgentConfig]:
        """获取所有Agent配置
        
        Returns:
            Dict[str, AgentConfig]: 所有Agent配置
        """
        return self.agents.copy()
    
    def get_available_agents(self) -> List[Dict[str, Any]]:
        """获取所有可用的Agent列表"""
        return [
            {
                "name": agent_config.name,
                "base_name": agent_config.base_name,
                "description": agent_config.description,
                "model_id": agent_config.id,
                "temperature": agent_config.temperature,
                "max_output_tokens": agent_config.max_output_tokens
            }
            for agent_config in self.agents.values()
        ]
    
    def get_agent_info(self, agent_name: str) -> Optional[Dict[str, Any]]:
        """获取指定Agent的详细信息"""
        if agent_name not in self.agents:
            return None
        
        agent_config = self.agents[agent_name]
        return {
            "name": agent_config.name,
            "base_name": agent_config.base_name,
            "description": agent_config.description,
            "model_id": agent_config.id,
            "temperature": agent_config.temperature,
            "max_output_tokens": agent_config.max_output_tokens,
            "system_prompt": agent_config.system_prompt,
            "model_provider": agent_config.model_provider
        }
    
    def reload_configs(self):
        """重新加载Agent配置"""
        self.agents.clear()
        self._load_agent_configs()
        logger.info("Agent配置已重新加载")
    
    def has_agent(self, agent_name: str) -> bool:
        """检查Agent是否存在
        
        Args:
            agent_name: Agent名称
            
        Returns:
            bool: Agent是否存在
        """
        return agent_name in self.agents
    
    def _log_registered_agents(self):
        """记录已注册的Agent信息"""
        if self.agents:
            agent_names = [f"{name} ({config.name})" for name, config in self.agents.items()]
            logger.info(f"AgentRegistry初始化完成，已加载 {len(self.agents)} 个Agent: {', '.join(agent_names)}")

# 全局Agent注册器实例
_AGENT_REGISTRY = None

def get_agent_registry() -> AgentRegistry:
    """获取全局Agent注册器实例"""
    global _AGENT_REGISTRY
    if _AGENT_REGISTRY is None:
        _AGENT_REGISTRY = AgentRegistry()
    return _AGENT_REGISTRY

# 便捷函数
def list_agents() -> List[Dict[str, Any]]:
    """便捷的Agent列表获取函数"""
    registry = get_agent_registry()
    return registry.get_available_agents()

def get_agent_info(agent_name: str) -> Optional[Dict[str, Any]]:
    """便捷的Agent信息获取函数"""
    registry = get_agent_registry()
    return registry.get_agent_info(agent_name)

def has_agent(agent_name: str) -> bool:
    """便捷的Agent存在检查函数"""
    registry = get_agent_registry()
    return registry.has_agent(agent_name) 