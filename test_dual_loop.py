#!/usr/bin/env python3
"""
双层循环逻辑测试脚本
验证时间控制精度和循环结构
"""

import asyncio
import random
import time
from playwright.async_api import async_playwright

class DualLoopTester:
    def __init__(self, browse_duration=10, major_cycles=2):
        """
        测试用的双层循环浏览器
        
        Args:
            browse_duration (int): 每页浏览时间（秒，测试用较短时间）
            major_cycles (int): 大循环次数
        """
        self.browse_duration = browse_duration
        self.major_cycles = major_cycles
        self.minor_cycles_per_major = 8
        self.base_url = "https://www.apple.com/jp/"
        self.visited_links = []
        self.available_links = []
        self.timing_log = []

    async def test_precise_timing(self, page, duration):
        """测试精确时间控制"""
        start_time = time.time()
        print(f"⏱️  开始精确时间测试，目标时长: {duration}秒")
        
        # 模拟滚动到底部（快速版本用于测试）
        scroll_start = time.time()
        await self._quick_scroll_to_bottom(page)
        scroll_end = time.time()
        scroll_duration = scroll_end - scroll_start
        
        print(f"📜 滚动完成，耗时: {scroll_duration:.2f}秒")
        
        # 等待剩余时间
        elapsed = time.time() - start_time
        remaining = max(0, duration - elapsed)
        
        if remaining > 0:
            print(f"⏳ 等待剩余时间: {remaining:.2f}秒")
            await asyncio.sleep(remaining)
        
        total_duration = time.time() - start_time
        error = abs(total_duration - duration)
        
        print(f"✅ 时间控制完成")
        print(f"   目标时间: {duration:.2f}秒")
        print(f"   实际时间: {total_duration:.2f}秒")
        print(f"   时间误差: {error:.2f}秒")
        
        # 记录时间数据
        self.timing_log.append({
            'target': duration,
            'actual': total_duration,
            'error': error,
            'scroll_time': scroll_duration
        })
        
        return total_duration

    async def _quick_scroll_to_bottom(self, page):
        """快速滚动到底部（测试用）"""
        scroll_position = 0
        
        while True:
            page_info = await page.evaluate("""
                () => ({
                    scrollHeight: document.body.scrollHeight,
                    clientHeight: window.innerHeight
                })
            """)
            
            max_scroll = page_info['scrollHeight'] - page_info['clientHeight']
            if scroll_position >= max_scroll:
                break
            
            scroll_distance = random.randint(300, 500)
            scroll_position = min(scroll_position + scroll_distance, max_scroll)
            
            await page.evaluate(f"window.scrollTo({{top: {scroll_position}, behavior: 'smooth'}})")
            await asyncio.sleep(0.2)  # 快速滚动用于测试

    async def get_test_links(self, page):
        """获取测试链接"""
        try:
            links = await page.evaluate("""
                () => {
                    const links = [];
                    const allLinks = document.querySelectorAll('a');
                    allLinks.forEach(link => {
                        if (link.href && link.href.includes('apple.com/jp/') && 
                            !link.href.includes('#') && 
                            link.href !== window.location.href) {
                            links.push({
                                url: link.href,
                                text: link.textContent.trim()
                            });
                        }
                    });
                    return links;
                }
            """)
            
            # 去重
            unique_links = []
            seen_urls = set()
            for link in links:
                if link['url'] not in seen_urls:
                    unique_links.append(link)
                    seen_urls.add(link['url'])
            
            return unique_links[:10]  # 限制数量用于测试
            
        except Exception as e:
            print(f"❌ 获取链接失败: {e}")
            return []

    async def run_test(self):
        """运行双层循环测试"""
        total_pages = self.major_cycles * self.minor_cycles_per_major
        
        print("🧪 双层循环逻辑测试")
        print("=" * 50)
        print(f"📊 测试配置:")
        print(f"   每页浏览时间: {self.browse_duration}秒")
        print(f"   大循环次数: {self.major_cycles}")
        print(f"   每个大循环: {self.minor_cycles_per_major} 次页面访问")
        print(f"   总页面访问: {total_pages}")
        print("=" * 50)
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            page = await browser.new_page()
            
            try:
                test_start_time = time.time()
                
                # 外层循环：大循环
                for major_cycle in range(self.major_cycles):
                    print(f"\n🔄 大循环 {major_cycle + 1}/{self.major_cycles} 开始")
                    
                    # 刷新链接
                    print("🔗 刷新链接列表...")
                    await page.goto(self.base_url)
                    await page.wait_for_load_state("networkidle")
                    
                    self.available_links = await self.get_test_links(page)
                    self.visited_links.clear()
                    
                    print(f"   找到 {len(self.available_links)} 个可用链接")
                    
                    # 内层循环：8次页面访问
                    for minor_cycle in range(self.minor_cycles_per_major):
                        page_number = major_cycle * self.minor_cycles_per_major + minor_cycle + 1
                        
                        print(f"\n   📄 小循环 {minor_cycle + 1}/8 (总第 {page_number}/{total_pages} 页)")
                        
                        if self.available_links:
                            selected_link = random.choice(self.available_links)
                            print(f"      访问: {selected_link['text'][:50]}...")
                            
                            try:
                                await page.goto(selected_link['url'])
                                await page.wait_for_load_state("networkidle")
                                
                                # 精确时间控制测试
                                actual_time = await self.test_precise_timing(page, self.browse_duration)
                                
                            except Exception as e:
                                print(f"      ❌ 页面访问失败: {e}")
                        else:
                            print("      ⚠️  没有可用链接，访问主页")
                            await page.goto(self.base_url)
                            await self.test_precise_timing(page, self.browse_duration)
                    
                    print(f"✅ 大循环 {major_cycle + 1}/{self.major_cycles} 完成")
                
                # 测试结果统计
                test_end_time = time.time()
                total_test_time = test_end_time - test_start_time
                
                print("\n" + "=" * 50)
                print("📈 测试结果统计")
                print("=" * 50)
                
                if self.timing_log:
                    avg_error = sum(log['error'] for log in self.timing_log) / len(self.timing_log)
                    max_error = max(log['error'] for log in self.timing_log)
                    
                    print(f"⏱️  时间控制精度:")
                    print(f"   平均误差: {avg_error:.2f}秒")
                    print(f"   最大误差: {max_error:.2f}秒")
                    print(f"   测试页面数: {len(self.timing_log)}")
                
                print(f"🕐 总测试时间: {total_test_time:.2f}秒")
                print(f"📊 预期时间: {total_pages * self.browse_duration}秒")
                print("✅ 双层循环测试完成！")
                
            finally:
                await browser.close()

async def main():
    """主测试函数"""
    print("选择测试模式:")
    print("1. 快速测试 (10秒/页, 2个大循环)")
    print("2. 标准测试 (30秒/页, 2个大循环)")
    print("3. 自定义测试")
    
    choice = input("请选择 (1-3): ").strip()
    
    if choice == "1":
        tester = DualLoopTester(browse_duration=10, major_cycles=2)
    elif choice == "2":
        tester = DualLoopTester(browse_duration=30, major_cycles=2)
    elif choice == "3":
        try:
            duration = int(input("每页浏览时间（秒）: "))
            cycles = int(input("大循环次数: "))
            tester = DualLoopTester(browse_duration=duration, major_cycles=cycles)
        except ValueError:
            print("输入无效，使用默认配置")
            tester = DualLoopTester()
    else:
        print("使用默认快速测试")
        tester = DualLoopTester(browse_duration=10, major_cycles=2)
    
    await tester.run_test()

if __name__ == "__main__":
    asyncio.run(main())
