﻿# config.py - 简化配置系统
"""
NagaAgent 配置系统 - 基于Pydantic实现类型安全和验证
支持配置热更新和变更通知
"""
import os
import socket
import json
from pathlib import Path
from typing import Optional, List, Dict, Any, Callable
from datetime import datetime

from nagaagent_core.vendors.PyQt5.QtWidgets import QWidget
from pydantic import BaseModel, Field, field_validator
from nagaagent_core.vendors.charset_normalizer import from_path
from nagaagent_core.vendors import json5  # 支持带注释的JSON解析

# ========== 服务器端口配置 - 统一管理 ==========
class ServerPortsConfig(BaseModel):
    """服务器端口配置 - 统一管理所有服务器端口"""
    # 主API服务器
    api_server: int = Field(default=8000, ge=1, le=65535, description="API服务器端口")
    
    # 智能体服务器
    agent_server: int = Field(default=8001, ge=1, le=65535, description="智能体服务器端口")
    
    # MCP工具服务器
    mcp_server: int = Field(default=8003, ge=1, le=65535, description="MCP工具服务器端口")
    
    # TTS语音合成服务器
    tts_server: int = Field(default=5048, ge=1, le=65535, description="TTS语音合成服务器端口")
    
    # ASR语音识别服务器
    asr_server: int = Field(default=5060, ge=1, le=65535, description="ASR语音识别服务器端口")

# 全局服务器端口配置实例
server_ports = ServerPortsConfig()

def get_server_port(server_name: str) -> int:
    """获取指定服务器的端口号"""
    return getattr(server_ports, server_name, None)

def get_all_server_ports() -> Dict[str, int]:
    """获取所有服务器端口配置"""
    return {
        "api_server": server_ports.api_server,
        "agent_server": server_ports.agent_server,
        "mcp_server": server_ports.mcp_server,
        "tts_server": server_ports.tts_server,
        "asr_server": server_ports.asr_server,
    }

# 配置变更监听器
_config_listeners: List[Callable] = []

# 为了向后兼容，提供AI_NAME常量
def get_ai_name() -> str:
    """获取AI名称"""
    return config.system.ai_name

def add_config_listener(callback: Callable):
    """添加配置变更监听器"""
    _config_listeners.append(callback)

def remove_config_listener(callback: Callable):
    """移除配置变更监听器"""
    if callback in _config_listeners:
        _config_listeners.remove(callback)

def notify_config_changed():
    """通知所有监听器配置已变更"""
    for listener in _config_listeners:
        try:
            listener()
        except Exception as e:
            print(f"配置监听器执行失败: {e}")

def setup_environment():
    """设置环境变量解决兼容性问题"""
    env_vars = {
        "OMP_NUM_THREADS": "1",
        "MKL_NUM_THREADS": "1", 
        "OPENBLAS_NUM_THREADS": "1",
        "VECLIB_MAXIMUM_THREADS": "1",
        "NUMEXPR_NUM_THREADS": "1",
        "TOKENIZERS_PARALLELISM": "false",
        "PYTORCH_MPS_HIGH_WATERMARK_RATIO": "0.0",
        "PYTORCH_ENABLE_MPS_FALLBACK": "1"
    }
    for key, value in env_vars.items():
        os.environ.setdefault(key, value)

class SystemConfig(BaseModel):
    """系统基础配置"""
    version: str = Field(default="4.0.0", description="系统版本号")
    ai_name: str = Field(default="娜迦日达", description="AI助手名称")
    base_dir: Path = Field(default_factory=lambda: Path(__file__).parent.parent, description="项目根目录")
    log_dir: Path = Field(default_factory=lambda: Path(__file__).parent.parent / "logs", description="日志目录")
    voice_enabled: bool = Field(default=True, description="是否启用语音功能")
    stream_mode: bool = Field(default=True, description="是否启用流式响应")
    debug: bool = Field(default=False, description="是否启用调试模式")
    log_level: str = Field(default="INFO", description="日志级别")
    save_prompts: bool = Field(default=True, description="是否保存提示词")

    @field_validator('log_level')
    @classmethod
    def validate_log_level(cls, v):
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in valid_levels:
            raise ValueError(f'日志级别必须是以下之一: {valid_levels}')
        return v.upper()

