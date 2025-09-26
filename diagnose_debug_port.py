#!/usr/bin/env python3
"""
诊断 Linken Sphere 调试端口连接问题
"""

import requests
import json
import time
import socket

def check_port_open(host, port, timeout=5):
    """检查端口是否开放"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except:
        return False

def check_chrome_debug_api(port):
    """检查 Chrome 调试 API"""
    try:
        response = requests.get(f"http://127.0.0.1:{port}/json", timeout=5)
        if response.status_code == 200:
            tabs = response.json()
            print(f"   ✅ 调试 API 可用，找到 {len(tabs)} 个标签页")
            for i, tab in enumerate(tabs[:3]):  # 只显示前3个
                print(f"      标签 {i+1}: {tab.get('title', 'N/A')[:50]}")
            return True
        else:
            print(f"   ❌ 调试 API 返回状态码: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ 调试 API 请求失败: {e}")
        return False

def start_linken_sphere_session():
    """启动 Linken Sphere 会话并诊断"""
    print("🔍 Linken Sphere 调试端口诊断工具")
    print("=" * 60)
    
    # 1. 获取配置文件
    print("📋 步骤 1: 获取配置文件...")
    try:
        response = requests.get("http://127.0.0.1:36555/sessions", timeout=10)
        if response.status_code == 200:
            profiles = response.json()
            if profiles:
                profile = profiles[0]
                profile_uuid = profile.get('uuid')
                profile_name = profile.get('name')
                print(f"   ✅ 配置文件: {profile_name}")
                print(f"   UUID: {profile_uuid}")
            else:
                print("   ❌ 没有可用的配置文件")
                return
        else:
            print(f"   ❌ 获取配置文件失败: {response.status_code}")
            return
    except Exception as e:
        print(f"   ❌ 获取配置文件异常: {e}")
        return
    
    # 2. 测试不同的调试端口
    debug_ports_to_test = [9222, 9223, 9224, 9225, 12345, 8080, 8888]
    
    for debug_port in debug_ports_to_test:
        print(f"\n🚀 步骤 2: 测试调试端口 {debug_port}...")
        
        # 启动会话
        try:
            payload = json.dumps({
                "uuid": profile_uuid,
                "headless": False,
                "debug_port": debug_port
            }, indent=4)
            
            headers = {'Content-Type': 'application/json'}
            response = requests.post(
                "http://127.0.0.1:36555/sessions/start", 
                data=payload, 
                headers=headers, 
                timeout=15
            )
            
            print(f"   启动请求状态码: {response.status_code}")
            print(f"   启动请求响应: {response.text}")
            
            if response.status_code in [200, 409]:  # 200=成功, 409=已运行
                session_data = response.json() if response.status_code == 200 else {"debug_port": debug_port}
                actual_debug_port = session_data.get('debug_port', debug_port)
                
                print(f"   ✅ 会话启动成功，调试端口: {actual_debug_port}")
                
                # 等待浏览器启动
                print(f"   ⏳ 等待浏览器启动...")
                time.sleep(5)
                
                # 3. 检查端口连通性
                print(f"\n🔍 步骤 3: 检查端口 {actual_debug_port} 连通性...")
                
                if check_port_open("127.0.0.1", actual_debug_port):
                    print(f"   ✅ 端口 {actual_debug_port} 已开放")
                    
                    # 4. 检查 Chrome 调试 API
                    print(f"\n🌐 步骤 4: 检查 Chrome 调试 API...")
                    if check_chrome_debug_api(actual_debug_port):
                        print(f"\n🎉 成功！调试端口 {actual_debug_port} 完全可用")
                        
                        # 5. 测试 Selenium 连接
                        print(f"\n🔧 步骤 5: 测试 Selenium 连接...")
                        test_selenium_connection(actual_debug_port)
                        return actual_debug_port
                    else:
                        print(f"   ❌ Chrome 调试 API 不可用")
                else:
                    print(f"   ❌ 端口 {actual_debug_port} 未开放")
                    
                    # 检查其他可能的端口
                    print(f"   🔍 检查其他可能的端口...")
                    for alt_port in range(actual_debug_port, actual_debug_port + 10):
                        if check_port_open("127.0.0.1", alt_port):
                            print(f"      发现开放端口: {alt_port}")
                            if check_chrome_debug_api(alt_port):
                                print(f"      🎯 端口 {alt_port} 有 Chrome 调试 API！")
                                test_selenium_connection(alt_port)
                                return alt_port
            else:
                print(f"   ❌ 会话启动失败")
                
        except Exception as e:
            print(f"   ❌ 启动会话异常: {e}")
    
    print(f"\n❌ 所有调试端口测试都失败")
    
    # 6. 扫描所有开放的端口
    print(f"\n🔍 扫描所有可能的调试端口...")
    scan_debug_ports()

def test_selenium_connection(debug_port):
    """测试 Selenium 连接"""
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        
        chrome_options = Options()
        chrome_options.add_experimental_option("debuggerAddress", f"127.0.0.1:{debug_port}")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        print(f"   尝试连接到 127.0.0.1:{debug_port}...")
        driver = webdriver.Chrome(options=chrome_options)
        
        # 测试基本操作
        current_url = driver.current_url
        title = driver.title
        
        print(f"   ✅ Selenium 连接成功！")
        print(f"      当前URL: {current_url}")
        print(f"      页面标题: {title}")
        
        driver.quit()
        return True
        
    except Exception as e:
        print(f"   ❌ Selenium 连接失败: {str(e)[:100]}...")
        return False

def scan_debug_ports():
    """扫描可能的调试端口"""
    port_ranges = [
        (9220, 9230),   # Chrome 默认范围
        (8080, 8090),   # 常用端口
        (12340, 12350), # Linken Sphere 可能使用的端口
        (40080, 40090), # 基于之前的测试
    ]
    
    found_ports = []
    
    for start_port, end_port in port_ranges:
        print(f"   扫描端口范围: {start_port}-{end_port}")
        for port in range(start_port, end_port + 1):
            if check_port_open("127.0.0.1", port):
                print(f"      发现开放端口: {port}")
                if check_chrome_debug_api(port):
                    print(f"      🎯 端口 {port} 有 Chrome 调试 API！")
                    found_ports.append(port)
    
    if found_ports:
        print(f"\n🎉 找到 {len(found_ports)} 个可用的调试端口: {found_ports}")
        for port in found_ports:
            print(f"\n测试端口 {port}:")
            test_selenium_connection(port)
    else:
        print(f"\n❌ 未找到任何可用的调试端口")

def main():
    """主函数"""
    working_port = start_linken_sphere_session()
    
    if working_port:
        print(f"\n💡 建议更新代码使用端口: {working_port}")
    else:
        print(f"\n💡 建议:")
        print("1. 检查 Linken Sphere 设置中的远程调试选项")
        print("2. 尝试手动启动浏览器并启用调试模式")
        print("3. 查看 Linken Sphere 文档中的调试端口配置")

if __name__ == "__main__":
    main()
