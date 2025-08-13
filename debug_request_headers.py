"""请求头调试脚本 #"""
import asyncio
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def debug_request_headers():
    """调试请求头 #"""
    print("🔍 开始调试请求头...")  # 开始调试 #
    
    try:
        # 导入相关模块
        from mcpserver.agent_naga_portal.portal_login_manager import auto_login_naga_portal
        from mcpserver.agent_naga_portal.client import NagaPortalClient
        from mcpserver.agent_naga_portal.cookie_manager import get_cookies
        
        # 1. 确保登录
        await auto_login_naga_portal()
        
        # 2. 获取cookie
        cookies = get_cookies()
        
        # 3. 创建客户端
        client = NagaPortalClient()
        client.set_cookies(cookies)
        
        # 4. 确保客户端初始化
        await client._ensure_client()
        
        # 5. 检查客户端状态
        print("\n📊 客户端状态:")
        print(f"   Base URL: {client.base_url}")
        print(f"   Client: {client._client}")
        print(f"   Cookies: {dict(client._client.cookies)}")
        print(f"   Headers: {client._client.headers}")
        
        # 6. 构建充值载荷
        import time
        import random
        out_trade_no = f"USR{random.randint(1000, 9999)}NO{int(time.time())}"
        
        payload = {
            "data": {
                "device": "pc",
                "money": "11.00",
                "name": "TUC1100",
                "notify_url": "https://naga.furina.chat/api/user/epay/notify",
                "out_trade_no": out_trade_no,
                "pid": "1001",
                "return_url": "https://naga.furina.chat/log",
                "sign": "e37a7320730ddb2efb66ccce45752a97",
                "sign_type": "MD5",
                "type": "wxpay"
            },
            "message": "success",
            "url": "https://pay.furina.chat/submit.php"
        }
        
        # 7. 发送请求并检查详细信息
        print("\n🌐 发送充值请求:")
        try:
            resp = await client._client.post("/api/user/pay", json=payload)
            
            print(f"   请求URL: {resp.request.url}")
            print(f"   请求方法: {resp.request.method}")
            print(f"   请求头: {dict(resp.request.headers)}")
            print(f"   状态码: {resp.status_code}")
            print(f"   响应头: {dict(resp.headers)}")
            print(f"   响应内容: {resp.text[:500]}")
            
            # 检查cookie是否正确发送
            if 'cookie' in resp.request.headers:
                print(f"   发送的Cookie: {resp.request.headers['cookie']}")
            else:
                print("   未发送Cookie")
                
        except Exception as e:
            print(f"   请求失败: {e}")
            import traceback
            traceback.print_exc()
        
        print("\n✅ 请求头调试完成！")  # 完成调试 #
        
    except Exception as e:
        print(f"❌ 调试失败: {e}")  # 调试失败 #
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_request_headers())
