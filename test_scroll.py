#!/usr/bin/env python3
"""
测试滚动行为的脚本
只向下滚动，到底部后重新从顶部开始
"""

import asyncio
import random
import time
from playwright.async_api import async_playwright

async def test_downward_scroll(page, duration):
    """
    测试纯向下滚动
    """
    print(f"开始测试向下滚动 {duration} 秒...")
    
    start_time = time.time()
    scroll_position = 0
    scroll_count = 0
    
    while time.time() - start_time < duration:
        # 获取当前页面信息
        page_info = await page.evaluate("""
            () => ({
                scrollHeight: document.body.scrollHeight,
                clientHeight: window.innerHeight,
                scrollTop: window.pageYOffset
            })
        """)
        
        print(f"当前滚动位置: {page_info['scrollTop']}, 页面高度: {page_info['scrollHeight']}")
        
        # 计算向下滚动距离
        scroll_distance = random.randint(150, 300)
        new_position = scroll_position + scroll_distance
        max_scroll = page_info['scrollHeight'] - page_info['clientHeight']
        
        # 如果超过页面底部，重新从顶部开始
        if new_position >= max_scroll:
            print("📍 到达页面底部，重新从顶部开始滚动")
            scroll_position = 0
            await page.evaluate("window.scrollTo({top: 0, behavior: 'smooth'})")
            await asyncio.sleep(2)  # 给用户时间看到回到顶部
        else:
            scroll_position = new_position
            await page.evaluate(f"window.scrollTo({{top: {scroll_position}, behavior: 'smooth'}})")
        
        scroll_count += 1
        print(f"第 {scroll_count} 次滚动，目标位置: {scroll_position}")
        
        # 随机停顿时间
        pause_time = random.uniform(1.0, 2.5)
        print(f"停顿 {pause_time:.1f} 秒...")
        await asyncio.sleep(pause_time)
        
        # 偶尔长时间停顿，模拟阅读
        if random.random() < 0.2:  # 20% 概率
            reading_time = random.uniform(2.0, 4.0)
            print(f"📖 模拟阅读，停顿 {reading_time:.1f} 秒...")
            await asyncio.sleep(reading_time)
    
    print(f"✅ 滚动测试完成，总共滚动 {scroll_count} 次")

async def main():
    """主测试函数"""
    print("Apple 网站向下滚动测试")
    print("=" * 40)
    
    # 获取测试参数
    try:
        test_duration = int(input("请输入测试时长（秒，默认30）: ") or "30")
    except ValueError:
        test_duration = 30
        print("使用默认测试时长: 30秒")
    
    async with async_playwright() as p:
        # 启动浏览器
        browser = await p.chromium.launch(headless=False, slow_mo=100)
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080}
        )
        page = await context.new_page()
        
        try:
            print("正在访问 Apple 日本官网...")
            await page.goto("https://www.apple.com/jp/", wait_until="domcontentloaded")
            await page.wait_for_load_state("networkidle")
            
            print("页面加载完成，开始滚动测试...")
            await asyncio.sleep(2)  # 给用户时间看到页面
            
            # 执行滚动测试
            await test_downward_scroll(page, test_duration)
            
            print("\n🎉 测试完成！浏览器将在5秒后关闭...")
            await asyncio.sleep(5)
            
        except Exception as e:
            print(f"❌ 测试过程中出错: {e}")
        
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
