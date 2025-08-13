"""测试兑换码功能 #"""
import asyncio  # 异步 #
import json  # JSON #
from portal_login_manager import set_cookies, set_user_id  # 登录管理器 #
from naga_portal_agent import NagaPortalAgent  # Agent #

async def test_redeem_code():  # 测试兑换码 #
    """测试兑换码功能 #"""
    
    # 设置测试数据 #
    test_cookies = {
        "session": "MTc1NDc1MTM3NnxEWDhFQVFMX2dBQUJFQUVRQUFEX2pQLUFBQVVHYzNSeWFXNW5EQWNBQldkeWIzVndCbk4wY21sdVp3d0pBQWRrWldaaGRXeDBCbk4wY21sdVp3d0VBQUpwWkFOcGJuUUVBZ0JzQm5OMGNtbHVad3dLQUFoMWMyVnlibUZ0WlFaemRISnBibWNNQlFBRFlXRmhCbk4wY21sdVp3d0dBQVJ5YjJ4bEEybHVkQVFDQUFJR2MzUnlhVzVuREFnQUJuTjBZWFIxY3dOcGJuUUVBZ0FDfAyGHYLFMulRtmQFEThwEW5ChvC8Si_R_PGfpeS_q3F5",
        "sl-session": "5yqgRCFwm2gjCLsIVnY8Jg=="
    }
    
    # 设置cookie和用户ID #
    set_cookies(test_cookies)  # 设置cookie #
    set_user_id(54)  # 设置用户ID #
    
    print("🍪 已设置测试数据")  # 调试信息 #
    print(f"Cookie: {test_cookies}")  # 显示cookie #
    print(f"User ID: 54")  # 显示用户ID #
    
    # 创建Agent #
    agent = NagaPortalAgent()  # 创建Agent #
    
    try:
        # 测试兑换码请求 #
        print("\n🚀 开始测试兑换码请求...")  # 调试信息 #
        
        # 构建测试数据 #
        test_data = {
            "tool_name": "naga_redeem_code",
            "key": "aaaa"
        }  # 测试数据 #
        
        # 调用Agent #
        result = await agent.handle_handoff(test_data)  # 调用Agent #
        
        print(f"\n📋 Agent返回结果:")  # 调试信息 #
        print(result)  # 显示结果 #
        
        # 解析结果 #
        try:
            result_json = json.loads(result)
            if result_json.get("success"):
                print("✅ 兑换码调用成功！")  # 成功信息 #
                if result_json.get("status") == "redeem_success":
                    print("🎉 兑换码使用成功！")  # 成功信息 #
                else:
                    print(f"⚠️ 兑换码状态: {result_json.get('status')}")  # 状态信息 #
            else:
                print("❌ 兑换码调用失败！")  # 失败信息 #
        except json.JSONDecodeError:
            print("❌ 结果解析失败！")  # 解析失败 #
            
    except Exception as e:
        print(f"❌ 测试异常: {e}")  # 异常信息 #
    finally:
        await agent.close()  # 关闭Agent #

if __name__ == "__main__":
    asyncio.run(test_redeem_code())  # 运行测试 #
