#!/usr/bin/env python3
"""
测试 Linken Sphere API 端点
基于官方文档尝试不同的端点格式
"""

import requests
import json
import time
from typing import Dict, List, Optional

def test_api_endpoint(base_url: str, endpoint: str, method: str = "GET", data: Dict = None) -> Dict:
    """测试单个 API 端点"""
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
            "url": url,
            "method": method,
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "success": response.status_code < 400
        }
        
        # 尝试解析 JSON 响应
        try:
            result["json"] = response.json()
        except:
            result["text"] = response.text[:500]  # 只保留前500字符
        
        return result
        
    except requests.exceptions.ConnectionError:
        return {"error": "连接被拒绝", "url": url}
    except requests.exceptions.Timeout:
        return {"error": "请求超时", "url": url}
    except Exception as e:
        return {"error": str(e), "url": url}

def test_linken_sphere_api(host: str = "127.0.0.1", port: int = 3001):
    """测试 Linken Sphere API 的各种可能端点"""
    base_url = f"http://{host}:{port}"
    
    print(f"🔍 测试 Linken Sphere API: {base_url}")
    print("=" * 60)
    
    # 基于文档和常见模式的端点列表
    endpoints_to_test = [
        # 基础端点
        {"endpoint": "/", "method": "GET"},
        {"endpoint": "/api", "method": "GET"},
        {"endpoint": "/health", "method": "GET"},
        {"endpoint": "/status", "method": "GET"},
        
        # 版本化端点
        {"endpoint": "/v1", "method": "GET"},
        {"endpoint": "/v1/status", "method": "GET"},
        {"endpoint": "/v1/profiles", "method": "GET"},
        {"endpoint": "/v1/sessions", "method": "GET"},
        
        # API 版本化端点
        {"endpoint": "/api/v1", "method": "GET"},
        {"endpoint": "/api/v1/status", "method": "GET"},
        {"endpoint": "/api/v1/profiles", "method": "GET"},
        {"endpoint": "/api/v1/sessions", "method": "GET"},
        
        # 常见的 REST API 端点
        {"endpoint": "/profiles", "method": "GET"},
        {"endpoint": "/sessions", "method": "GET"},
        {"endpoint": "/browser", "method": "GET"},
        {"endpoint": "/browser/profiles", "method": "GET"},
        {"endpoint": "/browser/sessions", "method": "GET"},
        
        # 可能的本地 API 端点
        {"endpoint": "/local", "method": "GET"},
        {"endpoint": "/local/profiles", "method": "GET"},
        {"endpoint": "/local/sessions", "method": "GET"},
        
        # 自动化相关端点
        {"endpoint": "/automation", "method": "GET"},
        {"endpoint": "/automation/profiles", "method": "GET"},
        {"endpoint": "/automation/sessions", "method": "GET"},
        
        # WebDriver 相关端点
        {"endpoint": "/webdriver", "method": "GET"},
        {"endpoint": "/webdriver/sessions", "method": "GET"},
        
        # 可能的管理端点
        {"endpoint": "/admin", "method": "GET"},
        {"endpoint": "/admin/profiles", "method": "GET"},
        {"endpoint": "/admin/sessions", "method": "GET"},
    ]
    
    successful_endpoints = []
    auth_required_endpoints = []
    
    for test_case in endpoints_to_test:
        endpoint = test_case["endpoint"]
        method = test_case["method"]
        
        print(f"测试: {method} {endpoint}")
        result = test_api_endpoint(base_url, endpoint, method)
        
        if "error" in result:
            print(f"  ❌ 错误: {result['error']}")
        else:
            status = result["status_code"]
            if status == 200:
                print(f"  ✅ 成功 [{status}]")
                successful_endpoints.append(endpoint)
                
                # 显示响应内容
                if "json" in result:
                    print(f"     JSON: {json.dumps(result['json'], indent=2)[:200]}...")
                elif "text" in result:
                    print(f"     文本: {result['text'][:100]}...")
                    
            elif status in [401, 403]:
                print(f"  🔐 需要认证 [{status}]")
                auth_required_endpoints.append(endpoint)
                
                if "json" in result:
                    print(f"     响应: {result['json']}")
                elif "text" in result:
                    print(f"     响应: {result['text'][:100]}")
                    
            elif status == 404:
                print(f"  ⚠️ 未找到 [{status}]")
            else:
                print(f"  ⚠️ 其他状态 [{status}]")
                
                if "json" in result:
                    print(f"     响应: {result['json']}")
                elif "text" in result:
                    print(f"     响应: {result['text'][:100]}")
        
        print()
    
    # 总结结果
    print("📊 测试结果总结")
    print("=" * 60)
    
    if successful_endpoints:
        print(f"✅ 成功的端点 ({len(successful_endpoints)} 个):")
        for endpoint in successful_endpoints:
            print(f"   - {endpoint}")
    
    if auth_required_endpoints:
        print(f"\n🔐 需要认证的端点 ({len(auth_required_endpoints)} 个):")
        for endpoint in auth_required_endpoints:
            print(f"   - {endpoint}")
    
    if not successful_endpoints and not auth_required_endpoints:
        print("❌ 未找到可用的 API 端点")
        print("\n💡 可能的原因:")
        print("1. API 功能未在 Linken Sphere 中启用")
        print("2. API 端口配置不正确")
        print("3. 当前套餐不支持 API 功能")
        print("4. Linken Sphere 版本过旧")
    
    return {
        "successful": successful_endpoints,
        "auth_required": auth_required_endpoints
    }

