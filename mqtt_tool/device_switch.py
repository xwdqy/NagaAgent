# device_switch.py # 设备开关控制MCP工具
import json
import logging
import sys
import os
import time
import threading
from typing import Optional, Dict, Any
from fastmcp import FastMCP

logger = logging.getLogger('DeviceSwitch')

# Windows 控制台 UTF-8 编码修复
if sys.platform == 'win32':
    sys.stderr.reconfigure(encoding='utf-8')
    sys.stdout.reconfigure(encoding='utf-8')

# 从config模块读取MQTT配置
def load_mqtt_config():
    """从config模块加载MQTT配置"""
    try:
        # 添加项目根目录到路径，以便导入config
        sys.path.append(os.path.dirname(os.path.dirname(__file__)))
        from config import config
        
        # 检查是否启用MQTT
        if not config.mqtt.enabled:
            logger.info("MQTT功能未启用，跳过初始化")
            return None
            
        return {
            'broker': config.mqtt.broker,
            'port': config.mqtt.port,
            'topic': config.mqtt.topic,
            'client_id': config.mqtt.client_id,
            'username': config.mqtt.username,
            'password': config.mqtt.password
        }
    except ImportError:
        # 兼容旧版本，从config.json读取MQTT配置
        try:
            config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.json')
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            mqtt_config = config_data.get('mqtt', {})
            
            # 检查是否启用MQTT
            if not mqtt_config.get('enabled', False):
                logger.info("MQTT功能未启用，跳过初始化")
                return None
                
            return {
                'broker': mqtt_config.get('broker', 'broker.emqx.io'),
                'port': mqtt_config.get('port', 1883),
                'topic': mqtt_config.get('topic', 'device/switch'),
                'client_id': mqtt_config.get('client_id', 'mcp_device_switch'),
                'username': mqtt_config.get('username', ''),
                'password': mqtt_config.get('password', '')
            }
        except Exception as e:
            logger.warning(f"无法加载MQTT配置: {e}")
            return None
    except Exception as e:
        logger.warning(f"无法加载MQTT配置: {e}")
        return None

# 加载MQTT配置
mqtt_config = load_mqtt_config()

# 只有在MQTT配置存在且启用时才导入MQTT相关模块
if mqtt_config:
    try:
        import paho.mqtt.client as mqtt
        MQTT_AVAILABLE = True
    except ImportError:
        logger.warning("paho-mqtt库未安装，MQTT功能不可用")
        MQTT_AVAILABLE = False
        mqtt = None
else:
    MQTT_AVAILABLE = False
    mqtt = None

mcp = FastMCP("DeviceSwitch")

