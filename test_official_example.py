#!/usr/bin/env python3
"""
测试官方提供的 Linken Sphere API 实例
"""

import requests
import json

def test_official_example():
    """测试官方实例代码"""
    print("🧪 测试官方 Linken Sphere API 实例")
    print("=" * 60)
    
    # 首先获取配置文件ID
    print("📋 获取配置文件...")
    try:
        # 尝试不同的端口来获取配置文件
        ports_to_try = [40080, 36555, 3001]
        profiles = None
        working_port = None
        
        for port in ports_to_try:
            try:
                response = requests.get(f"http://127.0.0.1:{port}/sessions", timeout=5)
                if response.status_code == 200:
                    profiles = response.json()
                    working_port = port
                    print(f"✅ 在端口 {port} 找到配置文件")
                    break
            except:
                continue
        
        if not profiles:
            print("❌ 无法获取配置文件")
            return
        
        if not profiles:
            print("❌ 没有可用的配置文件")
            return
        
        profile = profiles[0]
        profile_uuid = profile.get('uuid')
        profile_name = profile.get('name')
        
        print(f"   配置文件: {profile_name}")
        print(f"   UUID: {profile_uuid}")
        
    except Exception as e:
        print(f"❌ 获取配置文件失败: {e}")
        return
    
    # 测试官方实例代码
    print(f"\n🚀 测试会话启动...")
    print("-" * 40)
    
    # 尝试不同的端口
    ports_to_test = [40080, working_port] if working_port != 40080 else [40080]
    
    for port in ports_to_test:
        print(f"\n测试端口: {port}")
        
        url = f"http://127.0.0.1:{port}/sessions/start"
        
        # 使用官方实例的格式
        payload = json.dumps({
            "uuid": profile_uuid,
            "headless": False,
            "debug_port": 12345
        }, indent=4)
        
        headers = {
            'Content-Type': 'application/json'
        }
        
        try:
            print(f"   请求URL: {url}")
            print(f"   请求数据: {payload}")
            
            response = requests.post(url, data=payload, headers=headers, timeout=10)
            
            print(f"   响应状态码: {response.status_code}")
            print(f"   响应内容: {response.text}")
            
            if response.status_code < 400:
                print("   ✅ 请求成功！")
                
                try:
                    response_data = response.json()
                    print(f"   📄 JSON响应: {json.dumps(response_data, indent=2)}")
                    
                    # 检查响应中是否包含会话信息
                    if any(key in response_data for key in ['session_id', 'webdriver_url', 'port', 'selenium_port']):
                        print("   🎯 成功启动会话！")
                        
                        # 如果有会话ID，尝试停止会话
                        session_id = response_data.get('session_id')
                        if session_id:
                            print(f"\n🛑 尝试停止会话: {session_id}")
                            stop_url = f"http://127.0.0.1:{port}/sessions/stop"
                            stop_payload = json.dumps({"session_id": session_id})
                            
                            try:
                                stop_response = requests.post(stop_url, data=stop_payload, headers=headers, timeout=10)
                                print(f"   停止会话状态码: {stop_response.status_code}")
                                print(f"   停止会话响应: {stop_response.text}")
                            except Exception as e:
                                print(f"   停止会话失败: {e}")
                        
                        return True
                        
                except Exception as e:
                    print(f"   ⚠️ JSON解析失败: {e}")
                    
            else:
                print(f"   ❌ 请求失败")
                
        except Exception as e:
            print(f"   ❌ 请求异常: {e}")
    
    return False

def test_alternative_formats():
    """测试其他可能的数据格式"""
    print(f"\n🔄 测试其他数据格式...")
    print("-" * 40)
    
    # 获取配置文件
    try:
        response = requests.get("http://127.0.0.1:36555/sessions", timeout=5)
        if response.status_code == 200:
            profiles = response.json()
            if profiles:
                profile_uuid = profiles[0].get('uuid')
            else:
                return
        else:
            return
    except:
        return
    
    # 测试不同的数据格式
    test_formats = [
        # 格式1: 标准JSON对象
        {"uuid": profile_uuid, "headless": False},
        
        # 格式2: 添加debug_port
        {"uuid": profile_uuid, "headless": False, "debug_port": 9222},
        
        # 格式3: 使用profile_id
        {"profile_id": profile_uuid, "headless": False},
        
        # 格式4: 简化格式
        {"uuid": profile_uuid},
        
        # 格式5: 字符串格式
        profile_uuid
    ]
    
    url = "http://127.0.0.1:36555/sessions/start"
    
    for i, test_data in enumerate(test_formats, 1):
        print(f"\n格式 {i}: {type(test_data).__name__}")
        
        try:
            if isinstance(test_data, str):
                # 字符串数据
                response = requests.post(url, data=test_data, headers={'Content-Type': 'text/plain'}, timeout=5)
            else:
                # JSON数据
                response = requests.post(url, json=test_data, timeout=5)
            
            print(f"   状态码: {response.status_code}")
            
            if response.status_code < 400:
                print(f"   ✅ 成功！")
                print(f"   响应: {response.text[:100]}...")
            else:
                print(f"   ❌ 失败")
                if response.text:
                    print(f"   错误: {response.text[:100]}...")
                    
        except Exception as e:
            print(f"   ❌ 异常: {e}")

def main():
    """主函数"""
    print("🔍 Linken Sphere 官方实例测试工具")
    print("基于您提供的官方API实例进行测试")
    print("=" * 60)
    
    # 测试官方实例
    success = test_official_example()
    
    if not success:
        # 如果官方实例失败，尝试其他格式
        test_alternative_formats()
    
    print(f"\n📊 测试完成")
    print("=" * 60)
    
    if success:
        print("✅ 找到可用的API配置")
        print("💡 可以更新主程序使用发现的配置")
    else:
        print("❌ 未找到可用的API配置")
        print("💡 建议:")
        print("1. 检查 Linken Sphere 中的 API 设置")
        print("2. 确认当前套餐是否支持 API 功能")
        print("3. 尝试手动集成模式")

if __name__ == "__main__":
    main()
