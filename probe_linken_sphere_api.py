#!/usr/bin/env python3
"""
Linken Sphere API 探测工具
尝试找到正确的 API 端点
"""

import requests
import json
from typing import List, Dict, Tuple

def probe_api_endpoints(host: str = "127.0.0.1", port: int = 3001) -> Dict:
    """探测可能的 API 端点"""
    base_url = f"http://{host}:{port}"
    
    # 可能的 API 路径
    possible_paths = [
        "/",
        "/api",
        "/api/v1",
        "/api/v1/status",
        "/api/v1/profiles",
        "/api/v1/sessions",
        "/api/status",
        "/api/profiles", 
        "/api/sessions",
        "/status",
        "/profiles",
        "/sessions",
        "/v1/status",
        "/v1/profiles",
        "/v1/sessions",
        "/automation",
        "/automation/api",
        "/automation/v1",
        "/automation/v1/status",
        "/automation/v1/profiles",
        "/automation/v1/sessions",
        "/local-api",
        "/local-api/v1",
        "/local-api/v1/status",
        "/local-api/v1/profiles",
        "/local-api/v1/sessions"
    ]
    
    results = {}
    
    print(f"🔍 探测 Linken Sphere API 端点 ({base_url})")
    print("=" * 60)
    
    for path in possible_paths:
        url = f"{base_url}{path}"
        try:
            response = requests.get(url, timeout=5)
            
            # 记录结果
            result_info = {
                "status_code": response.status_code,
                "content_type": response.headers.get("content-type", ""),
                "content_length": len(response.text),
                "content_preview": response.text[:200] if response.text else ""
            }
            
            results[path] = result_info
            
            # 显示结果
            status_icon = "✅" if response.status_code == 200 else "⚠️" if response.status_code < 500 else "❌"
            print(f"{status_icon} {path:<30} [{response.status_code}] {response.headers.get('content-type', 'unknown')}")
            
            # 如果是 JSON 响应，尝试解析
            if response.status_code == 200 and "application/json" in response.headers.get("content-type", ""):
                try:
                    json_data = response.json()
                    print(f"   📄 JSON 响应: {json.dumps(json_data, indent=2)[:100]}...")
                except:
                    pass
            
            # 如果响应内容很短，显示完整内容
            elif response.text and len(response.text) < 100:
                print(f"   📄 响应内容: {response.text}")
                
        except requests.exceptions.ConnectionError:
            results[path] = {"error": "连接被拒绝"}
            print(f"❌ {path:<30} [连接被拒绝]")
        except requests.exceptions.Timeout:
            results[path] = {"error": "超时"}
            print(f"⏰ {path:<30} [超时]")
        except Exception as e:
            results[path] = {"error": str(e)}
            print(f"❌ {path:<30} [错误: {e}]")
    
    return results

def analyze_results(results: Dict) -> List[str]:
    """分析结果并提供建议"""
    print("\n📊 结果分析")
    print("=" * 60)
    
    successful_endpoints = []
    potential_endpoints = []
    
    for path, info in results.items():
        if isinstance(info, dict) and "status_code" in info:
            if info["status_code"] == 200:
                successful_endpoints.append(path)
                print(f"✅ 成功端点: {path}")
            elif info["status_code"] in [401, 403]:
                potential_endpoints.append(path)
                print(f"🔐 需要认证: {path}")
            elif info["status_code"] == 404:
                pass  # 忽略 404
            else:
                print(f"⚠️ 其他状态: {path} [{info['status_code']}]")
    
    recommendations = []
    
    if successful_endpoints:
        print(f"\n🎉 找到 {len(successful_endpoints)} 个可用端点:")
        for endpoint in successful_endpoints:
            print(f"   - {endpoint}")
            recommendations.append(f"尝试使用端点: {endpoint}")
    
    if potential_endpoints:
        print(f"\n🔐 找到 {len(potential_endpoints)} 个需要认证的端点:")
        for endpoint in potential_endpoints:
            print(f"   - {endpoint}")
            recommendations.append(f"配置认证后尝试: {endpoint}")
    
    if not successful_endpoints and not potential_endpoints:
        print("\n❌ 未找到可用的 API 端点")
        recommendations.extend([
            "检查 Linken Sphere 版本是否支持 API",
            "确认 API 功能已在设置中启用",
            "查看 Linken Sphere 文档获取正确的 API 路径",
            "尝试不同的端口号（如 3000, 3002, 8080）"
        ])
    
    return recommendations

def test_common_operations(base_url: str, successful_endpoints: List[str]):
    """测试常见操作"""
    if not successful_endpoints:
        return
    
    print(f"\n🧪 测试常见操作")
    print("=" * 60)
    
    for endpoint in successful_endpoints[:3]:  # 只测试前3个
        print(f"\n测试端点: {endpoint}")
        print("-" * 40)
        
        # 测试 GET 请求
        try:
            url = f"{base_url}{endpoint}"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                print(f"✅ GET {endpoint} - 成功")
                
                # 尝试解析 JSON
                try:
                    data = response.json()
                    if isinstance(data, dict):
                        print(f"   📋 响应字段: {list(data.keys())}")
                    elif isinstance(data, list):
                        print(f"   📋 响应列表长度: {len(data)}")
                except:
                    print(f"   📄 非 JSON 响应")
            else:
                print(f"⚠️ GET {endpoint} - 状态码: {response.status_code}")
                
        except Exception as e:
            print(f"❌ GET {endpoint} - 错误: {e}")

def main():
    """主函数"""
    print("🔍 Linken Sphere API 探测工具")
    print("=" * 60)
    print("正在探测可能的 API 端点...")
    print()
    
    # 探测 API 端点
    results = probe_api_endpoints()
    
    # 分析结果
    recommendations = analyze_results(results)
    
    # 找到成功的端点
    successful_endpoints = [
        path for path, info in results.items() 
        if isinstance(info, dict) and info.get("status_code") == 200
    ]
    
    # 测试常见操作
    if successful_endpoints:
        test_common_operations("http://127.0.0.1:3001", successful_endpoints)
    
    # 显示建议
    print(f"\n💡 建议")
    print("=" * 60)
    for i, rec in enumerate(recommendations, 1):
        print(f"{i}. {rec}")
    
    # 生成配置建议
    if successful_endpoints:
        print(f"\n⚙️ 配置建议")
        print("=" * 60)
        print("基于探测结果，建议在 linken_sphere_api.py 中使用以下配置:")
        print()
        
        best_endpoint = successful_endpoints[0]
        if best_endpoint.startswith('/api/v1'):
            api_base = '/api/v1'
        elif best_endpoint.startswith('/api'):
            api_base = '/api'
        elif best_endpoint.startswith('/automation'):
            api_base = '/automation'
        else:
            api_base = ''
        
        print(f"API_BASE_PATH = '{api_base}'")
        print(f"STATUS_ENDPOINT = '{best_endpoint}'")
        
        if '/profiles' in str(successful_endpoints):
            profiles_endpoint = next((ep for ep in successful_endpoints if 'profiles' in ep), f"{api_base}/profiles")
            print(f"PROFILES_ENDPOINT = '{profiles_endpoint}'")
        
        if '/sessions' in str(successful_endpoints):
            sessions_endpoint = next((ep for ep in successful_endpoints if 'sessions' in ep), f"{api_base}/sessions")
            print(f"SESSIONS_ENDPOINT = '{sessions_endpoint}'")

if __name__ == "__main__":
    main()
