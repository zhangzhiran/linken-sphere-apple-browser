#!/usr/bin/env python3
"""
测试使用 36555 端口作为调试端口
"""

import asyncio
import requests
import json
from playwright.async_api import async_playwright

async def test_port_36555_as_debug():
    """测试端口 36555 作为调试端口"""
    print("🧪 测试端口 36555 作为调试端口...")
    
    # 1. 检查端口是否响应调试协议
    try:
        response = requests.get("http://127.0.0.1:36555/json", timeout=5)
        print(f"📋 端口 36555 /json 响应: {response.status_code}")
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"   找到 {len(data)} 个标签页")
                for i, tab in enumerate(data[:3]):
                    print(f"   标签页 {i+1}: {tab.get('title', 'No title')}")
                    print(f"             URL: {tab.get('url', 'No URL')}")
            except:
                print(f"   响应内容: {response.text[:200]}...")
        else:
            print(f"   错误响应: {response.text}")
    except Exception as e:
        print(f"❌ HTTP /json 请求失败: {e}")
    
    # 2. 检查其他调试端点
    debug_endpoints = ["/json/version", "/json/list", "/json/new", "/"]
    for endpoint in debug_endpoints:
        try:
            response = requests.get(f"http://127.0.0.1:36555{endpoint}", timeout=3)
            print(f"📋 端点 {endpoint}: {response.status_code}")
            if response.status_code == 200 and len(response.text) < 500:
                print(f"   响应: {response.text}")
        except Exception as e:
            print(f"❌ 端点 {endpoint} 失败: {e}")
    
    # 3. 测试 Playwright 连接
    try:
        print("\n🧪 测试 Playwright 连接到端口 36555...")
        playwright = await async_playwright().start()
        browser = await playwright.chromium.connect_over_cdp("http://127.0.0.1:36555")
        print("✅ Playwright 连接成功！")
        
        # 获取页面信息
        contexts = browser.contexts
        print(f"   找到 {len(contexts)} 个上下文")
        
        if contexts:
            context = contexts[0]
            pages = context.pages
            print(f"   找到 {len(pages)} 个页面")
            
            if pages:
                page = pages[0]
                try:
                    url = await page.url()
                    title = await page.title()
                    print(f"   当前页面标题: {title}")
                    print(f"   当前页面URL: {url}")
                    
                    # 测试基本操作
                    print("🧪 测试基本页面操作...")
                    await page.goto("https://www.apple.com/jp/", timeout=30000)
                    await page.wait_for_load_state("domcontentloaded")
                    new_title = await page.title()
                    print(f"✅ 成功导航到 Apple Japan: {new_title}")
                    
                    return True
                    
                except Exception as e:
                    print(f"⚠️ 页面操作测试失败: {e}")
                    return True  # 连接成功，但操作失败
        
        await browser.close()
        await playwright.stop()
        return True
        
    except Exception as e:
        print(f"❌ Playwright 连接失败: {e}")
        return False

async def test_linken_sphere_with_port_36555():
    """测试使用端口 36555 启动 Linken Sphere 会话"""
    print("\n🔄 测试使用端口 36555 启动会话...")
    
    try:
        # 获取配置文件
        response = requests.get("http://127.0.0.1:36555/sessions", timeout=10)
        sessions = response.json()
        
        if not sessions:
            print("❌ 没有找到会话")
            return False
        
        uuid = sessions[0]['uuid']
        print(f"使用配置文件: {sessions[0]['name']}")
        
        # 尝试启动会话，指定端口 36555 作为调试端口
        payload = json.dumps({
            "uuid": uuid,
            "headless": False,
            "debug_port": 36555
        })
        
        headers = {'Content-Type': 'application/json'}
        response = requests.post(
            "http://127.0.0.1:36555/sessions/start", 
            data=payload, 
            headers=headers, 
            timeout=15
        )
        
        print(f"启动响应: {response.status_code} - {response.text}")
        
        if response.status_code in [200, 409]:
            # 等待一下让会话启动
            await asyncio.sleep(3)
            
            # 测试连接
            success = await test_port_36555_as_debug()
            return success
        else:
            print("❌ 会话启动失败")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

