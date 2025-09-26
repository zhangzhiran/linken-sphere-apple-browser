#!/usr/bin/env python3
"""
最终测试停止会话功能
"""

import requests
import json
import time
from linken_sphere_api import LinkenSphereAPI

def test_stop_session_final():
    """最终测试停止会话功能"""
    print("🧪 最终停止会话测试")
    print("=" * 50)
    
    # 初始化API
    api = LinkenSphereAPI()
    
    # 获取配置文件
    profiles = api.get_profiles()
    if not profiles:
        print("❌ 没有找到配置文件")
        return
    
    profile = profiles[0]
    profile_name = profile.get('name', 'Unknown')
    profile_uuid = profile.get('uuid')
    
    print(f"🚀 使用配置: {profile_name}")
    print(f"   UUID: {profile_uuid}")
    
    try:
        # 启动会话
        print("\n1️⃣ 启动会话...")
        session_info = api.start_session(profile_uuid)
        
        if not session_info:
            print("❌ 启动会话失败")
            return
        
        debug_port = session_info.get('debug_port')
        print(f"✅ 会话启动成功，Debug Port: {debug_port}")
        
        # 等待会话完全启动
        print("\n2️⃣ 等待会话启动...")
        time.sleep(3)
        
        # 检查会话状态
        status = check_session_status(profile_uuid)
        if status != 'automationRunning':
            print(f"⚠️ 会话状态异常: {status}")
        
        # 使用修复后的API停止会话
        print("\n3️⃣ 使用修复后的API停止会话...")
        print("   (使用30秒超时)")
        
        success = api.stop_session(profile_uuid)
        
        if success:
            print("✅ 停止会话成功!")
        else:
            print("❌ 停止会话失败")
        
        # 等待并检查最终状态
        print("\n4️⃣ 检查最终状态...")
        time.sleep(3)
        final_status = check_session_status(profile_uuid)
        
        if final_status == 'stopped':
            print("✅ 会话已成功停止")
        else:
            print(f"⚠️ 会话状态: {final_status}")
        
    except Exception as e:
        print(f"❌ 测试异常: {e}")
        import traceback
        traceback.print_exc()

def check_session_status(profile_uuid):
    """检查会话状态"""
    try:
        url = "http://127.0.0.1:36555/sessions"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            sessions = response.json()
            for session in sessions:
                if session.get('uuid') == profile_uuid:
                    status = session.get('status', 'Unknown')
                    print(f"   📊 状态: {status}")
                    return status
        
        print("   ❌ 未找到会话")
        return None
        
    except Exception as e:
        print(f"   ❌ 检查状态异常: {e}")
        return None

def test_manual_stop_correct_format():
    """手动测试正确格式的停止API"""
    print("\n🔍 手动测试正确格式...")
    
    # 获取配置文件
    api = LinkenSphereAPI()
    profiles = api.get_profiles()
    if not profiles:
        return
    
    profile_uuid = profiles[0].get('uuid')
    
    # 启动会话
    print("   启动会话...")
    session_info = api.start_session(profile_uuid)
    if not session_info:
        return
    
    time.sleep(2)
    
    # 手动测试正确格式
    try:
        url = "http://127.0.0.1:36555/sessions/stop"
        data = {"uuid": profile_uuid}
        
        print(f"   POST {url}")
        print(f"   数据: {data}")
        
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        # 使用30秒超时
        response = requests.post(url, json=data, headers=headers, timeout=30)
        
        print(f"   状态码: {response.status_code}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print(f"   响应: {result}")
                if result.get('success'):
                    print("   ✅ 手动测试成功!")
                    return True
            except:
                print(f"   响应文本: {response.text}")
                if "success" in response.text.lower():
                    print("   ✅ 手动测试可能成功!")
                    return True
        else:
            print(f"   ❌ 失败: {response.text}")
            
    except Exception as e:
        print(f"   ❌ 异常: {e}")
        if "timeout" in str(e).lower():
            print("   ⚠️ 超时，但操作可能仍在进行...")
            time.sleep(3)
            status = check_session_status(profile_uuid)
            if status == 'stopped':
                print("   ✅ 会话已停止，操作成功!")
                return True
    
    return False

def main():
    """主函数"""
    print("🧪 Linken Sphere 停止会话最终测试")
    print("=" * 60)
    
    # 测试修复后的API
    test_stop_session_final()
    
    print("\n" + "=" * 60)
    
    # 手动测试正确格式
    test_manual_stop_correct_format()

if __name__ == "__main__":
    main()
