"""NagaPortal自动登录管理器 #"""
import asyncio  # 异步 #
import logging  # 日志 #
from typing import Optional, Dict, Any  # 类型 #
from .client import NagaPortalClient  # 客户端 #
from config import config  # 配置 #

logger = logging.getLogger("NagaPortalLoginManager")

class NagaPortalLoginManager:
    """娜迦官网自动登录管理器 #"""
    
    def __init__(self):  # 初始化 #
        self.client: Optional[NagaPortalClient] = None  # 客户端 #
        self.is_logged_in: bool = False  # 登录状态 #
        self.login_error: Optional[str] = None  # 登录错误 #
        self.cookies: Dict[str, str] = {}  # Cookie存储 #
        
    async def auto_login(self) -> Dict[str, Any]:  # 自动登录 #
        """自动登录娜迦官网 #"""
        try:
            # 检查配置 #
            if not config.naga_portal.username or not config.naga_portal.password:  # 检查配置 #
                error_msg = "未配置娜迦官网用户名或密码，请在config.json中设置naga_portal.username和password"  # 错误消息 #
                logger.warning(error_msg)  # 警告日志 #
                return {
                    "success": False,
                    "status": "no_credentials",
                    "message": error_msg,
                    "data": {}
                }  # 返回 #
            
            logger.info("🔄 正在自动登录娜迦官网...")  # 登录中 #
            logger.info(f"   官网地址: {config.naga_portal.portal_url}")  # 地址 #
            logger.info(f"   用户名: {config.naga_portal.username[:3]}***{config.naga_portal.username[-3:] if len(config.naga_portal.username) > 6 else '***'}")  # 掩码用户名 #
            
            # 创建客户端 #
            self.client = NagaPortalClient()  # 客户端 #
            
            # 执行登录 #
            result = await self.client.login()  # 登录 #
            
            if result['success']:  # 成功 #
                self.is_logged_in = True  # 更新状态 #
                self.login_error = None  # 清除错误 #
                
                # 提取cookie信息 #
                data = result.get('data', {})  # 数据 #
                if 'cookies_set' in data:  # 有cookie #
                    cookie_count = data.get('cookie_count', 0)  # cookie数量 #
                    logger.info(f"✅ 登录成功！已设置 {cookie_count} 个Cookie")  # 成功 #
                    
                    # 保存cookie到客户端 #
                    if hasattr(self.client, '_client') and self.client._client:  # 有客户端 #
                        self.cookies = dict(self.client._client.cookies)  # 保存cookie #
                        logger.info(f"   已保存Cookie: {list(self.cookies.keys())}")  # cookie列表 #
                else:  # 无cookie #
                    logger.info("✅ 登录成功！（模拟模式）")  # 成功 #
                
                return {
                    "success": True,
                    "status": "logged_in",
                    "message": "娜迦官网自动登录成功",
                    "data": {
                        "cookie_count": data.get('cookie_count', 0),
                        "cookies": list(self.cookies.keys())
                    }
                }  # 返回 #
            else:  # 失败 #
                self.is_logged_in = False  # 更新状态 #
                self.login_error = result.get('message', '未知错误')  # 保存错误 #
                logger.error(f"❌ 登录失败: {self.login_error}")  # 错误日志 #
                
                return {
                    "success": False,
                    "status": "login_failed",
                    "message": f"娜迦官网登录失败: {self.login_error}",
                    "data": {}
                }  # 返回 #
                
        except Exception as e:  # 异常 #
            self.is_logged_in = False  # 更新状态 #
            self.login_error = str(e)  # 保存错误 #
            logger.error(f"❌ 自动登录过程中发生异常: {e}")  # 异常日志 #
            
            return {
                "success": False,
                "status": "exception",
                "message": f"自动登录异常: {str(e)}",
                "data": {}
            }  # 返回 #
    
    async def get_user_info(self) -> Dict[str, Any]:  # 获取用户信息 #
        """获取用户信息 #"""
        if not self.is_logged_in or not self.client:  # 未登录 #
            return {
                "success": False,
                "status": "not_logged_in",
                "message": "未登录，无法获取用户信息",
                "data": {}
            }  # 返回 #
        
        try:
            result = await self.client.get_profile()  # 获取资料 #
            return result  # 返回 #
        except Exception as e:  # 异常 #
            logger.error(f"获取用户信息失败: {e}")  # 错误日志 #
            return {
                "success": False,
                "status": "error",
                "message": f"获取用户信息失败: {str(e)}",
                "data": {}
            }  # 返回 #
    
    async def logout(self) -> Dict[str, Any]:  # 登出 #
        """登出娜迦官网 #"""
        if not self.client:  # 无客户端 #
            return {
                "success": True,
                "status": "not_logged_in",
                "message": "未登录，无需登出",
                "data": {}
            }  # 返回 #
        
        try:
            result = await self.client.logout()  # 登出 #
            self.is_logged_in = False  # 更新状态 #
            self.cookies.clear()  # 清除cookie #
            logger.info("✅ 已登出娜迦官网")  # 成功 #
            return result  # 返回 #
        except Exception as e:  # 异常 #
            logger.error(f"登出失败: {e}")  # 错误日志 #
            return {
                "success": False,
                "status": "error",
                "message": f"登出失败: {str(e)}",
                "data": {}
            }  # 返回 #
    
    def get_status(self) -> Dict[str, Any]:  # 获取状态 #
        """获取登录管理器状态 #"""
        return {
            "is_logged_in": self.is_logged_in,
            "login_error": self.login_error,
            "cookie_count": len(self.cookies),
            "cookies": list(self.cookies.keys()) if self.cookies else []
        }  # 返回 #
    
    def get_cookies(self) -> Dict[str, str]:  # 获取cookie #
        """获取当前保存的cookie #"""
        return self.cookies.copy()  # 返回副本 #

# 全局登录管理器实例 #
_portal_login_manager: Optional[NagaPortalLoginManager] = None

def get_portal_login_manager() -> NagaPortalLoginManager:  # 获取管理器 #
    """获取全局NagaPortal登录管理器实例 #"""
    global _portal_login_manager
    if _portal_login_manager is None:  # 未初始化 #
        _portal_login_manager = NagaPortalLoginManager()  # 创建实例 #
    return _portal_login_manager  # 返回 #

async def auto_login_naga_portal() -> Dict[str, Any]:  # 自动登录 #
    """自动登录娜迦官网的便捷函数 #"""
    manager = get_portal_login_manager()  # 获取管理器 #
    return await manager.auto_login()  # 自动登录 #
