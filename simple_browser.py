#!/usr/bin/env python3
"""
简化版 Apple 网站浏览器 - 双层循环版本
"""

import asyncio
import random
import time
from playwright.async_api import async_playwright

# 简单的链接过滤函数
def filter_blocked_links(links):
    """过滤掉被屏蔽的链接"""
    blocked_patterns = ['search', '/search', '/search/']
    filtered = []
    blocked_count = 0

    for link in links:
        url = str(link).lower()
        if not any(pattern in url for pattern in blocked_patterns):
            filtered.append(link)
        else:
            blocked_count += 1

    if blocked_count > 0:
        print(f"🚫 已屏蔽 {blocked_count} 个搜索相关链接")

    return filtered

# 重试配置
MAX_RETRIES = 3
RETRY_DELAY = 3  # 秒

async def safe_goto(page, url, max_retries=MAX_RETRIES):
    """安全的页面导航，带重试机制"""
    for attempt in range(max_retries + 1):
        try:
            if attempt > 0:
                print(f"🔄 导航重试 {attempt}/{max_retries}: {url}")
                await asyncio.sleep(RETRY_DELAY)

            await page.goto(url)
            await page.wait_for_load_state("networkidle")
            return True

        except Exception as e:
            if attempt < max_retries:
                print(f"⚠️ 导航失败，准备重试: {e}")
            else:
                print(f"❌ 导航最终失败: {e}")
                return False

    return False

async def safe_evaluate(page, script, description="执行脚本", max_retries=MAX_RETRIES):
    """安全的脚本执行，带重试机制"""
    for attempt in range(max_retries + 1):
        try:
            if attempt > 0:
                print(f"🔄 脚本执行重试 {attempt}/{max_retries}: {description}")
                await asyncio.sleep(RETRY_DELAY)

            return await page.evaluate(script)

        except Exception as e:
            if attempt < max_retries:
                print(f"⚠️ 脚本执行失败，准备重试: {e}")
            else:
                print(f"❌ 脚本执行最终失败: {e}")
                return None

    return None

async def precise_browse_page(page, duration):
    """精确控制页面浏览时间：滚动到底部 + 等待剩余时间"""
    total_start_time = time.time()
    print(f"开始精确浏览页面，总时长: {duration}秒")

    # 阶段1: 滚动到底部
    scroll_start_time = time.time()
    await scroll_to_bottom(page)
    scroll_end_time = time.time()
    scroll_duration = scroll_end_time - scroll_start_time

    print(f"滚动阶段完成，耗时: {scroll_duration:.2f}秒")

    # 阶段2: 在底部等待剩余时间
    elapsed_time = time.time() - total_start_time
    remaining_time = max(0, duration - elapsed_time)

    if remaining_time > 0:
        print(f"在页面底部等待剩余时间: {remaining_time:.2f}秒")
        await asyncio.sleep(remaining_time)

    total_duration = time.time() - total_start_time
    print(f"页面浏览完成，实际总耗时: {total_duration:.2f}秒")

async def scroll_to_bottom(page):
    """向下滚动直到页面底部（带重试机制）"""
    print("开始向下滚动到页面底部")
    scroll_position = 0
    scroll_count = 0
    consecutive_failures = 0
    max_consecutive_failures = 3

    while True:
        # 安全获取页面信息
        page_info = await safe_evaluate(
            page,
            """
            () => ({
                scrollHeight: document.body.scrollHeight,
                clientHeight: window.innerHeight,
                scrollTop: window.pageYOffset
            })
            """,
            "获取页面滚动信息"
        )

        if page_info is None:
            consecutive_failures += 1
            print(f"⚠️ 获取页面信息失败，连续失败次数: {consecutive_failures}")

            if consecutive_failures >= max_consecutive_failures:
                print("❌ 连续获取页面信息失败，停止滚动")
                break

            await asyncio.sleep(2)
            continue

        # 重置连续失败计数
        consecutive_failures = 0

        # 检查是否已到达底部
        max_scroll = page_info['scrollHeight'] - page_info['clientHeight']
        if scroll_position >= max_scroll:
            print(f"✅ 已到达页面底部，总共滚动 {scroll_count} 次")
            break

        # 向下滚动
        scroll_distance = random.randint(150, 300)
        scroll_position = min(scroll_position + scroll_distance, max_scroll)

        # 安全执行滚动
        try:
            await page.evaluate(f"window.scrollTo({{top: {scroll_position}, behavior: 'smooth'}})")
            scroll_count += 1
        except Exception as e:
            print(f"⚠️ 滚动操作失败: {e}，继续尝试")
            # 即使滚动失败，也要继续，避免无限循环

        # 随机停顿
        await asyncio.sleep(random.uniform(0.8, 1.5))