class DeviceSwitchManager:
    """设备开关管理器"""
    def __init__(self):
        if not mqtt_config or not MQTT_AVAILABLE:
            self.available = False
            logger.warning("MQTT功能不可用，设备开关控制将无法工作")
            return
            
        self.available = True
        self.client = mqtt.Client(client_id=mqtt_config['client_id'])
        self.connected = False
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect  # 添加断开连接回调
        self.client.on_message = self._on_message
        self.last_message = None
        self._lock = threading.Lock()
        
        # 自动重连设置
        self.reconnect_enabled = True
        self.reconnect_attempt = 0
        self.max_reconnect_attempts = 10
        self.reconnect_delay = 1  # 初始重连延迟（秒）
        self.max_reconnect_delay = 60  # 最大重连延迟（秒）
        self.reconnect_thread = None
        self.should_reconnect = False
        
        # 设置用户名密码（如果有）
        if mqtt_config['username'] or mqtt_config['password']:
            self.client.username_pw_set(mqtt_config['username'], mqtt_config['password'])

    def _on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.connected = True
            self.reconnect_attempt = 0  # 重置重连计数器
            self.reconnect_delay = 1  # 重置重连延迟
            logger.info(f"已连接到MQTT服务器 {client._host}:{client._port}")
            # 订阅主题以接收设备状态反馈
            client.subscribe(f"{mqtt_config['topic']}/status")
        else:
            self.connected = False
            logger.error(f"MQTT连接失败，错误代码: {rc}")
            # 触发重连
            if self.reconnect_enabled:
                self._start_reconnect()

    def _on_disconnect(self, client, userdata, rc):
        """断开连接回调"""
        self.connected = False
        logger.warning(f"MQTT连接断开，错误代码: {rc}")
        
        # 如果不是主动断开，则尝试重连
        if rc != 0 and self.reconnect_enabled:
            self._start_reconnect()

    def _on_message(self, client, userdata, msg):
        """接收设备状态反馈"""
        try:
            # 编码问题转换：确保消息正确解码
            if isinstance(msg.payload, bytes):
                try:
                    payload = msg.payload.decode('utf-8')
                except UnicodeDecodeError:
                    # 如果UTF-8解码失败，尝试其他编码
                    try:
                        payload = msg.payload.decode('gbk')
                    except UnicodeDecodeError:
                        payload = msg.payload.decode('latin-1')  # 最后尝试latin-1
            else:
                payload = str(msg.payload)
            
            self.last_message = {
                "topic": msg.topic,
                "payload": payload,
                "timestamp": time.time()
            }
            logger.info(f"收到设备状态: {payload}")
        except Exception as e:
            logger.error(f"处理消息失败: {e}")

    def _start_reconnect(self):
        """启动自动重连"""
        if self.reconnect_thread and self.reconnect_thread.is_alive():
            return  # 重连线程已在运行
            
        self.should_reconnect = True
        self.reconnect_thread = threading.Thread(target=self._reconnect_loop, daemon=True)
        self.reconnect_thread.start()
        logger.info("启动自动重连线程")

    def _reconnect_loop(self):
        """重连循环"""
        while self.should_reconnect and self.reconnect_attempt < self.max_reconnect_attempts:
            try:
                logger.info(f"尝试重连 ({self.reconnect_attempt + 1}/{self.max_reconnect_attempts})，延迟 {self.reconnect_delay} 秒")
                time.sleep(self.reconnect_delay)
                
                # 尝试重连
                self.client.reconnect()
                
                # 等待连接确认
                for _ in range(10):  # 等待5秒
                    if self.connected:
                        logger.info("重连成功")
                        return
                    time.sleep(0.5)
                
                # 重连失败，增加延迟
                self.reconnect_attempt += 1
                self.reconnect_delay = min(self.reconnect_delay * 2, self.max_reconnect_delay)
                
            except Exception as e:
                logger.error(f"重连失败: {e}")
                self.reconnect_attempt += 1
                self.reconnect_delay = min(self.reconnect_delay * 2, self.max_reconnect_delay)
        
        if self.reconnect_attempt >= self.max_reconnect_attempts:
            logger.error("达到最大重连次数，停止重连")
            self.should_reconnect = False

    def stop_reconnect(self):
        """停止自动重连"""
        self.should_reconnect = False
        if self.reconnect_thread and self.reconnect_thread.is_alive():
            self.reconnect_thread.join(timeout=1)

    def connect(self):
        """连接到MQTT服务器"""
        if not self.available:
            return False
            
        if not self.connected:
            try:
                self.client.connect(mqtt_config['broker'], mqtt_config['port'], 60)
                self.client.loop_start()
                
                # 等待连接确认
                for _ in range(10):  # 增加等待时间到5秒
                    if self.connected:
                        return True
                    time.sleep(0.5)
                
                # 如果连接失败，启动重连
                if not self.connected and self.reconnect_enabled:
                    logger.warning("初始连接失败，启动自动重连")
                    self._start_reconnect()
                
                return False
            except Exception as e:
                logger.error(f"MQTT连接失败: {e}")
                # 连接异常时也启动重连
                if self.reconnect_enabled:
                    self._start_reconnect()
                return False
        return True

    def switch_devices(self, device1: int, device2: int):
        """控制两个设备的开关"""
        if not self.available:
            return False, "MQTT功能不可用"
            
        with self._lock:
            if not self.connect():
                return False, "MQTT未连接"
            
            try:
                # 构建控制消息
                payload = {
                    "device1": int(device1),
                    "device2": int(device2),
                    "timestamp": time.time()
                }
                
                # 编码处理：确保JSON字符串正确编码
                try:
                    payload_str = json.dumps(payload, ensure_ascii=False)
                    payload_bytes = payload_str.encode('utf-8')
                except UnicodeEncodeError:
                    # 如果UTF-8编码失败，使用ASCII编码
                    payload_str = json.dumps(payload, ensure_ascii=True)
                    payload_bytes = payload_str.encode('ascii')
                
                # 发布消息
                result = self.client.publish(mqtt_config['topic'], payload_bytes)
                
                if result.rc == mqtt.MQTT_ERR_SUCCESS:
                    logger.info(f"已发送设备控制命令: {payload}")
                    return True, "命令已发送"
                else:
                    return False, f"发送失败，错误代码: {result.rc}"
                    
            except Exception as e:
                logger.error(f"发送设备控制命令失败: {e}")
                return False, f"发送失败: {str(e)}"

    def get_last_status(self):
        """获取最后收到的设备状态"""
        if not self.available:
            return None
            
        if self.last_message:
            return self.last_message
        return None

    def cleanup(self):
        """清理资源，停止重连并断开连接"""
        if not self.available:
            return
            
        try:
            # 停止自动重连
            self.stop_reconnect()
            
            # 断开连接
            if self.connected:
                self.client.disconnect()
                self.client.loop_stop()
                self.connected = False
                logger.info("MQTT连接已断开")
                
        except Exception as e:
            logger.error(f"清理MQTT连接时出错: {e}")

    def get_connection_status(self):
        """获取连接状态信息"""
        if not self.available:
            return {
                "available": False,
                "connected": False,
                "reconnect_enabled": False,
                "reconnect_attempt": 0
            }
            
        return {
            "available": True,
            "connected": self.connected,
            "reconnect_enabled": self.reconnect_enabled,
            "reconnect_attempt": self.reconnect_attempt,
            "max_reconnect_attempts": self.max_reconnect_attempts,
            "reconnect_delay": self.reconnect_delay
        }

