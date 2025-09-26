#!/usr/bin/env python3
"""
测试 Linken Sphere 双端口 API 配置
验证 3001 端口（配置文件）和 40080 端口（会话管理）
"""

import requests
import json
import sys
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def test_port_connectivity(host: str, port: int, port_name: str) -> bool:
    """测试端口连通性"""
    print(f"🔍 测试 {port_name} 端口 ({port})...")
    
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((host, port))
        sock.close()
        
        if result == 0:
            print(f"✅ {port_name} 端口 {port} 连接成功")
            return True
        else:
            print(f"❌ {port_name} 端口 {port} 连接失败")
            return False
            
    except Exception as e:
        print(f"❌ {port_name} 端口测试异常: {e}")
        return False

def test_api_endpoint(base_url: str, endpoint: str, method: str = "GET", data: dict = None) -> dict:
    """测试 API 端点"""
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
            "success": response.status_code < 400
        }
        
        # 尝试解析 JSON 响应
        try:
            result["json"] = response.json()
        except:
            result["text"] = response.text[:200]  # 只保留前200字符
        
        return result
        
    except requests.exceptions.ConnectionError:
        return {"error": "连接被拒绝", "url": url}
    except requests.exceptions.Timeout:
        return {"error": "请求超时", "url": url}
    except Exception as e:
        return {"error": str(e), "url": url}

def test_profile_api(host: str = "127.0.0.1", port: int = 3001):
    """测试配置文件 API（3001端口）"""
    print(f"\n📋 测试配置文件 API: http://{host}:{port}")
    print("-" * 50)
    
    base_url = f"http://{host}:{port}"
    
    # 测试获取配置文件列表
    result = test_api_endpoint(base_url, "/sessions", "GET")
    
    if result.get("success"):
        print("✅ 获取配置文件列表成功")
        if "json" in result and isinstance(result["json"], list):
            profiles = result["json"]
            print(f"   找到 {len(profiles)} 个配置文件:")
            for i, profile in enumerate(profiles, 1):
                name = profile.get('name', 'Unknown')
                uuid = profile.get('uuid', 'N/A')
                status = profile.get('status', 'Unknown')
                print(f"   {i}. {name} (ID: {uuid}, 状态: {status})")
            return profiles
        else:
            print("   ⚠️ 响应格式异常")
            return []
    else:
        print(f"❌ 获取配置文件失败: {result.get('error', '未知错误')}")
        return []

def test_session_api(host: str = "127.0.0.1", port: int = 40080, profiles: list = None):
    """测试会话管理 API（40080端口）"""
    print(f"\n🚀 测试会话管理 API: http://{host}:{port}")
    print("-" * 50)
    
    base_url = f"http://{host}:{port}"
    
    # 测试基础连接
    endpoints_to_test = [
        "/",
        "/status", 
        "/health",
        "/sessions",
        "/start",
        "/stop",
        "/info"
    ]
    
    successful_endpoints = []
    
    for endpoint in endpoints_to_test:
        print(f"测试端点: {endpoint}")
        result = test_api_endpoint(base_url, endpoint, "GET")
        
        if result.get("success"):
            print(f"  ✅ 成功 [{result['status_code']}]")
            successful_endpoints.append(endpoint)
            
            if "json" in result:
                print(f"     响应: {json.dumps(result['json'], indent=2)[:100]}...")
            elif "text" in result:
                print(f"     响应: {result['text'][:50]}...")
        else:
            status = result.get('status_code', 'N/A')
            error = result.get('error', '未知错误')
            print(f"  ❌ 失败 [{status}]: {error}")
    
    # 如果有配置文件，尝试启动会话
    if profiles and successful_endpoints:
        print(f"\n🧪 尝试会话操作...")
        test_profile = profiles[0]
        profile_id = test_profile.get('uuid')
        profile_name = test_profile.get('name')
        
        if profile_id:
            print(f"使用配置文件: {profile_name} (ID: {profile_id})")
            
            # 尝试启动会话
            start_data = {"profile_id": profile_id}
            start_result = test_api_endpoint(base_url, "/start", "POST", start_data)
            
            if start_result.get("success"):
                print("✅ 会话启动请求成功")
                if "json" in start_result:
                    session_info = start_result["json"]
                    print(f"   会话信息: {json.dumps(session_info, indent=2)}")
                    
                    # 如果获得了会话ID，尝试停止
                    session_id = session_info.get('session_id')
                    if session_id:
                        print(f"\n尝试停止会话: {session_id}")
                        stop_data = {"session_id": session_id}
                        stop_result = test_api_endpoint(base_url, "/stop", "POST", stop_data)
                        
                        if stop_result.get("success"):
                            print("✅ 会话停止成功")
                        else:
                            print(f"⚠️ 会话停止失败: {stop_result.get('error', '未知错误')}")
            else:
                print(f"❌ 会话启动失败: {start_result.get('error', '未知错误')}")
                if "json" in start_result:
                    print(f"   错误详情: {start_result['json']}")
    
    return successful_endpoints

