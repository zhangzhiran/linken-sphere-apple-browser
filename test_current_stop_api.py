#!/usr/bin/env python3
"""
测试当前的停止会话API功能
"""

import requests
import json
import time
from linken_sphere_api import LinkenSphereAPI

def test_current_stop_functionality():
    """测试当前的停止会话功能"""
    print("🧪 测试当前停止会话功能")
    print("=" * 50)
    
    # 初始化API
    api = LinkenSphereAPI()
    
    # 获取配置文件
    print("📋 获取配置文件...")
    profiles = api.get_profiles()
    
    if not profiles:
        print("❌ 没有找到配置文件")
        return
    
    print(f"✅ 找到 {len(profiles)} 个配置文件")
    for i, profile in enumerate(profiles):
        print(f"   {i+1}. {profile.get('name')} ({profile.get('status')})")
    
    # 使用第一个配置文件
    profile = profiles[0]
    profile_name = profile.get('name', 'Unknown')
    profile_uuid = profile.get('uuid')
    
    print(f"\n🚀 使用配置: {profile_name}")
    print(f"   UUID: {profile_uuid}")
    
    try:
        # 启动会话
        print("\n1️⃣ 启动会话...")
        session_info = api.start_session(profile_uuid)
        
        if not session_info:
            print("❌ 启动会话失败")
            return
        
        session_id = session_info.get('session_id')
        debug_port = session_info.get('debug_port')
        
        print(f"✅ 会话启动成功:")
        print(f"   Session ID: {session_id}")
        print(f"   Debug Port: {debug_port}")
        
        # 等待几秒钟让会话完全启动
        print("\n⏳ 等待会话完全启动...")
        time.sleep(3)
        
        # 测试停止会话 - 使用profile_uuid而不是session_id
        print("\n2️⃣ 测试停止会话...")
        print(f"   使用Profile UUID: {profile_uuid}")
        success = api.stop_session(profile_uuid)

        if success:
            print("✅ 停止会话成功!")
        else:
            print("❌ 停止会话失败")

            # 如果失败，尝试手动测试不同的API端点
            print("\n🔍 尝试手动测试停止API...")
            test_manual_stop_api(profile_uuid)
        
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

def test_manual_stop_api(profile_uuid):
    """手动测试停止API的不同格式"""
    base_url = "http://127.0.0.1:36555"

    # 测试不同的停止端点 - 使用uuid字段
    stop_endpoints = [
        ("/stop", {"uuid": profile_uuid}),
        ("/sessions/stop", {"uuid": profile_uuid}),
        ("/sessions/stop", {"session_id": profile_uuid}),
        (f"/sessions/{profile_uuid}/stop", {}),
        ("/session/stop", {"uuid": profile_uuid}),
        (f"/session/{profile_uuid}/stop", {}),
    ]
    
    for endpoint, data in stop_endpoints:
        try:
            print(f"   测试: POST {endpoint}")
            url = f"{base_url}{endpoint}"
            
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
            
            response = requests.post(url, json=data, headers=headers, timeout=10)
            print(f"      状态码: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    result = response.json()
                    print(f"      响应: {result}")
                    if result.get('success'):
                        print(f"      ✅ 端点 {endpoint} 成功!")
                        return True
                except:
                    print(f"      响应文本: {response.text}")
            else:
                print(f"      ❌ 失败: {response.text}")
                
        except Exception as e:
            print(f"      ❌ 异常: {e}")
    
    return False

def check_session_status():
    """检查当前会话状态"""
    print("\n📊 检查当前会话状态...")
    
    try:
        url = "http://127.0.0.1:36555/sessions"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            sessions = response.json()
            print(f"✅ 当前会话状态:")
            for session in sessions:
                name = session.get('name', 'Unknown')
                status = session.get('status', 'Unknown')
                uuid = session.get('uuid', 'Unknown')
                print(f"   - {name}: {status} ({uuid[:8]}...)")
        else:
            print(f"❌ 获取会话状态失败: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 检查会话状态异常: {e}")

def main():
    """主函数"""
    print("🧪 Linken Sphere 停止会话API测试")
    print("=" * 60)
    
    # 检查初始状态
    check_session_status()
    
    # 测试停止功能
    test_current_stop_functionality()
    
    # 检查最终状态
    check_session_status()

if __name__ == "__main__":
    main()
