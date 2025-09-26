#!/usr/bin/env python3
"""
网络重试机制测试脚本
模拟网络问题并测试重试功能
"""

import asyncio
import random
import time
from playwright.async_api import async_playwright

class NetworkRetryTester:
    def __init__(self, max_retries=3, retry_delay=2):
        """
        网络重试测试器
        
        Args:
            max_retries (int): 最大重试次数
            retry_delay (int): 重试间隔时间（秒）
        """
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.test_stats = {
            'total_operations': 0,
            'successful_operations': 0,
            'failed_operations': 0,
            'total_retries': 0,
            'successful_retries': 0
        }

    async def retry_operation(self, operation_name, operation_func, *args, **kwargs):
        """通用重试机制"""
        self.test_stats['total_operations'] += 1
        
        for attempt in range(self.max_retries + 1):
            try:
                if attempt > 0:
                    print(f"🔄 {operation_name} - 第 {attempt} 次重试")
                    self.test_stats['total_retries'] += 1
                    await asyncio.sleep(self.retry_delay)
                
                result = await operation_func(*args, **kwargs)
                
                if attempt > 0:
                    print(f"✅ {operation_name} - 重试成功")
                    self.test_stats['successful_retries'] += 1
                
                self.test_stats['successful_operations'] += 1
                return result
                
            except Exception as e:
                if attempt < self.max_retries:
                    print(f"⚠️ {operation_name} - 尝试 {attempt + 1} 失败: {e}")
                else:
                    print(f"❌ {operation_name} - 所有重试都失败: {e}")
                    self.test_stats['failed_operations'] += 1
                    return None

    async def test_navigation_with_retry(self, page, url):
        """测试页面导航的重试机制"""
        async def _navigation_operation():
            # 随机模拟网络问题
            if random.random() < 0.3:  # 30% 概率模拟失败
                raise Exception("模拟网络超时")
            
            await page.goto(url, wait_until="domcontentloaded", timeout=15000)
            await page.wait_for_load_state("networkidle", timeout=8000)
            return True
        
        return await self.retry_operation(f"导航到 {url}", _navigation_operation)

    async def test_script_execution_with_retry(self, page, script, description):
        """测试脚本执行的重试机制"""
        async def _script_operation():
            # 随机模拟脚本执行失败
            if random.random() < 0.2:  # 20% 概率模拟失败
                raise Exception("模拟脚本执行错误")
            
            return await page.evaluate(script)
        
        return await self.retry_operation(description, _script_operation)

    async def test_link_extraction_with_retry(self, page):
        """测试链接提取的重试机制"""
        script = """
        () => {
            // 随机模拟DOM访问问题
            if (Math.random() < 0.25) {
                throw new Error('模拟DOM访问失败');
            }
            
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
            return links.slice(0, 5);
        }
        """
        
        return await self.test_script_execution_with_retry(page, script, "提取页面链接")

    async def run_comprehensive_test(self):
        """运行综合网络重试测试"""
        print("🧪 网络重试机制综合测试")
        print("=" * 50)
        print(f"配置: 最大重试 {self.max_retries} 次, 重试间隔 {self.retry_delay} 秒")
        print("模拟: 30% 导航失败率, 20% 脚本失败率, 25% DOM访问失败率")
        print("=" * 50)
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            page = await browser.new_page()
            
            try:
                test_start_time = time.time()
                
                # 测试1: 主页导航重试
                print("\n🌐 测试1: 主页导航重试机制")
                print("-" * 30)
                
                for i in range(3):
                    print(f"\n导航测试 {i+1}/3:")
                    result = await self.test_navigation_with_retry(page, "https://www.apple.com/jp/")
                    if result:
                        print("✅ 导航成功")
                    else:
                        print("❌ 导航最终失败")
                
                # 测试2: 链接提取重试
                print("\n🔗 测试2: 链接提取重试机制")
                print("-" * 30)
                
                for i in range(5):
                    print(f"\n链接提取测试 {i+1}/5:")
                    links = await self.test_link_extraction_with_retry(page)
                    if links:
                        print(f"✅ 成功提取 {len(links)} 个链接")
                        for link in links[:2]:  # 只显示前2个
                            print(f"   - {link['text'][:30]}...")
                    else:
                        print("❌ 链接提取失败")
                
                # 测试3: 页面信息获取重试
                print("\n📄 测试3: 页面信息获取重试机制")
                print("-" * 30)
                
                for i in range(4):
                    print(f"\n页面信息测试 {i+1}/4:")
                    page_info = await self.test_script_execution_with_retry(
                        page,
                        """
                        () => ({
                            title: document.title,
                            url: window.location.href,
                            scrollHeight: document.body.scrollHeight
                        })
                        """,
                        "获取页面基本信息"
                    )
                    
                    if page_info:
                        print(f"✅ 页面标题: {page_info['title'][:40]}...")
                        print(f"   页面高度: {page_info['scrollHeight']}px")
                    else:
                        print("❌ 页面信息获取失败")
                
                # 测试4: 滚动操作重试
                print("\n📜 测试4: 滚动操作重试机制")
                print("-" * 30)
                
                for i in range(3):
                    print(f"\n滚动测试 {i+1}/3:")
                    scroll_result = await self.test_script_execution_with_retry(
                        page,
                        f"window.scrollTo({{top: {(i+1) * 500}, behavior: 'smooth'}})",
                        f"滚动到位置 {(i+1) * 500}"
                    )
                    
                    if scroll_result is not None:
                        print("✅ 滚动操作成功")
                    else:
                        print("❌ 滚动操作失败")
                    
                    await asyncio.sleep(1)  # 等待滚动完成
                
                # 输出测试结果
                test_end_time = time.time()
                test_duration = test_end_time - test_start_time
                
                print("\n" + "=" * 50)
                print("📊 网络重试测试结果统计")
                print("=" * 50)
                
                stats = self.test_stats
                print(f"总操作次数: {stats['total_operations']}")
                print(f"成功操作次数: {stats['successful_operations']}")
                print(f"失败操作次数: {stats['failed_operations']}")
                print(f"总重试次数: {stats['total_retries']}")
                print(f"成功重试次数: {stats['successful_retries']}")
                
                if stats['total_operations'] > 0:
                    success_rate = (stats['successful_operations'] / stats['total_operations']) * 100
                    print(f"操作成功率: {success_rate:.1f}%")
                
                if stats['total_retries'] > 0:
                    retry_success_rate = (stats['successful_retries'] / stats['total_retries']) * 100
                    print(f"重试成功率: {retry_success_rate:.1f}%")
                else:
                    print("重试成功率: N/A (无重试发生)")
                
                print(f"测试总耗时: {test_duration:.2f}秒")
                
                # 评估重试机制效果
                print("\n🎯 重试机制效果评估:")
                if stats['successful_retries'] > 0:
                    print("✅ 重试机制有效，成功恢复了部分失败操作")
                else:
                    print("ℹ️ 测试期间未触发重试或重试未成功")
                
                if stats['failed_operations'] == 0:
                    print("🎉 所有操作最终都成功了！")
                elif stats['failed_operations'] < stats['total_operations'] * 0.1:
                    print("👍 失败率很低，重试机制表现良好")
                else:
                    print("⚠️ 仍有较多操作失败，可能需要调整重试参数")
                
                print("=" * 50)
                
            finally:
                await browser.close()

async def main():
    """主测试函数"""
    print("网络重试机制测试工具")
    print("此工具会模拟网络问题来测试重试功能的有效性")
    print()
    
    # 配置选项
    try:
        max_retries = int(input("请输入最大重试次数（默认3）: ") or "3")
        retry_delay = int(input("请输入重试间隔时间（秒，默认2）: ") or "2")
    except ValueError:
        max_retries = 3
        retry_delay = 2
        print("使用默认配置")
    
    tester = NetworkRetryTester(max_retries=max_retries, retry_delay=retry_delay)
    await tester.run_comprehensive_test()

if __name__ == "__main__":
    asyncio.run(main())