def main():
    """主函数"""
    print("🔍 Linken Sphere 双端口 API 测试")
    print("=" * 60)
    print("测试配置文件 API (3001) 和会话管理 API (40080)")
    print("=" * 60)
    
    host = "127.0.0.1"
    profile_port = 3001
    session_port = 40080
    
    # 测试端口连通性
    print("🔌 测试端口连通性")
    print("-" * 30)
    
    profile_port_ok = test_port_connectivity(host, profile_port, "配置文件API")
    session_port_ok = test_port_connectivity(host, session_port, "会话管理API")
    
    if not profile_port_ok and not session_port_ok:
        print("\n❌ 两个端口都无法连接")
        print("💡 请确保 Linken Sphere 正在运行并且 API 功能已启用")
        return False
    
    # 测试配置文件 API
    profiles = []
    if profile_port_ok:
        profiles = test_profile_api(host, profile_port)
    else:
        print(f"\n⚠️ 跳过配置文件 API 测试（端口 {profile_port} 不可用）")
    
    # 测试会话管理 API
    session_endpoints = []
    if session_port_ok:
        session_endpoints = test_session_api(host, session_port, profiles)
    else:
        print(f"\n⚠️ 跳过会话管理 API 测试（端口 {session_port} 不可用）")
    
    # 总结
    print(f"\n{'='*60}")
    print("📊 测试结果总结")
    print("=" * 60)
    
    print(f"配置文件 API (端口 {profile_port}): {'✅ 可用' if profile_port_ok else '❌ 不可用'}")
    if profiles:
        print(f"  - 找到 {len(profiles)} 个配置文件")
    
    print(f"会话管理 API (端口 {session_port}): {'✅ 可用' if session_port_ok else '❌ 不可用'}")
    if session_endpoints:
        print(f"  - 可用端点: {', '.join(session_endpoints)}")
    
    if profile_port_ok and session_port_ok:
        print("\n🎉 双端口配置测试完成！")
        print("✅ 可以更新 linken_sphere_api.py 使用正确的端口配置")
        print("\n💡 下一步:")
        print("1. 运行 python test_updated_api.py 验证更新后的API")
        print("2. 或运行 python linken_sphere_browser.py 测试完整功能")
    elif profile_port_ok:
        print("\n⚠️ 仅配置文件 API 可用")
        print("💡 会话管理功能可能需要不同的配置或端口")
    elif session_port_ok:
        print("\n⚠️ 仅会话管理 API 可用")
        print("💡 配置文件获取功能可能需要不同的配置或端口")
    else:
        print("\n❌ API 功能不可用")
        print("💡 建议使用手动集成模式: python linken_sphere_manual.py")
    
    return profile_port_ok or session_port_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
