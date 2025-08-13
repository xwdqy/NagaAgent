"""API响应调试脚本 #"""
import asyncio
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def debug_api_response():
    """调试API响应 #"""
    print("🔍 开始调试API响应...")  # 开始调试 #
    
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
        await client._ensure_client()
        
        # 4. 获取用户ID
        from mcpserver.agent_naga_portal.cookie_manager import get_user_id
        user_id = get_user_id()
        print(f"用户ID: {user_id}")
        
        # 5. 测试充值请求
        import time
        import random
        out_trade_no = f"USR{random.randint(1000, 9999)}NO{int(time.time())}"
        
        payload = {
            "data": {
                "device": "pc",
                "money": "1000.00",  # 测试1000元
                "name": "TUC100000",
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
        
        headers = {"User-id": str(user_id)} if user_id else {}
        
        print(f"请求载荷: {payload}")
        print(f"请求头: {headers}")
        
        # 6. 发送请求
        resp = await client._client.post("/api/user/pay", json=payload, headers=headers)
        
        print(f"状态码: {resp.status_code}")
        print(f"响应头: {dict(resp.headers)}")
        print(f"完整响应内容: {resp.text}")
        
        # 7. 解析响应
        try:
            import json
            response_data = json.loads(resp.text)
            print(f"解析后的响应: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
        except Exception as e:
            print(f"响应解析失败: {e}")
        
        print("\n✅ API响应调试完成！")  # 完成调试 #
        
    except Exception as e:
        print(f"❌ 调试失败: {e}")  # 调试失败 #
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_api_response())