class APIConfig(BaseModel):
    """API服务配置"""
    api_key: str = Field(default="sk-placeholder-key-not-set", description="API密钥")
    base_url: str = Field(default="https://api.deepseek.com/v1", description="API基础URL")
    model: str = Field(default="deepseek-chat", description="使用的模型名称")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="温度参数")
    max_tokens: int = Field(default=10000, ge=1, le=32768, description="最大token数")
    max_history_rounds: int = Field(default=100, ge=1, le=200, description="最大历史轮数")
    persistent_context: bool = Field(default=True, description="是否启用持久化上下文")
    context_load_days: int = Field(default=3, ge=1, le=30, description="加载历史上下文的天数")
    context_parse_logs: bool = Field(default=True, description="是否从日志文件解析上下文")
    applied_proxy: bool = Field(default=True, description="是否应用代理")
    applied_proxy: bool = Field(default=True, description="是否应用代理")

class APIServerConfig(BaseModel):
    """API服务器配置"""
    enabled: bool = Field(default=True, description="是否启用API服务器")
    host: str = Field(default="127.0.0.1", description="API服务器主机")
    port: int = Field(default_factory=lambda: server_ports.api_server, description="API服务器端口")
    auto_start: bool = Field(default=True, description="启动时自动启动API服务器")
    docs_enabled: bool = Field(default=True, description="是否启用API文档")

class GRAGConfig(BaseModel):
    """GRAG知识图谱记忆系统配置"""
    enabled: bool = Field(default=False, description="是否启用GRAG记忆系统")
    auto_extract: bool = Field(default=False, description="是否自动提取对话中的五元组")
    context_length: int = Field(default=5, ge=1, le=20, description="记忆上下文长度")
    similarity_threshold: float = Field(default=0.6, ge=0.0, le=1.0, description="记忆检索相似度阈值")
    neo4j_uri: str = Field(default="neo4j://127.0.0.1:7687", description="Neo4j连接URI")
    neo4j_user: str = Field(default="neo4j", description="Neo4j用户名")
    neo4j_password: str = Field(default="your_password", description="Neo4j密码")
    neo4j_database: str = Field(default="neo4j", description="Neo4j数据库名")
    extraction_timeout: int = Field(default=12, ge=1, le=60, description="知识提取超时时间（秒）")
    extraction_retries: int = Field(default=2, ge=0, le=5, description="知识提取重试次数")
    base_timeout: int = Field(default=15, ge=5, le=120, description="基础操作超时时间（秒）")

class HandoffConfig(BaseModel):
    """工具调用循环配置"""
    max_loop_stream: int = Field(default=5, ge=1, le=20, description="流式模式最大工具调用循环次数")
    max_loop_non_stream: int = Field(default=5, ge=1, le=20, description="非流式模式最大工具调用循环次数")
    show_output: bool = Field(default=False, description="是否显示工具调用输出")

class BrowserConfig(BaseModel):
    """浏览器配置"""
    playwright_headless: bool = Field(default=False, description="Playwright浏览器是否无头模式")
    edge_lnk_path: str = Field(
        default=r'C:\Users\DREEM\Desktop\Microsoft Edge.lnk',
        description="Edge浏览器快捷方式路径"
    )
    edge_common_paths: List[str] = Field(
        default=[
            r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',
            r'C:\Program Files\Microsoft\Edge\Application\msedge.exe',
            os.path.expanduser(r'~\AppData\Local\Microsoft\Edge\Application\msedge.exe')
        ],
        description="Edge浏览器常见安装路径"
    )

class TTSConfig(BaseModel):
    """TTS服务配置"""
    api_key: str = Field(default="", description="TTS服务API密钥")
    port: int = Field(default_factory=lambda: server_ports.tts_server, description="TTS服务端口")
    default_voice: str = Field(default="zh-CN-XiaoxiaoNeural", description="默认语音")
    default_format: str = Field(default="mp3", description="默认音频格式")
    default_speed: float = Field(default=1.0, ge=0.1, le=3.0, description="默认语速")
    default_language: str = Field(default="zh-CN", description="默认语言")
    remove_filter: bool = Field(default=False, description="是否移除过滤")
    expand_api: bool = Field(default=True, description="是否扩展API")
    require_api_key: bool = Field(default=False, description="是否需要API密钥")

