#!/usr/bin/env python3
"""
测试发现的 Linken Sphere 端口
"""

import requests
import json

def test_port_for_api(host: str, port: int) -> dict:
    """测试端口是否是 Linken Sphere API"""
    base_url = f"http://{host}:{port}"
    
    # 测试常见的 API 端点
    endpoints_to_test = [
        "/",
        "/sessions", 
        "/api",
        "/status",
        "/health"
    ]
    
    results = {"port": port, "endpoints": {}}
    
    for endpoint in endpoints_to_test:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            
            result = {
                "status_code": response.status_code,
                "success": response.status_code < 400
            }
            
            # 尝试解析响应
            try:
                json_data = response.json()
                result["json"] = json_data
                
                # 检查是否包含 Linken Sphere 相关信息
                if isinstance(json_data, list):
                    # 检查是否是配置文件列表
                    if json_data and isinstance(json_data[0], dict):
                        first_item = json_data[0]
                        if any(key in first_item for key in ['uuid', 'name', 'status']):
                            result["likely_profiles"] = True
                            
            except:
                result["text"] = response.text[:100]
            
            results["endpoints"][endpoint] = result
            
        except Exception as e:
            results["endpoints"][endpoint] = {"error": str(e)}
    
    return results

def main():
    """主函数"""
    print("🔍 测试发现的端口")
    print("=" * 50)
    
    # 从 netstat 输出中发现的端口
    discovered_ports = [
        3450, 8307, 9097, 9100, 14013, 14016, 14019, 14022, 14023, 
        26795, 26805, 33331, 36555
    ]
    
    host = "127.0.0.1"
    api_ports = []
    
    for port in discovered_ports:
        print(f"\n🧪 测试端口 {port}")
        print("-" * 30)
        
        results = test_port_for_api(host, port)
        
        has_api_response = False
        
        for endpoint, result in results["endpoints"].items():
            if result.get("success"):
                print(f"  ✅ {endpoint} [状态: {result['status_code']}]")
                
                if "json" in result:
                    json_data = result["json"]
                    print(f"     JSON: {json.dumps(json_data, indent=2)[:150]}...")
                    
                    if result.get("likely_profiles"):
                        print("     🎯 这可能是配置文件端点！")
                        has_api_response = True
                        
                elif "text" in result:
                    text = result["text"]
                    if text.strip():
                        print(f"     文本: {text}...")
                        
            elif "error" not in result:
                status = result.get("status_code", "N/A")
                print(f"  ❌ {endpoint} [状态: {status}]")
            else:
                print(f"  ❌ {endpoint} [错误: {result['error'][:50]}]")
        
        if has_api_response:
            api_ports.append(port)
    
    # 总结结果
    print(f"\n📊 测试结果总结")
    print("=" * 50)
    
    if api_ports:
        print(f"✅ 发现可能的 API 端口: {api_ports}")
        
        for port in api_ports:
            print(f"\n🎯 端口 {port} 详细测试:")
            
            # 对找到的 API 端口进行更详细的测试
            base_url = f"http://{host}:{port}"
            
            # 测试获取配置文件
            try:
                response = requests.get(f"{base_url}/sessions", timeout=5)
                if response.status_code == 200:
                    profiles = response.json()
                    if isinstance(profiles, list) and profiles:
                        print(f"   📋 找到 {len(profiles)} 个配置文件:")
                        for i, profile in enumerate(profiles[:3], 1):  # 只显示前3个
                            name = profile.get('name', 'Unknown')
                            uuid = profile.get('uuid', 'N/A')
                            status = profile.get('status', 'Unknown')
                            print(f"      {i}. {name} (ID: {uuid}, 状态: {status})")
                        
                        print(f"\n💡 建议更新 linken_sphere_api.py:")
                        print(f"   将 api_port 设置为: {port}")
                        
            except Exception as e:
                print(f"   ❌ 详细测试失败: {e}")
    
    else:
        print("❌ 未发现明确的 API 端口")
        print("\n💡 可能的原因:")
        print("1. API 功能未启用")
        print("2. 需要认证")
        print("3. 使用了不同的端点路径")
        print("4. 当前套餐不支持 API")
        
        print(f"\n🔧 建议:")
        print("1. 检查 Linken Sphere 设置中的 API 配置")
        print("2. 尝试手动集成模式: python linken_sphere_manual.py")

if __name__ == "__main__":
    main()
