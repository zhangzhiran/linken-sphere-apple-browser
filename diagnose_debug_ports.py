#!/usr/bin/env python3
"""
诊断 Linken Sphere 调试端口的脚本
"""

import requests
import json
import subprocess
import re

def get_linken_sphere_sessions():
    """获取 Linken Sphere 会话信息"""
    try:
        response = requests.get("http://127.0.0.1:36555/sessions", timeout=10)
        response.raise_for_status()
        sessions = response.json()
        print(f"📋 找到 {len(sessions)} 个会话:")
        for i, session in enumerate(sessions, 1):
            print(f"   {i}. {session.get('name', 'Unknown')} - 状态: {session.get('status', 'Unknown')}")
            print(f"      UUID: {session.get('uuid', 'Unknown')}")
        return sessions
    except Exception as e:
        print(f"❌ 获取会话失败: {e}")
        return []

def start_session_with_custom_port(uuid, debug_port):
    """使用自定义调试端口启动会话"""
    try:
        payload = json.dumps({
            "uuid": uuid,
            "headless": False,
            "debug_port": debug_port
        })
        
        headers = {'Content-Type': 'application/json'}
        response = requests.post(
            "http://127.0.0.1:36555/sessions/start", 
            data=payload, 
            headers=headers, 
            timeout=15
        )
        
        print(f"🔄 启动会话响应 (端口 {debug_port}):")
        print(f"   状态码: {response.status_code}")
        print(f"   响应: {response.text}")
        
        if response.status_code in [200, 409]:
            return response.json() if response.text else {"debug_port": debug_port}
        return None
        
    except Exception as e:
        print(f"❌ 启动会话失败: {e}")
        return None

def scan_debug_ports():
    """扫描可能的调试端口"""
    print("\n🔍 扫描调试端口...")
    
    # 常见的调试端口
    ports_to_check = [9222, 9223, 9224, 9225, 12345, 40080, 40081, 40082]
    
    active_ports = []
    
    for port in ports_to_check:
        try:
            # 尝试访问调试端点
            response = requests.get(f"http://127.0.0.1:{port}/json", timeout=2)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 端口 {port}: 活跃 - 找到 {len(data)} 个标签页")
                active_ports.append(port)
                
                # 显示前几个标签页信息
                for i, tab in enumerate(data[:3]):
                    print(f"      标签页 {i+1}: {tab.get('title', 'No title')[:50]}")
                    print(f"                URL: {tab.get('url', 'No URL')[:80]}")
            else:
                print(f"❌ 端口 {port}: 无响应")
        except:
            print(f"❌ 端口 {port}: 连接失败")
    
    return active_ports

def check_netstat_ports():
    """使用 netstat 检查监听端口"""
    print("\n🔍 检查系统监听端口...")
    
    try:
        # Windows netstat 命令
        result = subprocess.run(
            ["netstat", "-an"], 
            capture_output=True, 
            text=True, 
            timeout=10
        )
        
        if result.returncode == 0:
            lines = result.stdout.split('\n')
            listening_ports = []
            
            for line in lines:
                if 'LISTENING' in line and '127.0.0.1:' in line:
                    # 提取端口号
                    match = re.search(r'127\.0\.0\.1:(\d+)', line)
                    if match:
                        port = int(match.group(1))
                        if 9000 <= port <= 50000:  # 只关注可能的调试端口范围
                            listening_ports.append(port)
            
            listening_ports = sorted(set(listening_ports))
            print(f"📋 发现 {len(listening_ports)} 个本地监听端口:")
            for port in listening_ports:
                print(f"   - 127.0.0.1:{port}")
            
            return listening_ports
        else:
            print("❌ netstat 命令执行失败")
            return []
            
    except Exception as e:
        print(f"❌ 检查端口失败: {e}")
        return []

def test_playwright_connection(port):
    """测试 Playwright 连接"""
    print(f"\n🧪 测试 Playwright 连接到端口 {port}...")
    
    try:
        import asyncio
        from playwright.async_api import async_playwright
        
        async def test_connection():
            playwright = await async_playwright().start()
            try:
                browser = await playwright.chromium.connect_over_cdp(f"http://127.0.0.1:{port}")
                print(f"✅ Playwright 成功连接到端口 {port}")
                
                # 获取页面信息
                contexts = browser.contexts
                if contexts:
                    context = contexts[0]
                    pages = context.pages
                    print(f"   找到 {len(pages)} 个页面")
                    if pages:
                        page = pages[0]
                        url = await page.url()
                        title = await page.title()
                        print(f"   当前页面: {title}")
                        print(f"   URL: {url}")
                
                await browser.close()
                return True
            except Exception as e:
                print(f"❌ Playwright 连接失败: {e}")
                return False
            finally:
                await playwright.stop()
        
        return asyncio.run(test_connection())
        
    except Exception as e:
        print(f"❌ 测试连接时出错: {e}")
        return False

def main():
    """主函数"""
    print("🔍 Linken Sphere 调试端口诊断工具")
    print("=" * 50)
    
    # 1. 获取会话信息
    sessions = get_linken_sphere_sessions()
    if not sessions:
        print("❌ 无法获取会话信息，请确保 Linken Sphere 正在运行")
        return
    
    # 2. 扫描调试端口
    active_ports = scan_debug_ports()
    
    # 3. 检查系统端口
    system_ports = check_netstat_ports()
    
    # 4. 尝试不同的调试端口启动会话
    if sessions:
        session = sessions[0]
        uuid = session.get('uuid')
        
        print(f"\n🔄 尝试使用不同调试端口启动会话...")
        
        # 尝试常见端口
        test_ports = [9222, 9223, 9224, 12345] + active_ports + system_ports
        test_ports = sorted(set(test_ports))  # 去重并排序
        
        successful_ports = []
        
        for port in test_ports[:10]:  # 限制测试数量
            print(f"\n--- 测试端口 {port} ---")
            session_data = start_session_with_custom_port(uuid, port)
            
            if session_data:
                # 测试 Playwright 连接
                if test_playwright_connection(port):
                    successful_ports.append(port)
                    print(f"🎉 端口 {port} 完全可用！")
                else:
                    print(f"⚠️ 端口 {port} 会话启动成功，但 Playwright 连接失败")
            else:
                print(f"❌ 端口 {port} 会话启动失败")
    
    # 5. 总结
    print("\n" + "=" * 50)
    print("📊 诊断结果总结")
    print("=" * 50)
    
    if active_ports:
        print(f"✅ 发现活跃调试端口: {active_ports}")
    else:
        print("❌ 未发现活跃调试端口")
    
    if 'successful_ports' in locals() and successful_ports:
        print(f"🎉 可用的调试端口: {successful_ports}")
        print(f"\n💡 建议修改程序中的调试端口为: {successful_ports[0]}")
    else:
        print("❌ 未找到可用的调试端口")
        print("\n💡 建议:")
        print("   1. 确保 Linken Sphere 中启用了远程调试")
        print("   2. 检查 Linken Sphere 的调试端口设置")
        print("   3. 尝试重启 Linken Sphere")

if __name__ == "__main__":
    main()
