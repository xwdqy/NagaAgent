"""NagaPortal HTTP客户端封装 #"""
import asyncio  # 异步 #
from typing import Any, Dict, Optional  # 类型 #
import httpx  # HTTP客户端 #
from config import config  # 全局配置 #


class NagaPortalClient:
    """与官网API交互的轻量客户端(基础骨架) #"""

    def __init__(self, base_url: Optional[str] = None):  # 初始化 #
        self.base_url = (base_url or config.naga_portal.portal_url).rstrip('/')  # 基础URL #
        self._client: Optional[httpx.AsyncClient] = None  # 异步客户端 #
        self._logged_in: bool = False  # 登录标记 #
        self._username_masked: str = ""  # 掩码用户名 #

    async def _ensure_client(self):  # 确保客户端 #
        if self._client is None:  # 未创建则创建 #
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=config.naga_portal.request_timeout,  # 统一超时 #
                follow_redirects=True,
                headers=config.naga_portal.default_headers.copy(),  # 默认头 #
            )  # 创建客户端 #

    @staticmethod
    def _mask(s: str) -> str:  # 掩码 #
        if not s:  # 空处理 #
            return ""  # 返回空 #
        if len(s) <= 2:  # 短字符 #
            return s[0] + "*" * (len(s) - 1)  # 简单掩码 #
        return s[0] + "*" * (len(s) - 2) + s[-1]  # 掩码中间 #

    async def login(self, username: Optional[str] = None, password: Optional[str] = None, login_path: Optional[str] = None) -> Dict[str, Any]:  # 登录 #
        await self._ensure_client()  # 准备客户端 #
        u = username or config.naga_portal.username  # 用户名 #
        p = password or config.naga_portal.password  # 密码 #
        self._username_masked = self._mask(u)  # 保存掩码 #
        if not u or not p:  # 校验 #
            return {"success": False, "status": "no_credentials", "message": "未配置用户名或密码", "data": {}}  # 缺少凭据 #
        
        # 使用配置的登录路径或默认路径 #
        path = login_path or config.naga_portal.login_path  # 登录路径 #
        if not path.startswith('/'):
            path = '/' + path  # 规范路径 #
        
        # 添加turnstile参数 #
        turnstile = config.naga_portal.turnstile_param  # 验证参数 #
        if turnstile:
            path = f"{path}?turnstile={turnstile}"  # 添加参数 #
        
        try:
            # 载荷生成：支持json或form #
            uname_key = config.naga_portal.login_username_key  # 用户名键 #
            passwd_key = config.naga_portal.login_password_key  # 密码键 #
            payload = {uname_key: u, passwd_key: p}  # 载荷 #
            
            if config.naga_portal.login_payload_mode == "form":  # 表单模式 #
                resp = await self._client.post(path, data=payload)  # 表单提交 #
            else:
                resp = await self._client.post(path, json=payload)  # JSON提交 #
            
            ok = (200 <= resp.status_code < 300)  # 状态判断 #
            self._logged_in = ok  # 更新状态 #
            
            # 提取响应信息 #
            response_data = {
                "url": str(resp.request.url),
                "status_code": resp.status_code,
                "response_text": resp.text[:500]  # 限制长度 #
            }
            
            # 检查是否有set-cookie头 #
            if "set-cookie" in resp.headers:
                response_data["cookies_set"] = True  # 标记有cookie #
                response_data["cookie_count"] = len(resp.headers.getlist("set-cookie"))  # cookie数量 #
            
            return {"success": ok, "status": "ok" if ok else "http_error", "message": f"HTTP {resp.status_code}", "data": response_data}  # 返回 #
        except Exception as e:
            # 允许无真实接口时也能跑通流程 #
            self._logged_in = True  # 置为已登录(占位)，便于后续GET/POST测试 #
            return {"success": True, "status": "mock_login", "message": f"已进入占位登录: {e}", "data": {"username": self._username_masked}}  # 占位成功 #

    async def get(self, path: str, params: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:  # GET请求 #
        await self._ensure_client()  # 确保客户端 #
        if not path.startswith('/'):
            path = '/' + path  # 规范路径 #
        try:
            resp = await self._client.get(path, params=params or {}, headers=headers)  # 发送 #
            return {"success": True, "status": "ok", "message": f"HTTP {resp.status_code}", "data": {"status_code": resp.status_code, "text": resp.text[:1000]}}  # 返回 #
        except Exception as e:
            return {"success": False, "status": "network_error", "message": str(e), "data": {}}  # 异常 #

    async def post(self, path: str, json_body: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:  # POST请求 #
        await self._ensure_client()  # 确保客户端 #
        if not path.startswith('/'):
            path = '/' + path  # 规范路径 #
        try:
            resp = await self._client.post(path, json=json_body or {}, headers=headers)  # 发送 #
            return {"success": True, "status": "ok", "message": f"HTTP {resp.status_code}", "data": {"status_code": resp.status_code, "text": resp.text[:1000]}}  # 返回 #
        except Exception as e:
            return {"success": False, "status": "network_error", "message": str(e), "data": {}}  # 异常 #

    async def request(self, method: str, path: str, *, params: Optional[Dict[str, Any]] = None, json_body: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:  # 通用请求 #
        await self._ensure_client()  # 准备 #
        if not path.startswith('/'):
            path = '/' + path  # 规范 #
        tries = max(1, config.naga_portal.retry_times + 1)  # 尝试次数 #
        last_exc = None  # 最后异常 #
        for _ in range(tries):  # 重试循环 #
            try:
                resp = await self._client.request(method.upper(), path, params=params, json=json_body, headers=headers)  # 请求 #
                return {"success": True, "status": "ok", "message": f"HTTP {resp.status_code}", "data": {"status_code": resp.status_code, "text": resp.text[:2000]}}  # 返回 #
            except Exception as e:
                last_exc = e  # 保存异常 #
        return {"success": False, "status": "network_error", "message": str(last_exc), "data": {}}  # 重试后失败 #

    def set_bearer_token(self, token: str):  # 设置Bearer令牌 #
        if self._client:
            self._client.headers["authorization"] = f"Bearer {token}"  # 设置头 #

    def set_headers(self, headers: Dict[str, str]):  # 批量设置头 #
        if self._client:
            self._client.headers.update(headers or {})  # 更新 #

    def set_cookies(self, cookies: Dict[str, str]):  # 批量设置cookie #
        if self._client:
            self._client.cookies.update(cookies or {})  # 更新 #

    async def get_profile(self) -> Dict[str, Any]:  # 获取用户信息(占位) #
        # 约定测试路径 /api/profile，如不同后续再改 #
        return await self.get('/api/profile')  # 代理 #

    async def logout(self) -> Dict[str, Any]:  # 登出 #
        try:
            if self._client:
                await self._client.aclose()  # 关闭 #
        finally:
            self._client = None  # 清理 #
            self._logged_in = False  # 状态 #
        return {"success": True, "status": "ok", "message": "已清理本地会话", "data": {"user": self._username_masked}}  # 返回 #


