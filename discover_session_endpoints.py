#!/usr/bin/env python3
"""
发现 Linken Sphere 正确的会话管理端点
基于40080端口进行详细的端点探测
"""

import requests
import json
import sys

def test_endpoint(base_url: str, endpoint: str, method: str = "GET", data: dict = None) -> dict:
    """测试单个端点"""
    url = f"{base_url}{endpoint}"
    
    try:
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        if method.upper() == "GET":
            response = requests.get(url, headers=headers, timeout=10)
        elif method.upper() == "POST":
            response = requests.post(url, headers=headers, json=data, timeout=10)
        else:
            return {"error": f"不支持的方法: {method}"}
        
        result = {
            "endpoint": endpoint,
            "method": method,
            "status_code": response.status_code,
            "success": response.status_code < 400
        }
        
        # 尝试解析响应
        try:
            result["json"] = response.json()
        except:
            result["text"] = response.text[:200]
        
        return result
        
    except requests.exceptions.ConnectionError:
        return {"error": "连接被拒绝", "endpoint": endpoint}
    except requests.exceptions.Timeout:
        return {"error": "请求超时", "endpoint": endpoint}
    except Exception as e:
        return {"error": str(e), "endpoint": endpoint}

def discover_session_endpoints(host: str = "127.0.0.1", port: int = 40080):
    """发现会话管理端点"""
    base_url = f"http://{host}:{port}"
    
    print(f"🔍 探测 Linken Sphere 会话端点: {base_url}")
    print("=" * 60)
    
    # 首先确认我们能获取配置文件
    print("📋 验证配置文件获取...")
    sessions_result = test_endpoint(base_url, "/sessions", "GET")
    
    if not sessions_result.get("success"):
        print("❌ 无法获取配置文件列表，停止测试")
        return None
    
    profiles = sessions_result.get("json", [])
    if not profiles:
        print("❌ 没有可用的配置文件")
        return None
    
    print(f"✅ 找到 {len(profiles)} 个配置文件")
    test_profile = profiles[0]
    profile_id = test_profile.get("uuid")
    profile_name = test_profile.get("name")
    print(f"   测试配置文件: {profile_name} (ID: {profile_id})")
    
    # 可能的会话管理端点模式
    session_endpoints = [
        # 直接端点
        "/start",
        "/stop", 
        "/launch",
        "/close",
        "/create",
        "/destroy",
        
        # 带sessions前缀
        "/sessions/start",
        "/sessions/stop",
        "/sessions/launch", 
        "/sessions/close",
        "/sessions/create",
        "/sessions/destroy",
        
        # 带profile前缀
        "/profile/start",
        "/profile/stop",
        "/profile/launch",
        "/profile/close",
        
        # RESTful风格
        f"/sessions/{profile_id}/start",
        f"/sessions/{profile_id}/stop",
        f"/sessions/{profile_id}/launch",
        f"/sessions/{profile_id}/close",
        
        # API版本化
        "/api/start",
        "/api/stop",
        "/api/sessions/start",
        "/api/sessions/stop",
        "/api/v1/start",
        "/api/v1/stop",
        "/api/v1/sessions/start",
        "/api/v1/sessions/stop",
        
        # 浏览器相关
        "/browser/start",
        "/browser/stop",
        "/browser/launch",
        "/browser/close",
        
        # 自动化相关
        "/automation/start",
        "/automation/stop",
        
        # WebDriver风格
        "/webdriver/session",
        "/wd/hub/session",
        
        # 其他可能的端点
        "/run",
        "/execute",
        "/open",
        "/kill"
    ]
    
    print(f"\n🧪 测试会话管理端点...")
    print("-" * 60)
    
    successful_endpoints = []
    potential_endpoints = []
    
    # 测试数据
    test_data = {
        "profile_id": profile_id,
        "uuid": profile_id,
        "id": profile_id,
        "name": profile_name
    }
    
    for endpoint in session_endpoints:
        print(f"测试: POST {endpoint}")
        
        # 尝试POST请求
        result = test_endpoint(base_url, endpoint, "POST", test_data)
        
        if result.get("success"):
            print(f"  ✅ 成功 [{result['status_code']}]")
            successful_endpoints.append(endpoint)
            
            if "json" in result:
                response_data = result["json"]
                print(f"     响应: {json.dumps(response_data, indent=2)[:150]}...")
                
                # 检查响应是否包含会话信息
                if any(key in response_data for key in ["session_id", "webdriver", "port", "url"]):
                    print("     🎯 这可能是启动会话的端点！")
            
        elif result.get("status_code") in [400, 422]:
            # 400/422 可能表示端点存在但参数错误
            print(f"  ⚠️ 参数错误 [{result['status_code']}] - 端点可能存在")
            potential_endpoints.append(endpoint)
            
            if "json" in result:
                print(f"     错误: {result['json']}")
            elif "text" in result:
                print(f"     错误: {result['text'][:100]}")
                
        elif result.get("status_code") == 404:
            print(f"  ❌ 未找到 [404]")
        else:
            error = result.get("error", "未知错误")
            status = result.get("status_code", "N/A")
            print(f"  ❌ 失败 [{status}]: {error}")
    
    # 对于可能存在的端点，尝试不同的参数格式
    if potential_endpoints:
        print(f"\n🔄 尝试不同参数格式...")
        print("-" * 40)
        
        alternative_data_formats = [
            {"profileId": profile_id},
            {"profile": profile_id},
            {"sessionId": profile_id},
            {"browser_profile": profile_id},
            {"config": {"profile_id": profile_id}},
            profile_id,  # 直接发送ID字符串
        ]
        
        for endpoint in potential_endpoints[:3]:  # 只测试前3个
            print(f"\n测试端点: {endpoint}")
            for i, alt_data in enumerate(alternative_data_formats):
                print(f"  尝试参数格式 {i+1}...")
                result = test_endpoint(base_url, endpoint, "POST", alt_data)
                
                if result.get("success"):
                    print(f"    ✅ 成功！参数格式: {type(alt_data).__name__}")
                    if "json" in result:
                        print(f"    响应: {json.dumps(result['json'], indent=2)[:100]}...")
                    successful_endpoints.append(f"{endpoint} (格式{i+1})")
                    break
                elif result.get("status_code") not in [400, 422, 404]:
                    print(f"    ⚠️ 状态码: {result.get('status_code')}")
    
    # 总结结果
    print(f"\n📊 发现结果")
    print("=" * 60)
    
    if successful_endpoints:
        print(f"✅ 找到 {len(successful_endpoints)} 个可用端点:")
        for endpoint in successful_endpoints:
            print(f"   - {endpoint}")
        
        print(f"\n💡 建议更新 linken_sphere_api.py:")
        print(f"   将 start_session 方法中的端点改为: {successful_endpoints[0].split(' ')[0]}")
        
    elif potential_endpoints:
        print(f"⚠️ 找到 {len(potential_endpoints)} 个可能的端点:")
        for endpoint in potential_endpoints:
            print(f"   - {endpoint}")
        
        print(f"\n💡 这些端点存在但可能需要不同的参数格式")
        
    else:
        print("❌ 未找到可用的会话管理端点")
        print("\n💡 可能的原因:")
        print("1. 会话管理功能需要特殊权限")
        print("2. 使用了不同的API协议")
        print("3. 需要先进行认证")
        print("4. 当前套餐不支持会话管理")
    
    return {
        "successful": successful_endpoints,
        "potential": potential_endpoints,
        "profile_id": profile_id,
        "profile_name": profile_name
    }

def main():
    """主函数"""
    print("🔍 Linken Sphere 会话端点发现工具")
    print("基于40080端口进行详细探测")
    print("=" * 60)
    
    try:
        host = input("请输入 API 地址 (默认: 127.0.0.1): ").strip() or "127.0.0.1"
        port_input = input("请输入 API 端口 (默认: 40080): ").strip()
        port = int(port_input) if port_input else 40080
        
        print(f"\n使用配置: {host}:{port}")
        print("开始探测...\n")
        
    except ValueError:
        print("❌ 端口号必须是数字")
        return False
    except KeyboardInterrupt:
        print("\n探测已取消")
        return False
    
    results = discover_session_endpoints(host, port)
    
    if results and results["successful"]:
        print(f"\n🎉 探测完成！")
        print("可以使用发现的端点更新API配置")
        return True
    else:
        print(f"\n⚠️ 未找到完全可用的端点")
        print("建议尝试手动集成模式: python linken_sphere_manual.py")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
