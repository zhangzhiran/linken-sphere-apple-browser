#!/usr/bin/env python3
"""
扫描 Linken Sphere 可能的会话管理端口
"""

import socket
import requests
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

def test_port(host: str, port: int) -> dict:
    """测试单个端口"""
    try:
        # 测试TCP连接
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex((host, port))
        sock.close()
        
        if result == 0:
            # 端口开放，尝试HTTP请求
            try:
                response = requests.get(f"http://{host}:{port}/", timeout=3)
                return {
                    "port": port,
                    "open": True,
                    "http_status": response.status_code,
                    "http_response": response.text[:100] if response.text else ""
                }
            except:
                return {
                    "port": port,
                    "open": True,
                    "http_status": None,
                    "http_response": "HTTP请求失败"
                }
        else:
            return {"port": port, "open": False}
            
    except Exception as e:
        return {"port": port, "open": False, "error": str(e)}

def scan_ports(host: str = "127.0.0.1", start_port: int = 3000, end_port: int = 50000, max_workers: int = 50):
    """扫描端口范围"""
    print(f"🔍 扫描 {host} 的端口范围 {start_port}-{end_port}")
    print("寻找可能的 Linken Sphere 会话管理端口...")
    print("-" * 60)
    
    # 重点扫描的端口（基于常见配置）
    priority_ports = [
        3001, 3002, 3003,  # 基础API端口附近
        40080, 40081, 40082,  # 文档提到的端口
        8080, 8081, 8082,  # 常见Web端口
        9222, 9223, 9224,  # Chrome调试端口
        4444, 4445, 4446,  # WebDriver端口
        5555, 5556, 5557,  # 其他常见端口
    ]
    
    # 先测试重点端口
    print("📍 测试重点端口...")
    open_ports = []
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_port = {executor.submit(test_port, host, port): port for port in priority_ports}
        
        for future in as_completed(future_to_port):
            result = future.result()
            if result["open"]:
                open_ports.append(result)
                port = result["port"]
                status = result.get("http_status", "N/A")
                response = result.get("http_response", "")[:50]
                print(f"  ✅ 端口 {port} 开放 [HTTP: {status}] {response}")
    
    if not open_ports:
        print("  ❌ 重点端口中未发现开放端口")
        
        # 如果重点端口都没开放，进行更广泛的扫描
        print(f"\n🔍 扫描更广泛的端口范围 ({start_port}-{end_port})...")
        print("这可能需要一些时间...")
        
        ports_to_scan = list(range(start_port, min(end_port + 1, start_port + 1000)))  # 限制扫描范围
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_port = {executor.submit(test_port, host, port): port for port in ports_to_scan}
            
            completed = 0
            for future in as_completed(future_to_port):
                result = future.result()
                completed += 1
                
                if completed % 100 == 0:
                    print(f"  已扫描 {completed}/{len(ports_to_scan)} 个端口...")
                
                if result["open"]:
                    open_ports.append(result)
                    port = result["port"]
                    status = result.get("http_status", "N/A")
                    response = result.get("http_response", "")[:50]
                    print(f"  ✅ 发现开放端口 {port} [HTTP: {status}] {response}")
    
    return open_ports

def test_session_endpoints(host: str, port: int):
    """测试会话相关的端点"""
    print(f"\n🧪 测试端口 {port} 的会话端点...")
    
    base_url = f"http://{host}:{port}"
    
    # 可能的会话端点
    endpoints = [
        "/",
        "/start",
        "/stop", 
        "/sessions",
        "/session",
        "/api/start",
        "/api/stop",
        "/api/sessions",
        "/v1/start",
        "/v1/stop",
        "/v1/sessions",
        "/browser/start",
        "/browser/stop",
        "/automation/start",
        "/automation/stop"
    ]
    
    successful_endpoints = []
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            if response.status_code < 400:
                successful_endpoints.append(endpoint)
                print(f"  ✅ {endpoint} [状态: {response.status_code}]")
                
                # 显示响应内容
                try:
                    json_data = response.json()
                    print(f"     JSON: {json.dumps(json_data, indent=2)[:100]}...")
                except:
                    text = response.text[:100]
                    if text.strip():
                        print(f"     文本: {text}...")
            else:
                print(f"  ❌ {endpoint} [状态: {response.status_code}]")
                
        except Exception as e:
            print(f"  ❌ {endpoint} [错误: {str(e)[:50]}]")
    
    return successful_endpoints

def main():
    """主函数"""
    print("🔍 Linken Sphere 会话管理端口扫描器")
    print("=" * 60)
    
    host = "127.0.0.1"
    
    # 扫描端口
    open_ports = scan_ports(host)
    
    print(f"\n📊 扫描结果总结")
    print("=" * 60)
    
    if open_ports:
        print(f"✅ 发现 {len(open_ports)} 个开放端口:")
        
        for port_info in open_ports:
            port = port_info["port"]
            status = port_info.get("http_status", "N/A")
            print(f"  - 端口 {port} [HTTP状态: {status}]")
        
        # 测试每个开放端口的会话端点
        for port_info in open_ports:
            port = port_info["port"]
            if port_info.get("http_status"):  # 只测试有HTTP响应的端口
                endpoints = test_session_endpoints(host, port)
                if endpoints:
                    print(f"\n💡 端口 {port} 可能是会话管理端口")
                    print(f"   可用端点: {', '.join(endpoints)}")
        
        print(f"\n🎯 建议")
        print("-" * 30)
        print("1. 检查上述端口中哪个是会话管理端口")
        print("2. 更新 linken_sphere_api.py 中的 session_port 配置")
        print("3. 重新运行测试验证功能")
        
    else:
        print("❌ 未发现任何开放的端口")
        print("\n💡 可能的原因:")
        print("1. Linken Sphere 未启动")
        print("2. API 功能未启用")
        print("3. 使用了非标准端口配置")
        print("4. 防火墙阻止了端口访问")
        
        print("\n🔧 建议:")
        print("1. 检查 Linken Sphere 应用程序设置")
        print("2. 确认 API 功能已启用")
        print("3. 查看 Linken Sphere 日志文件")
        print("4. 尝试手动集成模式: python linken_sphere_manual.py")

if __name__ == "__main__":
    main()