async def test_different_debug_ports():
    """测试不同的调试端口配置"""
    print("\n🔄 测试不同调试端口配置...")
    
    try:
        # 获取配置文件
        response = requests.get("http://127.0.0.1:36555/sessions", timeout=10)
        sessions = response.json()
        
        if not sessions:
            print("❌ 没有找到会话")
            return
        
        uuid = sessions[0]['uuid']
        print(f"使用配置文件: {sessions[0]['name']}")
        
        # 测试不同的调试端口
        test_ports = [36555, 9222, 10002, 40080, 12345]
        
        for port in test_ports:
            print(f"\n--- 测试调试端口 {port} ---")
            
            # 启动会话
            payload = json.dumps({
                "uuid": uuid,
                "headless": False,
                "debug_port": port
            })
            
            headers = {'Content-Type': 'application/json'}
            response = requests.post(
                "http://127.0.0.1:36555/sessions/start", 
                data=payload, 
                headers=headers, 
                timeout=15
            )
            
            print(f"启动响应: {response.status_code}")
            
            if response.status_code in [200, 409]:
                # 等待会话启动
                await asyncio.sleep(2)
                
                # 测试调试端口连接
                try:
                    debug_response = requests.get(f"http://127.0.0.1:{port}/json", timeout=3)
                    if debug_response.status_code == 200:
                        data = debug_response.json()
                        print(f"✅ 调试端口 {port} 可用，找到 {len(data)} 个标签页")
                        
                        # 测试 Playwright 连接
                        try:
                            playwright = await async_playwright().start()
                            browser = await playwright.chromium.connect_over_cdp(f"http://127.0.0.1:{port}")
                            print(f"✅ Playwright 成功连接到端口 {port}")
                            await browser.close()
                            await playwright.stop()
                        except Exception as e:
                            print(f"❌ Playwright 连接端口 {port} 失败: {e}")
                    else:
                        print(f"❌ 调试端口 {port} 不可用: {debug_response.status_code}")
                except Exception as e:
                    print(f"❌ 调试端口 {port} 连接失败: {e}")
            else:
                print(f"❌ 会话启动失败: {response.text}")
            
            # 停止会话以便测试下一个端口
            try:
                stop_payload = json.dumps({"uuid": uuid})
                requests.post(
                    "http://127.0.0.1:36555/sessions/stop", 
                    data=stop_payload, 
                    headers=headers, 
                    timeout=10
                )
                await asyncio.sleep(1)
            except:
                pass
                
    except Exception as e:
        print(f"❌ 测试失败: {e}")

async def main():
    """主函数"""
    print("🔍 测试端口 36555 作为调试端口")
    print("=" * 50)
    
    # 1. 直接测试端口 36555 作为调试端口
    print("1️⃣ 直接测试端口 36555...")
    success1 = await test_port_36555_as_debug()
    
    # 2. 测试重新启动会话使用端口 36555
    print("\n2️⃣ 测试重启会话使用端口 36555...")
    success2 = await test_linken_sphere_with_port_36555()
    
    # 3. 测试不同调试端口配置
    print("\n3️⃣ 测试不同调试端口配置...")
    await test_different_debug_ports()
    
    print("\n" + "=" * 50)
    print("📊 测试结果:")
    print(f"   直接连接端口 36555: {'✅ 成功' if success1 else '❌ 失败'}")
    print(f"   会话重启端口 36555: {'✅ 成功' if success2 else '❌ 失败'}")
    
    if success1 or success2:
        print("\n🎉 端口 36555 可以作为调试端口使用！")
        print("💡 建议修改主程序使用端口 36555")
    else:
        print("\n❌ 端口 36555 不能作为调试端口使用")
        print("💡 建议继续使用端口 10002 或寻找其他可用端口")

if __name__ == "__main__":
    asyncio.run(main())