class ASRConfig(BaseModel):
    """ASR输入服务配置"""
    port: int = Field(default_factory=lambda: server_ports.asr_server, description="ASR服务端口")
    device_index: int | None = Field(default=None, description="麦克风设备序号")
    sample_rate_in: int = Field(default=48000, description="输入采样率")
    frame_ms: int = Field(default=30, description="分帧时长ms")
    resample_to: int = Field(default=16000, description="重采样目标采样率")
    vad_threshold: float = Field(default=0.7, ge=0.0, le=1.0, description="VAD阈值")
    silence_ms: int = Field(default=420, description="静音结束阈值ms")
    noise_reduce: bool = Field(default=True, description="是否降噪")
    engine: str = Field(default="local_funasr", description="ASR引擎，仅支持local_funasr")
    local_model_path: str = Field(default="./utilss/models/SenseVoiceSmall", description="本地FunASR模型路径")
    vad_model_path: str = Field(default="silero_vad.onnx", description="VAD模型路径")
    api_key_required: bool = Field(default=False, description="是否需要API密钥")
    callback_url: str | None = Field(default=None, description="识别结果回调地址")
    ws_broadcast: bool = Field(default=False, description="是否WS广播结果")

class FilterConfig(BaseModel):
    """输出过滤配置"""
    filter_think_tags: bool = Field(default=True, description="过滤思考标签内容")
    filter_patterns: List[str] = Field(
        default=[
            r'<think>.*?</think>',
            r'<reflection>.*?</reflection>',
            r'<internal>.*?</internal>',
        ],
        description="过滤正则表达式模式"
    )
    clean_output: bool = Field(default=True, description="清理多余空白字符")

class DifficultyConfig(BaseModel):
    """问题难度判断配置"""
    enabled: bool = Field(default=False, description="是否启用难度判断")
    use_small_model: bool = Field(default=False, description="使用小模型进行难度判断")
    pre_assessment: bool = Field(default=False, description="是否启用前置难度判断")
    assessment_timeout: float = Field(default=1.0, ge=0.1, le=5.0, description="难度判断超时时间（秒）")
    difficulty_levels: List[str] = Field(
        default=["简单", "中等", "困难", "极难"],
        description="难度级别"
    )
    factors: List[str] = Field(
        default=["概念复杂度", "推理深度", "知识广度", "计算复杂度", "创新要求"],
        description="难度评估因素"
    )
    threshold_simple: int = Field(default=2, ge=1, le=10, description="简单问题阈值")
    threshold_medium: int = Field(default=4, ge=1, le=10, description="中等问题阈值")
    threshold_hard: int = Field(default=6, ge=1, le=10, description="困难问题阈值")

class ScoringConfig(BaseModel):
    """黑白名单打分系统配置"""
    enabled: bool = Field(default=False, description="是否启用打分系统")
    score_range: List[int] = Field(default=[1, 5], description="评分范围")
    score_threshold: int = Field(default=2, ge=1, le=5, description="结果保留阈值")
    similarity_threshold: float = Field(default=0.85, ge=0.0, le=1.0, description="相似结果识别阈值")
    max_user_preferences: int = Field(default=3, ge=1, le=10, description="用户最多选择偏好数")
    default_preferences: List[str] = Field(
        default=["逻辑清晰准确", "实用性强", "创新思维"],
        description="默认偏好设置"
    )
    penalty_for_similar: int = Field(default=1, ge=0, le=3, description="相似结果的惩罚分数")
    min_results_required: int = Field(default=2, ge=1, le=10, description="最少保留结果数量")
    strict_filtering: bool = Field(default=True, description="严格过滤模式")


