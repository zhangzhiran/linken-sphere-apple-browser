#!/usr/bin/env python3
"""
发现正确的会话启动端点
基于端口 36555 进行详细测试
"""

import requests
import json

def test_session_endpoints():
    """测试各种可能的会话启动端点"""
    base_url = "http://127.0.0.1:36555"
    
    # 首先获取配置文件信息
    print("📋 获取配置文件信息...")
    try:
        response = requests.get(f"{base_url}/sessions", timeout=10)
        if response.status_code == 200:
            profiles = response.json()
            if profiles:
                profile = profiles[0]
                profile_id = profile.get('uuid')
                profile_name = profile.get('name')
                print(f"✅ 找到配置文件: {profile_name} (ID: {profile_id})")
            else:
                print("❌ 没有找到配置文件")
                return
        else:
            print(f"❌ 无法获取配置文件: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ 获取配置文件失败: {e}")
        return
    
    print(f"\n🔍 测试会话启动端点...")
    print("=" * 60)
    
    # 可能的启动端点
    start_endpoints = [
        # 直接启动
        "/start",
        "/launch", 
        "/run",
        "/open",
        "/create",
        "/execute",
        
        # 带sessions前缀
        "/sessions/start",
        "/sessions/launch",
        "/sessions/run", 
        "/sessions/open",
        "/sessions/create",
        
        # RESTful风格
        f"/sessions/{profile_id}/start",
        f"/sessions/{profile_id}/launch",
        f"/sessions/{profile_id}/run",
        f"/sessions/{profile_id}",
        
        # 带profile前缀
        "/profile/start",
        "/profile/launch",
        f"/profile/{profile_id}/start",
        f"/profile/{profile_id}/launch",
        
        # API版本化
        "/api/start",
        "/api/launch",
        "/api/sessions/start",
        "/api/sessions/launch",
        "/api/v1/start",
        "/api/v1/launch",
        "/api/v1/sessions/start",
        "/api/v1/sessions/launch",
        
        # 浏览器相关
        "/browser/start",
        "/browser/launch",
        "/browser/open",
        "/browser/create",
        
        # WebDriver风格
        "/webdriver/session",
        "/wd/hub/session",
        
        # 其他可能的端点
        f"/{profile_id}/start",
        f"/{profile_id}/launch",
        f"/{profile_id}",
    ]
    
    # 不同的数据格式
    data_formats = [
        {"profile_id": profile_id},
        {"uuid": profile_id},
        {"id": profile_id},
        {"profileId": profile_id},
        {"profile": profile_id},
        {"name": profile_name},
        {"session": {"profile_id": profile_id}},
        {"browser": {"profile_id": profile_id}},
        {"config": {"profile_id": profile_id}},
        profile_id,  # 直接发送ID
    ]
    
    successful_endpoints = []
    
    for endpoint in start_endpoints:
        print(f"\n测试端点: {endpoint}")
        print("-" * 40)
        
        for i, data in enumerate(data_formats):
            try:
                headers = {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                }
                
                # 尝试POST请求
                if isinstance(data, str):
                    # 如果数据是字符串，尝试不同的发送方式
                    response = requests.post(f"{base_url}{endpoint}", data=data, headers={'Content-Type': 'text/plain'}, timeout=10)
                else:
                    response = requests.post(f"{base_url}{endpoint}", json=data, headers=headers, timeout=10)
                
                print(f"  格式 {i+1}: {type(data).__name__} - 状态码: {response.status_code}")
                
                if response.status_code < 400:
                    print(f"    ✅ 成功！")
                    
                    try:
                        json_response = response.json()
                        print(f"    响应: {json.dumps(json_response, indent=2)[:200]}...")
                        
                        # 检查响应是否包含会话信息
                        if any(key in json_response for key in ['session_id', 'webdriver', 'port', 'url', 'selenium_port']):
                            print(f"    🎯 这可能是正确的启动端点！")
                            successful_endpoints.append({
                                'endpoint': endpoint,
                                'data_format': i+1,
                                'data': data,
                                'response': json_response
                            })
                            
                    except:
                        text_response = response.text[:200]
                        print(f"    响应文本: {text_response}...")
                        
                elif response.status_code in [400, 422]:
                    print(f"    ⚠️ 参数错误 - 端点可能存在但参数格式不对")
                    try:
                        error_response = response.json()
                        print(f"    错误: {error_response}")
                    except:
                        print(f"    错误文本: {response.text[:100]}")
                        
                elif response.status_code == 404:
                    print(f"    ❌ 端点不存在")
                else:
                    print(f"    ❌ 其他错误")
                    
            except Exception as e:
                print(f"  格式 {i+1}: 异常 - {str(e)[:50]}")
        
        # 如果找到成功的端点，可以提前结束
        if successful_endpoints:
            break
    
    # 总结结果
    print(f"\n📊 测试结果")
    print("=" * 60)
    
    if successful_endpoints:
        print(f"✅ 找到 {len(successful_endpoints)} 个可用的启动端点:")
        
        for i, endpoint_info in enumerate(successful_endpoints, 1):
            endpoint = endpoint_info['endpoint']
            data_format = endpoint_info['data_format']
            data = endpoint_info['data']
            response = endpoint_info['response']
            
            print(f"\n{i}. 端点: {endpoint}")
            print(f"   数据格式: {data_format} ({type(data).__name__})")
            print(f"   数据内容: {data}")
            print(f"   响应: {json.dumps(response, indent=2)[:150]}...")
            
        print(f"\n💡 建议更新代码:")
        best_endpoint = successful_endpoints[0]
        print(f"   端点: {best_endpoint['endpoint']}")
        print(f"   数据格式: {best_endpoint['data']}")
        
    else:
        print("❌ 未找到可用的启动端点")
        print("\n💡 可能的原因:")
        print("1. 会话启动功能需要特殊权限")
        print("2. 当前套餐不支持会话管理")
        print("3. 需要先进行认证")
        print("4. 使用了完全不同的API协议")
        
        print(f"\n🔧 建议:")
        print("1. 检查 Linken Sphere 设置中的 API 权限")
        print("2. 尝试手动集成模式: python linken_sphere_manual.py")
        print("3. 查看 Linken Sphere 官方文档")

if __name__ == "__main__":
    print("🔍 Linken Sphere 会话启动端点发现工具")
    print("基于端口 36555 进行详细测试")
    print("=" * 60)
    
    test_session_endpoints()