def test_profile_operations(base_url: str, successful_endpoints: List[str]):
    """测试配置文件相关操作"""
    if not successful_endpoints:
        return
    
    print(f"\n🧪 测试配置文件操作")
    print("=" * 60)
    
    # 寻找配置文件相关的端点
    profile_endpoints = [ep for ep in successful_endpoints if 'profile' in ep.lower()]
    
    if not profile_endpoints:
        print("❌ 未找到配置文件相关的端点")
        return
    
    for endpoint in profile_endpoints:
        print(f"\n测试端点: {endpoint}")
        print("-" * 40)
        
        # 测试 GET 请求
        result = test_api_endpoint(base_url, endpoint, "GET")
        if result.get("success"):
            print("✅ GET 请求成功")
            if "json" in result:
                data = result["json"]
                if isinstance(data, list):
                    print(f"   📋 找到 {len(data)} 个配置文件")
                    if data:
                        print(f"   📄 示例配置文件: {json.dumps(data[0], indent=2)[:200]}...")
                elif isinstance(data, dict):
                    print(f"   📋 响应字段: {list(data.keys())}")
        
        # 测试创建配置文件 (POST)
        test_profile_data = {
            "name": f"Test Profile {int(time.time())}",
            "browser": "chrome",
            "os": "windows"
        }
        
        print(f"\n尝试创建测试配置文件...")
        create_result = test_api_endpoint(base_url, endpoint, "POST", test_profile_data)
        
        if create_result.get("success"):
            print("✅ 配置文件创建成功")
            if "json" in create_result:
                print(f"   📄 创建结果: {create_result['json']}")
        else:
            print(f"⚠️ 配置文件创建失败: {create_result.get('error', '未知错误')}")

def main():
    """主函数"""
    print("🔍 Linken Sphere API 端点测试工具")
    print("基于官方文档和常见 API 模式")
    print("=" * 60)
    
    # 获取用户配置
    try:
        host = input("请输入 API 地址 (默认: 127.0.0.1): ").strip() or "127.0.0.1"
        port_input = input("请输入 API 端口 (默认: 3001): ").strip()
        port = int(port_input) if port_input else 3001
        
        print(f"\n使用配置: {host}:{port}")
        print("开始测试...\n")
        
    except ValueError:
        print("❌ 端口号必须是数字")
        return
    except KeyboardInterrupt:
        print("\n测试已取消")
        return
    
    # 测试基础端点
    results = test_linken_sphere_api(host, port)
    
    # 如果找到成功的端点，测试配置文件操作
    if results["successful"]:
        base_url = f"http://{host}:{port}"
        test_profile_operations(base_url, results["successful"])
    
    print(f"\n🎯 建议")
    print("=" * 60)
    
    if results["successful"]:
        print("✅ 找到可用的 API 端点，可以更新代码使用这些端点")
        print("💡 建议更新 linken_sphere_api.py 中的端点配置")
    elif results["auth_required"]:
        print("🔐 找到需要认证的端点，可能需要配置 API 密钥")
        print("💡 检查 Linken Sphere 设置中的 API 认证配置")
    else:
        print("❌ 未找到可用的 API 端点")
        print("💡 建议:")
        print("1. 检查 Linken Sphere 应用程序中的 API 设置")
        print("2. 确认 API 端口配置正确")
        print("3. 验证当前套餐是否支持 API 功能")
        print("4. 尝试使用手动集成模式: python linken_sphere_manual.py")

if __name__ == "__main__":
    main()