# ========== 新增：电脑控制配置 ==========
class ComputerControlConfig(BaseModel):
    """电脑控制配置"""
    enabled: bool = Field(default=True, description="是否启用电脑控制功能")
    model: str = Field(default="glm-4.5v", description="视觉/坐标识别模型")
    model_url: str = Field(default="https://open.bigmodel.cn/api/paas/v4", description="模型API地址")
    api_key: str = Field(default="", description="模型API密钥")
    grounding_model: str = Field(default="glm-4.5v", description="元素定位/grounding模型")
    grounding_url: str = Field(default="https://open.bigmodel.cn/api/paas/v4", description="grounding模型API地址")
    grounding_api_key: str = Field(default="", description="grounding模型API密钥")
    screen_width: int = Field(default=1920, description="逻辑屏幕宽度（用于缩放体系）")
    screen_height: int = Field(default=1080, description="逻辑屏幕高度（用于缩放体系）")
    max_dim_size: int = Field(default=1920, description="逻辑空间最大边尺寸")
    dpi_awareness: bool = Field(default=True, description="是否启用DPI感知（Windows）")
    safe_mode: bool = Field(default=True, description="是否启用安全模式（限制高风险操作）")

# 天气服务使用免费API，无需配置

class MQTTConfig(BaseModel):
    """MQTT配置"""
    enabled: bool = Field(default=False, description="是否启用MQTT功能")
    broker: str = Field(default="localhost", description="MQTT代理服务器地址")
    port: int = Field(default=1883, ge=1, le=65535, description="MQTT代理服务器端口")
    topic: str = Field(default="/test/topic", description="MQTT主题")
    client_id: str = Field(default="naga_mqtt_client", description="MQTT客户端ID")
    username: str = Field(default="", description="MQTT用户名")
    password: str = Field(default="", description="MQTT密码")
    keepalive: int = Field(default=60, ge=1, le=3600, description="保持连接时间（秒）")
    qos: int = Field(default=1, ge=0, le=2, description="服务质量等级")

class UIConfig(BaseModel):
    """用户界面配置"""
    user_name: str = Field(default="用户", description="默认用户名")
    bg_alpha: float = Field(default=0.5, ge=0.0, le=1.0, description="聊天背景透明度")
    window_bg_alpha: int = Field(default=110, ge=0, le=255, description="主窗口背景透明度")
    mac_btn_size: int = Field(default=36, ge=10, le=100, description="Mac按钮大小")
    mac_btn_margin: int = Field(default=16, ge=0, le=50, description="Mac按钮边距")
    mac_btn_gap: int = Field(default=12, ge=0, le=30, description="Mac按钮间距")
    animation_duration: int = Field(default=600, ge=100, le=2000, description="动画时长（毫秒）")

class Live2DConfig(BaseModel):
    """Live2D配置"""
    enabled: bool = Field(default=True, description="是否启用Live2D功能")
    model_path: str = Field(default="ui/live2d/live2d_models/kasane_teto/kasane_teto.model3.json", description="Live2D模型文件路径")
    fallback_image: str = Field(default="ui/img/standby.png", description="回退图片路径")
    auto_switch: bool = Field(default=True, description="是否自动切换模式")
    animation_enabled: bool = Field(default=True, description="是否启用动画")
    touch_interaction: bool = Field(default=True, description="是否启用触摸交互")
    scale_factor: float = Field(default=1.0, ge=0.5, le=3.0, description="Live2D缩放比例")

