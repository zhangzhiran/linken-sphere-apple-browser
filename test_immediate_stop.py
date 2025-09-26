#!/usr/bin/env python3
"""
立即测试停止会话功能 - 在会话启动后立即测试停止
"""

import requests
import json
import time
import threading
from linken_sphere_api import LinkenSphereAPI

def monitor_session_status(profile_uuid, stop_event):
    """监控会话状态的线程"""
    while not stop_event.is_set():
        try:
            url = "http://127.0.0.1:36555/sessions"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                sessions = response.json()
                for session in sessions:
                    if session.get('uuid') == profile_uuid:
                        status = session.get('status', 'unknown')
                        print(f"   📊 会话状态: {status}")
                        break
            
            time.sleep(1)  # 每秒检查一次
            
        except Exception as e:
            print(f"   ❌ 监控异常: {e}")
            break

def test_immediate_stop():
    """立即测试停止会话功能"""
    print("🧪 立即停止会话测试")
    print("=" * 50)
    
    # 初始化API
    api = LinkenSphereAPI()
    
    # 获取配置文件
    print("📋 获取配置文件...")
    profiles = api.get_profiles()
    
    if not profiles:
        print("❌ 没有找到配置文件")
        return
    
    # 使用第一个配置文件
    profile = profiles[0]
    profile_name = profile.get('name', 'Unknown')
    profile_uuid = profile.get('uuid')
    
    print(f"🚀 使用配置: {profile_name}")
    print(f"   UUID: {profile_uuid}")
    
    # 启动状态监控线程
    stop_monitor = threading.Event()
    monitor_thread = threading.Thread(
        target=monitor_session_status, 
        args=(profile_uuid, stop_monitor)
    )
    monitor_thread.daemon = True
    monitor_thread.start()
    
    try:
        print("\n1️⃣ 启动会话...")
        session_info = api.start_session(profile_uuid)
        
        if not session_info:
            print("❌ 启动会话失败")
            return
        
        debug_port = session_info.get('debug_port')
        print(f"✅ 会话启动成功，Debug Port: {debug_port}")
        
        # 立即检查会话状态
        print("\n2️⃣ 检查会话状态...")
        check_session_status(profile_uuid)
        
        # 等待1秒确保会话完全启动
        print("\n⏳ 等待1秒...")
        time.sleep(1)
        
        # 立即测试停止
        print("\n3️⃣ 立即测试停止会话...")
        success = test_stop_with_different_methods(profile_uuid)
        
        if success:
            print("✅ 停止会话成功!")
        else:
            print("❌ 停止会话失败")
        
        # 最终检查状态
        print("\n4️⃣ 最终状态检查...")
        time.sleep(2)
        check_session_status(profile_uuid)
        
    except Exception as e:
        print(f"❌ 测试异常: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # 停止监控线程
        stop_monitor.set()

def check_session_status(profile_uuid):
    """检查特定会话的状态"""
    try:
        url = "http://127.0.0.1:36555/sessions"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            sessions = response.json()
            for session in sessions:
                if session.get('uuid') == profile_uuid:
                    name = session.get('name', 'Unknown')
                    status = session.get('status', 'Unknown')
                    print(f"   📊 {name}: {status}")
                    return status
        
        print("   ❌ 未找到会话")
        return None
        
    except Exception as e:
        print(f"   ❌ 检查状态异常: {e}")
        return None

def test_stop_with_different_methods(profile_uuid):
    """使用不同方法测试停止会话"""
    base_url = "http://127.0.0.1:36555"
    
    # 测试方法列表
    stop_methods = [
        ("POST /sessions/stop (uuid)", "/sessions/stop", {"uuid": profile_uuid}),
        ("POST /sessions/stop (session_id)", "/sessions/stop", {"session_id": profile_uuid}),
        ("POST /stop (uuid)", "/stop", {"uuid": profile_uuid}),
        (f"POST /sessions/{profile_uuid}/stop", f"/sessions/{profile_uuid}/stop", {}),
    ]
    
    for method_name, endpoint, data in stop_methods:
        try:
            print(f"   🔍 测试: {method_name}")
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
                        print(f"      ✅ {method_name} 成功!")
                        return True
                    else:
                        print(f"      ⚠️ {method_name} 响应但未成功")
                except:
                    print(f"      响应文本: {response.text}")
                    if "success" in response.text.lower():
                        print(f"      ✅ {method_name} 可能成功!")
                        return True
            else:
                try:
                    error_info = response.json()
                    print(f"      ❌ 错误: {error_info}")
                except:
                    print(f"      ❌ 错误: {response.text}")
                
        except Exception as e:
            print(f"      ❌ 异常: {e}")
    
    return False

def test_api_discovery():
    """发现正确的API端点"""
    print("\n🔍 API端点发现...")
    
    base_url = "http://127.0.0.1:36555"
    
    # 测试不同的端点
    endpoints = [
        "/sessions",
        "/sessions/start", 
        "/sessions/stop",
        "/stop",
        "/api",
        "/help"
    ]
    
    for endpoint in endpoints:
        try:
            # 测试GET
            url = f"{base_url}{endpoint}"
            response = requests.get(url, timeout=5)
            print(f"GET {endpoint}: {response.status_code}")
            
            # 测试POST（如果GET失败）
            if response.status_code == 404:
                try:
                    response = requests.post(url, json={}, timeout=5)
                    print(f"POST {endpoint}: {response.status_code}")
                except:
                    pass
                    
        except Exception as e:
            print(f"{endpoint}: 连接失败")

def main():
    """主函数"""
    print("🧪 Linken Sphere 立即停止测试")
    print("=" * 60)
    
    # 首先发现API端点
    test_api_discovery()
    
    print("\n" + "=" * 60)
    
    # 然后测试立即停止
    test_immediate_stop()

if __name__ == "__main__":
    main()
