#!/usr/bin/env python3
"""
重置 Linken Sphere 会话并重新启动
"""

import requests
import json
import time

def reset_and_restart():
    """重置并重新启动 Linken Sphere 会话"""
    print("🔄 重置 Linken Sphere 会话")
    print("=" * 50)
    
    base_url = "http://127.0.0.1:36555"
    
    # 1. 获取配置文件
    print("📋 获取配置文件...")
    try:
        response = requests.get(f"{base_url}/sessions", timeout=10)
        if response.status_code == 200:
            profiles = response.json()
            if profiles:
                profile = profiles[0]
                profile_uuid = profile.get('uuid')
                profile_name = profile.get('name')
                profile_status = profile.get('status')
                
                print(f"   配置文件: {profile_name}")
                print(f"   UUID: {profile_uuid}")
                print(f"   当前状态: {profile_status}")
            else:
                print("   ❌ 没有可用的配置文件")
                return
        else:
            print(f"   ❌ 获取配置文件失败: {response.status_code}")
            return
    except Exception as e:
        print(f"   ❌ 获取配置文件异常: {e}")
        return
    
    # 2. 如果会话正在运行，先停止
    if profile_status in ["automationRunning", "running"]:
        print(f"\n🛑 停止现有会话...")
        try:
            stop_payload = json.dumps({
                "uuid": profile_uuid
            })
            
            headers = {'Content-Type': 'application/json'}
            response = requests.post(f"{base_url}/sessions/stop", data=stop_payload, headers=headers, timeout=10)
            
            print(f"   停止请求状态码: {response.status_code}")
            print(f"   停止请求响应: {response.text}")
            
            if response.status_code < 400:
                print("   ✅ 会话停止成功")
                time.sleep(3)  # 等待会话完全停止
            else:
                print("   ⚠️ 会话停止失败，继续尝试")
                
        except Exception as e:
            print(f"   ⚠️ 停止会话异常: {e}")
    
    # 3. 重新启动会话（不指定调试端口，让系统自动分配）
    print(f"\n🚀 重新启动会话...")
    try:
        # 尝试不同的启动方式
        start_configs = [
            # 配置1: 不指定调试端口
            {"uuid": profile_uuid, "headless": False},
            
            # 配置2: 指定常用调试端口
            {"uuid": profile_uuid, "headless": False, "debug_port": 9222},
            
            # 配置3: 指定其他调试端口
            {"uuid": profile_uuid, "headless": False, "debug_port": 9223},
        ]
        
        for i, config in enumerate(start_configs, 1):
            print(f"\n   尝试配置 {i}: {config}")
            
            payload = json.dumps(config, indent=4)
            headers = {'Content-Type': 'application/json'}
            
            response = requests.post(f"{base_url}/sessions/start", data=payload, headers=headers, timeout=15)
            
            print(f"   状态码: {response.status_code}")
            print(f"   响应: {response.text}")
            
            if response.status_code == 200:
                session_data = response.json()
                print(f"   ✅ 会话启动成功！")
                
                debug_port = session_data.get('debug_port')
                if debug_port:
                    print(f"   🎯 调试端口: {debug_port}")
                    
                    # 等待浏览器启动
                    print(f"   ⏳ 等待浏览器启动...")
                    time.sleep(5)
                    
                    # 检查端口
                    if check_debug_port(debug_port):
                        print(f"   🎉 调试端口 {debug_port} 可用！")
                        return debug_port
                    else:
                        print(f"   ❌ 调试端口 {debug_port} 不可用")
                else:
                    print(f"   ⚠️ 响应中没有调试端口信息")
                    
            elif response.status_code == 409:
                print(f"   ⚠️ 会话已在运行")
            else:
                print(f"   ❌ 启动失败")
    
    except Exception as e:
        print(f"   ❌ 启动会话异常: {e}")
    
    return None

def check_debug_port(port):
    """检查调试端口是否可用"""
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        result = sock.connect_ex(("127.0.0.1", port))
        sock.close()
        
        if result == 0:
            # 端口开放，检查是否是 Chrome 调试 API
            try:
                response = requests.get(f"http://127.0.0.1:{port}/json", timeout=3)
                if response.status_code == 200:
                    return True
            except:
                pass
        
        return False
    except:
        return False

def scan_all_debug_ports():
    """扫描所有可能的调试端口"""
    print(f"\n🔍 扫描所有可能的调试端口...")
    
    # 常见的调试端口范围
    port_ranges = [
        range(9220, 9230),
        range(8080, 8090),
        range(12340, 12350),
    ]
    
    found_ports = []
    
    for port_range in port_ranges:
        for port in port_range:
            if check_debug_port(port):
                print(f"   🎯 发现可用调试端口: {port}")
                found_ports.append(port)
    
    return found_ports

def main():
    """主函数"""
    working_port = reset_and_restart()
    
    if not working_port:
        print(f"\n🔍 自动启动失败，扫描现有端口...")
        found_ports = scan_all_debug_ports()
        
        if found_ports:
            working_port = found_ports[0]
            print(f"   使用发现的端口: {working_port}")
        else:
            print(f"   ❌ 未找到任何可用的调试端口")
    
    if working_port:
        print(f"\n🎉 成功！可用的调试端口: {working_port}")
        print(f"\n💡 更新代码建议:")
        print(f"   debug_port = {working_port}")
        
        # 测试 Selenium 连接
        print(f"\n🔧 测试 Selenium 连接...")
        test_selenium(working_port)
    else:
        print(f"\n❌ 无法找到可用的调试端口")
        print(f"\n💡 建议:")
        print("1. 手动打开 Linken Sphere")
        print("2. 创建一个配置文件")
        print("3. 在浏览器设置中启用远程调试")
        print("4. 手动启动浏览器并记录调试端口")

def test_selenium(debug_port):
    """测试 Selenium 连接"""
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        
        chrome_options = Options()
        chrome_options.add_experimental_option("debuggerAddress", f"127.0.0.1:{debug_port}")
        
        driver = webdriver.Chrome(options=chrome_options)
        print(f"   ✅ Selenium 连接成功！")
        print(f"   当前页面: {driver.current_url}")
        driver.quit()
        
    except Exception as e:
        print(f"   ❌ Selenium 连接失败: {str(e)[:100]}...")

if __name__ == "__main__":
    main()