class VoiceRealtimeConfig(BaseModel):
    """实时语音配置"""
    enabled: bool = Field(default=False, description="是否启用实时语音功能")
    provider: str = Field(default="qwen", description="语音服务提供商 (qwen/openai/local)")
    api_key: str = Field(default="", description="语音服务API密钥")
    model: str = Field(default="qwen3-omni-flash-realtime", description="语音模型名称")
    voice: str = Field(default="Cherry", description="语音角色")
    input_sample_rate: int = Field(default=16000, description="输入采样率")
    output_sample_rate: int = Field(default=24000, description="输出采样率")
    chunk_size_ms: int = Field(default=200, description="音频块大小（毫秒）")
    vad_threshold: float = Field(default=0.02, ge=0.0, le=1.0, description="静音检测阈值")
    echo_suppression: bool = Field(default=True, description="回声抑制")
    min_user_interval: float = Field(default=2.0, ge=0.5, le=10.0, description="用户输入最小间隔（秒）")
    cooldown_duration: float = Field(default=1.0, ge=0.5, le=5.0, description="冷却期时长（秒）")
    max_user_speech: float = Field(default=30.0, ge=5.0, le=120.0, description="最大说话时长（秒）")
    debug: bool = Field(default=False, description="是否启用调试模式")
    integrate_with_memory: bool = Field(default=True, description="是否集成到记忆系统")
    show_in_chat: bool = Field(default=True, description="是否在聊天界面显示对话内容")
    use_api_server: bool = Field(default=False, description="是否通过API Server处理（支持MCP调用）")
    voice_mode: str = Field(default="auto", description="语音模式：auto/local/end2end/hybrid（auto会根据provider自动选择）")
    asr_host: str = Field(default="localhost", description="本地ASR服务地址")
    asr_port: int = Field(default=5000, description="本地ASR服务端口")
    record_duration: int = Field(default=10, ge=5, le=60, description="本地模式最大录音时长（秒）")
    tts_voice: str = Field(default="zh-CN-XiaoyiNeural", description="TTS语音选择（本地/混合模式）")
    tts_host: str = Field(default="localhost", description="TTS服务地址")
    tts_port: int = Field(default=5061, ge=1, le=65535, description="TTS服务端口")
    auto_play: bool = Field(default=True, description="AI回复后自动播放语音")
    interrupt_playback: bool = Field(default=True, description="用户说话时自动打断AI语音播放")

class NagaPortalConfig(BaseModel):
    """娜迦官网账户配置"""
    portal_url: str = Field(default="https://naga.furina.chat/", description="娜迦官网地址")
    username: str = Field(default="", description="娜迦官网用户名")
    password: str = Field(default="", description="娜迦官网密码")
    request_timeout: int = Field(default=30, ge=5, le=120, description="请求超时时间（秒）")
    login_path: str = Field(default="/api/user/login", description="登录API路径")
    turnstile_param: str = Field(default="", description="Turnstile验证参数")
    login_username_key: str = Field(default="username", description="登录请求中用户名的键名")
    login_password_key: str = Field(default="password", description="登录请求中密码的键名")
    login_payload_mode: str = Field(default="json", description="登录请求载荷模式：json或form")
    default_headers: Dict[str, str] = Field(
        default={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Content-Type": "application/json"
        },
        description="默认HTTP请求头"
    )

class OnlineSearchConfig(BaseModel):
    """在线搜索配置"""
    searxng_url: str = Field(default="http://localhost:8080", description="SearXNG实例URL")
    engines: List[str] = Field(default=["google"], description="默认搜索引擎列表")
    num_results: int = Field(default=5, ge=1, le=20, description="搜索结果数量")

class SystemCheckConfig(BaseModel):
    """系统检测状态配置"""
    passed: bool = Field(default=False, description="系统检测是否通过")
    timestamp: str = Field(default="", description="检测时间戳")
    python_version: str = Field(default="", description="Python版本")
    project_path: str = Field(default="", description="项目路径")

# 提示词管理功能已集成到config.py中

