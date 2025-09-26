#!/usr/bin/env python3
"""
测试端口 10002 的连接
"""

import asyncio
import requests
import json
from playwright.async_api import async_playwright

async def test_port_10002():
    """测试端口 10002"""
    print("🧪 详细测试端口 10002...")
    
    # 1. 首先检查端口是否响应
    try:
        response = requests.get("http://127.0.0.1:10002/json", timeout=5)
        print(f"✅ 端口 10002 HTTP 响应: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   找到 {len(data)} 个标签页")
            for i, tab in enumerate(data[:3]):
                print(f"   标签页 {i+1}: {tab.get('title', 'No title')}")
                print(f"             URL: {tab.get('url', 'No URL')}")
    except Exception as e:
        print(f"❌ HTTP 请求失败: {e}")
        return False
    
    # 2. 测试 Playwright 连接
    try:
        playwright = await async_playwright().start()
        browser = await playwright.chromium.connect_over_cdp("http://127.0.0.1:10002")
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
                    
                except Exception as e:
                    print(f"⚠️ 页面操作测试失败: {e}")
        
        await browser.close()
        await playwright.stop()
        return True
        
    except Exception as e:
        print(f"❌ Playwright 连接失败: {e}")
        return False

async def test_linken_sphere_with_port_10002():
    """测试使用端口 10002 启动 Linken Sphere 会话"""
    print("\n🔄 测试使用端口 10002 启动会话...")
    
    try:
        # 获取配置文件
        response = requests.get("http://127.0.0.1:36555/sessions", timeout=10)
        sessions = response.json()
        
        if not sessions:
            print("❌ 没有找到会话")
            return False
        
        uuid = sessions[0]['uuid']
        print(f"使用配置文件: {sessions[0]['name']}")
        
        # 尝试启动会话，指定端口 10002
        payload = json.dumps({
            "uuid": uuid,
            "headless": False,
            "debug_port": 10002
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
            # 测试连接
            success = await test_port_10002()
            return success
        else:
            print("❌ 会话启动失败")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

async def main():
    """主函数"""
    print("🔍 测试端口 10002 连接")
    print("=" * 40)
    
    # 直接测试当前端口
    success1 = await test_port_10002()
    
    # 测试重新启动会话
    success2 = await test_linken_sphere_with_port_10002()
    
    print("\n" + "=" * 40)
    print("📊 测试结果:")
    print(f"   直接连接测试: {'✅ 成功' if success1 else '❌ 失败'}")
    print(f"   会话重启测试: {'✅ 成功' if success2 else '❌ 失败'}")
    
    if success1 or success2:
        print("\n🎉 端口 10002 可用！")
        print("💡 建议修改主程序使用端口 10002")
    else:
        print("\n❌ 端口 10002 不可用")

if __name__ == "__main__":
    asyncio.run(main())