# 全局设备管理器实例
device_manager = DeviceSwitchManager()

@mcp.tool()
def switch_devices(device1: int, device2: int) -> dict:
    """
    控制两个设备的开关
    
    参数:
        device1: 设备1开关状态，0=关闭，1=开启
        device2: 设备2开关状态，0=关闭，1=开启
    
    返回:
        包含操作结果的字典
    """
    try:
        # 检查MQTT是否可用
        if not device_manager.available:
            return {
                "success": False,
                "message": "MQTT功能未启用或配置缺失，请在config.json中配置mqtt部分",
                "data": {"device1": device1, "device2": device2}
            }
        
        # 验证参数
        if device1 not in [0, 1] or device2 not in [0, 1]:
            return {
                "success": False,
                "message": "设备状态必须是0（关闭）或1（开启）",
                "data": {"device1": device1, "device2": device2}
            }
        
        # 发送控制命令
        success, message = device_manager.switch_devices(device1, device2)
        
        return {
            "success": success,
            "message": message,
            "data": {
                "device1": device1,
                "device2": device2,
                "payload": {"device1": device1, "device2": device2}
            }
        }
        
    except Exception as e:
        logger.error(f"设备控制失败: {e}")
        return {
            "success": False,
            "message": f"设备控制异常: {str(e)}",
            "data": {"device1": device1, "device2": device2}
        }

@mcp.tool()
def get_device_status() -> dict:
    """
    获取设备状态信息
    
    返回:
        包含设备状态的字典
    """
    try:
        # 检查MQTT是否可用
        if not device_manager.available:
            return {
                "success": False,
                "message": "MQTT功能未启用或配置缺失，请在config.json中配置mqtt部分",
                "data": {}
            }
            
        status = device_manager.get_last_status()
        
        if status:
            return {
                "success": True,
                "message": "获取设备状态成功",
                "data": status
            }
        else:
            return {
                "success": False,
                "message": "暂无设备状态信息",
                "data": {}
            }
            
    except Exception as e:
        logger.error(f"获取设备状态失败: {e}")
        return {
            "success": False,
            "message": f"获取设备状态异常: {str(e)}",
            "data": {}
        }

@mcp.tool()
def connect_mqtt(broker: str = None, port: int = None) -> dict:
    """
    连接到MQTT服务器
    
    参数:
        broker: MQTT服务器地址（可选）
        port: MQTT服务器端口（可选）
    
    返回:
        连接结果
    """
    try:
        # 检查MQTT是否可用
        if not device_manager.available:
            return {
                "success": False,
                "message": "MQTT功能未启用或配置缺失，请在config.json中配置mqtt部分",
                "data": {}
            }
        
        # 如果传入了新的broker和port，临时更新配置
        if broker or port:
            global mqtt_config
            if broker:
                mqtt_config['broker'] = broker
            if port:
                mqtt_config['port'] = port
            
        success = device_manager.connect()
        
        if success:
            return {
                "success": True,
                "message": f"已连接到MQTT服务器 {mqtt_config['broker']}:{mqtt_config['port']}",
                "data": {"broker": mqtt_config['broker'], "port": mqtt_config['port']}
            }
        else:
            return {
                "success": False,
                "message": f"连接MQTT服务器失败 {mqtt_config['broker']}:{mqtt_config['port']}",
                "data": {"broker": mqtt_config['broker'], "port": mqtt_config['port']}
            }
            
    except Exception as e:
        logger.error(f"MQTT连接异常: {e}")
        return {
            "success": False,
            "message": f"MQTT连接异常: {str(e)}",
            "data": {}
        }

@mcp.tool()
def get_connection_status() -> dict:
    """
    获取MQTT连接状态信息
    
    返回:
        连接状态信息
    """
    try:
        status = device_manager.get_connection_status()
        
        return {
            "success": True,
            "message": "获取连接状态成功",
            "data": status
        }
        
    except Exception as e:
        logger.error(f"获取连接状态失败: {e}")
        return {
            "success": False,
            "message": f"获取连接状态异常: {str(e)}",
            "data": {}
        }

@mcp.tool()
def stop_reconnect() -> dict:
    """
    停止自动重连
    
    返回:
        操作结果
    """
    try:
        device_manager.stop_reconnect()
        
        return {
            "success": True,
            "message": "已停止自动重连",
            "data": {}
        }
        
    except Exception as e:
        logger.error(f"停止重连失败: {e}")
        return {
            "success": False,
            "message": f"停止重连异常: {str(e)}",
            "data": {}
        }

# 注册程序退出时的清理函数
import atexit
atexit.register(device_manager.cleanup)

if __name__ == "__main__":
    mcp.run(transport="stdio") 