class PromptManager:
    """提示词管理器 - 统一管理所有提示词模板"""
    
    def __init__(self, prompts_dir: str = None):
        """初始化提示词管理器"""
        if prompts_dir is None:
            # 默认使用system目录下的prompts文件夹
            prompts_dir = Path(__file__).parent / "prompts"
        
        self.prompts_dir = Path(prompts_dir)
        self.prompts_dir.mkdir(exist_ok=True)
        
        # 内存缓存
        self._cache = {}
        self._last_modified = {}
        
        # 初始化默认提示词
        self._init_default_prompts()
    
    def _init_default_prompts(self):
        """初始化默认提示词 - 现在从文件加载，不再硬编码"""
        # 检查是否存在默认提示词文件，如果不存在则创建
        default_prompts = ["conversation_analyzer_prompt","conversation_style_prompt"]
        
        for prompt_name in default_prompts:
            prompt_file = self.prompts_dir / f"{prompt_name}.txt"
            if not prompt_file.exists():
                print(f"警告：提示词文件 {prompt_name}.txt 不存在，请手动创建")
    
    def get_prompt(self, name: str, **kwargs) -> str:
        """获取提示词模板"""
        try:
            # 从缓存或文件加载
            content = self._load_prompt(name)
            if content is None:
                print(f"警告：提示词 '{name}' 不存在，使用默认值")
                return f"[提示词 {name} 未找到]"
            
            # 格式化模板
            if kwargs:
                try:
                    return content.format(**kwargs)
                except KeyError as e:
                    print(f"错误：提示词 '{name}' 格式化失败，缺少参数: {e}")
                    return content
            else:
                return content
                
        except Exception as e:
            print(f"错误：获取提示词 '{name}' 失败: {e}")
            return f"[提示词 {name} 加载失败: {e}]"
    
    def save_prompt(self, name: str, content: str):
        """保存提示词到文件"""
        try:
            prompt_file = self.prompts_dir / f"{name}.txt"
            with open(prompt_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # 更新缓存
            self._cache[name] = content
            self._last_modified[name] = datetime.now()
            
            print(f"提示词 '{name}' 已保存")
            
        except Exception as e:
            print(f"错误：保存提示词 '{name}' 失败: {e}")
    
    def _load_prompt(self, name: str) -> Optional[str]:
        """从文件加载提示词"""
        try:
            prompt_file = self.prompts_dir / f"{name}.txt"
            
            if not prompt_file.exists():
                return None
            
            # 检查文件是否被修改
            current_mtime = prompt_file.stat().st_mtime
            if name in self._last_modified and self._last_modified[name].timestamp() >= current_mtime:
                return self._cache.get(name)
            
            # 读取文件
            with open(prompt_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 更新缓存
            self._cache[name] = content
            self._last_modified[name] = datetime.now()
            
            return content
            
        except Exception as e:
            print(f"错误：加载提示词 '{name}' 失败: {e}")
            return None

# 全局提示词管理器实例
_prompt_manager = None

def get_prompt_manager() -> PromptManager:
    """获取全局提示词管理器实例"""
    global _prompt_manager
    if _prompt_manager is None:
        _prompt_manager = PromptManager()
    return _prompt_manager

def get_prompt(name: str, **kwargs) -> str:
    """便捷函数：获取提示词"""
    return get_prompt_manager().get_prompt(name, **kwargs)

def save_prompt(name: str, content: str):
    """便捷函数：保存提示词"""
    get_prompt_manager().save_prompt(name, content)

class GameModuleConfig(BaseModel):
    """博弈论模块配置"""
    enabled: bool = Field(default=False, description="是否启用博弈论流程")
    skip_on_error: bool = Field(default=True, description="博弈论流程失败时是否回退到普通对话")

class NagaConfig(BaseModel):
    """NagaAgent主配置类"""
    system: SystemConfig = Field(default_factory=SystemConfig)
    api: APIConfig = Field(default_factory=APIConfig)
    api_server: APIServerConfig = Field(default_factory=APIServerConfig)
    grag: GRAGConfig = Field(default_factory=GRAGConfig)
    handoff: HandoffConfig = Field(default_factory=HandoffConfig)
    browser: BrowserConfig = Field(default_factory=BrowserConfig)
    tts: TTSConfig = Field(default_factory=TTSConfig)
    asr: ASRConfig = Field(default_factory=ASRConfig)  # ASR输入服务配置 #
    filter: FilterConfig = Field(default_factory=FilterConfig)
    difficulty: DifficultyConfig = Field(default_factory=DifficultyConfig)
    scoring: ScoringConfig = Field(default_factory=ScoringConfig)
    # prompts: 提示词配置已迁移到 system/prompt_repository.py
    game: GameModuleConfig = Field(default_factory=GameModuleConfig)
    # weather: 天气服务使用免费API，无需配置
    mqtt: MQTTConfig = Field(default_factory=MQTTConfig)
    ui: UIConfig = Field(default_factory=UIConfig)
    live2d: Live2DConfig = Field(default_factory=Live2DConfig)
    voice_realtime: VoiceRealtimeConfig = Field(default_factory=VoiceRealtimeConfig)  # 实时语音配置
    naga_portal: NagaPortalConfig = Field(default_factory=NagaPortalConfig)
    online_search: OnlineSearchConfig = Field(default_factory=OnlineSearchConfig)
    system_check: SystemCheckConfig = Field(default_factory=SystemCheckConfig)
    computer_control: ComputerControlConfig = Field(default_factory=ComputerControlConfig)
    window: QWidget = Field(default=None)

    model_config = {
        "extra": "ignore",  # 保留原配置：忽略未定义的字段
        "arbitrary_types_allowed": True,  # 允许非标准类型（如 QWidget）
        "json_schema_extra": {
            "exclude": ["window"]  # 序列化到 config.json 时排除 window 字段（避免报错）
        }
    }
    def __init__(self, **kwargs):
        setup_environment()
        super().__init__(**kwargs)
        self.system.log_dir.mkdir(parents=True, exist_ok=True)  # 确保递归创建日志目录


# 全局配置实例

def load_config():
    """加载配置"""
    config_path = str(Path(__file__).parent.parent / "config.json")

    if os.path.exists(config_path):
        try:
            # 使用Charset Normalizer自动检测编码
            charset_results = from_path(config_path)
            if charset_results:
                best_match = charset_results.best()
                if best_match:
                    detected_encoding = best_match.encoding
                    print(f"检测到配置文件编码: {detected_encoding}")

                    # 使用检测到的编码直接打开文件，然后使用json5读取
                    with open(config_path, 'r', encoding=detected_encoding) as f:
                        # 使用json5解析支持注释的JSON
                        try:
                            config_data = json5.load(f)
                        except Exception as json5_error:
                            print(f"json5解析失败: {json5_error}")
                            print("尝试使用标准JSON库解析（将忽略注释）...")
                            # 回退到标准JSON库，但需要先去除注释
                            f.seek(0)  # 重置文件指针
                            content = f.read()
                            # 去除注释行
                            lines = content.split('\n')
                            cleaned_lines = []
                            for line in lines:
                                # 移除行内注释（#后面的内容）
                                if '#' in line:
                                    line = line.split('#')[0].rstrip()
                                if line.strip():  # 只保留非空行
                                    cleaned_lines.append(line)
                            cleaned_content = '\n'.join(cleaned_lines)
                            config_data = json.loads(cleaned_content)
                    return NagaConfig(**config_data)
                else:
                    print(f"警告：无法检测 {config_path} 的编码")
            else:
                print(f"警告：无法检测 {config_path} 的编码")

            # 如果自动检测失败，回退到原来的方法
            print("使用回退方法加载配置")
            with open(config_path, 'r', encoding='utf-8') as f:
                # 使用json5解析支持注释的JSON
                config_data = json5.load(f)
            return NagaConfig(**config_data)

        except Exception as e:
            print(f"警告：加载 {config_path} 失败: {e}")
            print("使用默认配置")
            return NagaConfig()
    else:
        print(f"警告：配置文件 {config_path} 不存在，使用默认配置")

    return NagaConfig()

config = load_config()

def reload_config() -> NagaConfig:
    """重新加载配置"""
    global config
    config = load_config()
    notify_config_changed()
    return config

def hot_reload_config() -> NagaConfig:
    """热更新配置 - 重新加载配置并通知所有模块"""
    global config
    old_config = config
    config = load_config()
    notify_config_changed()
    print(f"配置已热更新: {old_config.system.version} -> {config.system.version}")
    return config

def get_config() -> NagaConfig:
    """获取当前配置"""
    return config

# 初始化时打印配置信息
if config.system.debug:
    print(f"NagaAgent {config.system.version} 配置已加载")
    print(f"API服务器: {'启用' if config.api_server.enabled else '禁用'} ({config.api_server.host}:{config.api_server.port})")
    print(f"GRAG记忆系统: {'启用' if config.grag.enabled else '禁用'}")

# 启动时设置用户显示名：优先config.json，其次系统用户名 #
try:
    # 检查 config.json 中的 user_name 是否为空白或未填写
    if not config.ui.user_name or not config.ui.user_name.strip():
        # 如果是，则尝试获取系统登录用户名并覆盖
        config.ui.user_name = os.getlogin()
except Exception:
    # 获取系统用户名失败时，将保留默认值 "用户" 或 config.json 中的空值
    pass

# 向后兼容的AI_NAME常量
AI_NAME = config.system.ai_name

import logging
logger = logging.getLogger(__name__)
