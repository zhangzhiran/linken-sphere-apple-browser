#!/usr/bin/env python3
"""
测试Linken Sphere会话停止API的不同格式
"""

import requests
import json
import time
from linken_sphere_api import LinkenSphereAPI

def test_stop_session_formats():
    """测试不同的停止会话API格式"""
    print("🧪 测试Linken Sphere停止会话API格式")
    print("=" * 50)
    
    # 初始化API
    api = LinkenSphereAPI()
    
    # 首先获取可用的配置文件
    print("📋 获取配置文件...")
    profiles = api.get_profiles()
    
    if not profiles:
        print("❌ 没有找到配置文件")
        return
    
    print(f"✅ 找到 {len(profiles)} 个配置文件")
    
    # 使用第一个配置文件启动会话
    profile = profiles[0]
    profile_name = profile.get('name', 'Unknown')
    profile_uuid = profile.get('uuid')
    
    print(f"🚀 启动会话使用配置: {profile_name}")
    
    try:
        # 启动会话
        session_info = api.start_session(profile_uuid)
        
        if not session_info:
            print("❌ 启动会话失败")
            return
        
        session_id = session_info.get('session_id')
        debug_port = session_info.get('debug_port')
        
        print(f"✅ 会话启动成功:")
        print(f"   Session ID: {session_id}")
        print(f"   Debug Port: {debug_port}")
        
        # 等待几秒钟
        print("⏳ 等待5秒钟...")
        time.sleep(5)
        
        # 测试不同的停止API格式
        print("\n🔍 测试停止会话API格式...")
        
        # 方法1: RESTful格式 - /sessions/{session_id}/stop
        print("\n1️⃣ 测试 RESTful 格式: /sessions/{session_id}/stop")
        try:
            url = f"http://127.0.0.1:36555/sessions/{session_id}/stop"
            response = requests.post(url, json={}, timeout=10)
            print(f"   状态码: {response.status_code}")
            print(f"   响应: {response.text}")
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    print("   ✅ RESTful格式成功!")
                    return
        except Exception as e:
            print(f"   ❌ RESTful格式失败: {e}")
        
        # 方法2: 通用停止端点 - /sessions/stop
        print("\n2️⃣ 测试通用停止端点: /sessions/stop")
        try:
            url = "http://127.0.0.1:36555/sessions/stop"
            data = {'session_id': session_id}
            response = requests.post(url, json=data, timeout=10)
            print(f"   状态码: {response.status_code}")
            print(f"   响应: {response.text}")
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    print("   ✅ 通用停止端点成功!")
                    return
        except Exception as e:
            print(f"   ❌ 通用停止端点失败: {e}")
        
        # 方法3: 简单停止端点 - /stop
        print("\n3️⃣ 测试简单停止端点: /stop")
        try:
            url = "http://127.0.0.1:36555/stop"
            data = {'session_id': session_id}
            response = requests.post(url, json=data, timeout=10)
            print(f"   状态码: {response.status_code}")
            print(f"   响应: {response.text}")
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    print("   ✅ 简单停止端点成功!")
                    return
        except Exception as e:
            print(f"   ❌ 简单停止端点失败: {e}")
        
        # 方法4: 使用API类的方法
        print("\n4️⃣ 测试API类的停止方法")
        try:
            success = api.stop_session(session_id)
            if success:
                print("   ✅ API类停止方法成功!")
                return
            else:
                print("   ❌ API类停止方法失败")
        except Exception as e:
            print(f"   ❌ API类停止方法异常: {e}")
        
        # 方法5: 尝试其他可能的端点
        print("\n5️⃣ 测试其他可能的端点")
        
        other_endpoints = [
            f"/session/{session_id}/stop",
            f"/browser/{session_id}/stop",
            "/session/stop",
            "/browser/stop",
            "/close",
            "/terminate"
        ]
        
        for endpoint in other_endpoints:
            try:
                print(f"   测试: {endpoint}")
                url = f"http://127.0.0.1:36555{endpoint}"
                data = {'session_id': session_id}
                response = requests.post(url, json=data, timeout=5)
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('success'):
                        print(f"   ✅ 端点 {endpoint} 成功!")
                        return
                    else:
                        print(f"   ⚠️ 端点 {endpoint} 响应但未成功: {result}")
                else:
                    print(f"   ❌ 端点 {endpoint} 状态码: {response.status_code}")
                    
            except Exception as e:
                print(f"   ❌ 端点 {endpoint} 异常: {e}")
        
        print("\n⚠️ 所有停止方法都失败了，会话可能仍在运行")
        print("💡 建议手动在Linken Sphere中停止会话")
        
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")

def test_api_endpoints():
    """测试API端点发现"""
    print("\n🔍 探索可用的API端点...")
    
    base_url = "http://127.0.0.1:36555"
    
    # 常见的API端点
    endpoints_to_test = [
        "/",
        "/api",
        "/help",
        "/docs",
        "/status",
        "/sessions",
        "/profiles",
        "/version"
    ]
    
    for endpoint in endpoints_to_test:
        try:
            url = f"{base_url}{endpoint}"
            response = requests.get(url, timeout=5)
            print(f"GET {endpoint}: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"   响应: {json.dumps(data, indent=2, ensure_ascii=False)[:200]}...")
                except:
                    print(f"   响应: {response.text[:100]}...")
                    
        except Exception as e:
            print(f"GET {endpoint}: 失败 - {e}")

def main():
    """主函数"""
    print("🧪 Linken Sphere 会话停止API测试")
    print("=" * 60)
    
    # 首先测试API端点
    test_api_endpoints()
    
    print("\n" + "=" * 60)
    
    # 然后测试停止会话
    test_stop_session_formats()

if __name__ == "__main__":
    main()