async def main():
    """双层循环主函数"""
    BROWSE_TIME = 60    # 每页浏览时间
    MAJOR_CYCLES = 3    # 大循环次数
    MINOR_CYCLES = 8    # 每个大循环的页面访问次数
    BASE_URL = "https://www.apple.com/jp/"

    total_pages = MAJOR_CYCLES * MINOR_CYCLES
    print(f"简化版双层循环浏览器")
    print(f"大循环次数: {MAJOR_CYCLES}")
    print(f"每个大循环: {MINOR_CYCLES} 次页面访问")
    print(f"总页面访问: {total_pages}")
    print(f"每页时间: {BROWSE_TIME}秒")
    print("=" * 50)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        try:
            # 外层循环：大循环
            for major_cycle in range(MAJOR_CYCLES):
                print(f"\n=== 大循环 {major_cycle + 1}/{MAJOR_CYCLES} 开始 ===")

                # 安全返回主页并获取链接
                print("返回主页获取链接...")
                homepage_success = await safe_goto(page, BASE_URL)
                if not homepage_success:
                    print("❌ 无法返回主页，跳过此大循环")
                    continue

                # 安全获取可用链接
                links = await safe_evaluate(
                    page,
                    """
                    () => {
                        try {
                            const links = Array.from(document.querySelectorAll('a'))
                                .filter(a => a.href.includes('apple.com/jp/') &&
                                            !a.href.includes('#') &&
                                            a.href !== window.location.href)
                                .map(a => a.href);
                            return [...new Set(links)];
                        } catch (error) {
                            console.error('获取链接失败:', error);
                            return [];
                        }
                    }
                    """,
                    "获取页面链接"
                )

                if links is None:
                    links = []
                    print("⚠️ 获取链接失败，使用空链接列表")
                else:
                    # 过滤屏蔽的链接
                    original_count = len(links)
                    links = filter_blocked_links(links)
                    # 限制链接数量
                    links = links[:15]
                    print(f"找到 {original_count} 个链接，过滤后剩余 {len(links)} 个可用链接")

                # 内层循环：8次页面访问
                for minor_cycle in range(MINOR_CYCLES):
                    page_number = major_cycle * MINOR_CYCLES + minor_cycle + 1
                    print(f"\n--- 大循环 {major_cycle + 1}, 小循环 {minor_cycle + 1}/8 (总第 {page_number}/{total_pages} 页) ---")

                    if links:
                        # 随机选择链接
                        selected_link = random.choice(links)
                        print(f"访问: {selected_link}")

                        # 安全导航到选中的链接
                        navigation_success = await safe_goto(page, selected_link)
                        if navigation_success:
                            await precise_browse_page(page, BROWSE_TIME)
                        else:
                            print("⚠️ 页面导航失败，但仍等待指定时间")
                            await asyncio.sleep(BROWSE_TIME)
                    else:
                        print("没有可用链接，浏览主页")
                        homepage_success = await safe_goto(page, BASE_URL)
                        if homepage_success:
                            await precise_browse_page(page, BROWSE_TIME)
                        else:
                            print("⚠️ 主页导航失败，等待指定时间")
                            await asyncio.sleep(BROWSE_TIME)

                print(f"=== 大循环 {major_cycle + 1}/{MAJOR_CYCLES} 完成 ===")

            print("\n🎉 所有浏览循环完成！")

        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
