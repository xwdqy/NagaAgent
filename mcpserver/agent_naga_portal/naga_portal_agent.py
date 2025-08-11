"""NagaPortal MCP Agent #"""
import json  # JSON #
from typing import Any, Dict, Optional  # 类型 #
import asyncio  # 异步 #
from config import config  # 全局配置 #
from .client import NagaPortalClient  # 客户端封装 #


class NagaPortalAgent:
    """娜迦官网API Agent(基础骨架) #"""

    name = "NagaPortalAgent"  # 名称 #
    instructions = "与娜迦官网API交互，支持登录/GET/POST等基础操作"  # 描述 #

    def __init__(self):  # 初始化 #
        self.client = NagaPortalClient(base_url=config.naga_portal.portal_url)  # 客户端 #
        
        # 尝试从全局登录管理器获取cookie
        try:
            from .portal_login_manager import get_portal_login_manager
            manager = get_portal_login_manager()
            if manager.is_logged_in:
                cookies = manager.get_cookies()
                if cookies:
                    self.client.set_cookies(cookies)
        except Exception as e:
            # 如果获取失败，不影响正常使用
            pass

    async def handle_handoff(self, data: dict) -> str:  # 统一入口 #
        tool = data.get("tool_name")  # 工具名 #
        try:
            # 通用设置工具 #
            if tool == "set_bearer_token":
                token = data.get("token")  # 令牌 #
                if not token:
                    return json.dumps({"success": False, "status": "invalid_args", "message": "缺少token参数", "data": {}}, ensure_ascii=False)
                self.client.set_bearer_token(token)
                return json.dumps({"success": True, "status": "ok", "message": "已设置Bearer Token", "data": {}}, ensure_ascii=False)

            if tool == "set_headers":
                headers = data.get("headers") or {}
                if not isinstance(headers, dict):
                    return json.dumps({"success": False, "status": "invalid_args", "message": "headers需为对象", "data": {}}, ensure_ascii=False)
                self.client.set_headers(headers)
                return json.dumps({"success": True, "status": "ok", "message": "已更新headers", "data": {}}, ensure_ascii=False)

            if tool == "set_cookies":
                cookies = data.get("cookies") or {}
                if not isinstance(cookies, dict):
                    return json.dumps({"success": False, "status": "invalid_args", "message": "cookies需为对象", "data": {}}, ensure_ascii=False)
                self.client.set_cookies(cookies)
                return json.dumps({"success": True, "status": "ok", "message": "已更新cookies", "data": {}}, ensure_ascii=False)

            if tool == "naga_request":
                method = data.get("method", "GET")
                path = data.get("path")
                params = data.get("params")
                body = data.get("json")
                headers = data.get("headers")
                if not path:
                    return json.dumps({"success": False, "status": "invalid_args", "message": "缺少path参数", "data": {}}, ensure_ascii=False)
                res = await self.client.request(method, path, params=params, json_body=body, headers=headers)
                return json.dumps(res, ensure_ascii=False)

            if tool == "naga_login":
                username = data.get("username")  # 用户名 #
                password = data.get("password")  # 密码 #
                login_path = data.get("login_path")  # 登录路径 #
                res = await self.client.login(username=username, password=password, login_path=login_path)  # 登录 #
                return json.dumps(res, ensure_ascii=False)  # 返回 #

            if tool == "naga_get":
                path = data.get("path")  # 路径 #
                params = data.get("params")  # 参数 #
                if not path:
                    return json.dumps({"success": False, "status": "invalid_args", "message": "缺少path参数", "data": {}}, ensure_ascii=False)  # 校验 #
                res = await self.client.get(path, params=params)
                return json.dumps(res, ensure_ascii=False)

            if tool == "naga_post":
                path = data.get("path")  # 路径 #
                body = data.get("json")  # JSON体 #
                if not path:
                    return json.dumps({"success": False, "status": "invalid_args", "message": "缺少path参数", "data": {}}, ensure_ascii=False)  # 校验 #
                res = await self.client.post(path, json_body=body)
                return json.dumps(res, ensure_ascii=False)

            if tool == "get_user_info":
                res = await self.client.get_profile()  # 获取资料 #
                return json.dumps(res, ensure_ascii=False)

            if tool == "naga_logout":
                res = await self.client.logout()  # 登出 #
                return json.dumps(res, ensure_ascii=False)

            return json.dumps({"success": False, "status": "unknown_tool", "message": f"未知工具: {tool}", "data": {}}, ensure_ascii=False)  # 未知 #
        except Exception as e:
            return json.dumps({"success": False, "status": "exception", "message": str(e), "data": {}}, ensure_ascii=False)  # 异常 #


# 工厂方法 #
def create_naga_portal_agent(config_dict: Optional[Dict[str, Any]] = None) -> NagaPortalAgent:
    return NagaPortalAgent()  # 返回实例 #


# 配置校验 #
def validate_agent_config(config_dict: Dict[str, Any]) -> bool:
    return True  # 预留校验，基础骨架总是通过 #


# 依赖 #
def get_agent_dependencies():
    return [
        "httpx>=0.28.1"  # HTTP客户端 #
    ]  # 依赖列表 #


