#!/usr/bin/env python3
"""
Apple Japan Website Browser
使用 Playwright 自动浏览 Apple 日本官网的脚本
支持 Windows 和 Mac 系统
"""

import asyncio
import random
import time
import platform
from playwright.async_api import async_playwright
import logging
try:
    from blocked_urls import get_blocked_patterns_js, filter_links
except ImportError:
    # 如果导入失败，使用内置的屏蔽逻辑
    def get_blocked_patterns_js():
        return "['search', '/search', '/search/', 'apple.com/jp/search']"

    def filter_links(links):
        blocked_patterns = ['search']
        filtered = []
        for link in links:
            url = link.get('url', '') if isinstance(link, dict) else str(link)
            if not any(pattern in url.lower() for pattern in blocked_patterns):
                filtered.append(link)
        return filtered

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('browser_log.txt', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AppleWebsiteBrowser:
    def __init__(self, browse_duration=60, major_cycles=3, max_retries=3, retry_delay=5):
        """
        初始化浏览器配置

        Args:
            browse_duration (int): 每个页面的浏览时间（秒）
            major_cycles (int): 大循环次数，每个大循环包含8次页面访问
            max_retries (int): 最大重试次数
            retry_delay (int): 重试间隔时间（秒）
        """
        self.browse_duration = browse_duration
        self.major_cycles = major_cycles
        self.minor_cycles_per_major = 8  # 固定值，每个大循环包含8次页面访问
        self.base_url = "https://www.apple.com/jp/"
        self.visited_links = []
        self.available_links = []
        self.current_major_cycle = 0
        self.current_minor_cycle = 0

        # 重试机制配置
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.retry_stats = {
            'total_retries': 0,
            'successful_retries': 0,
            'failed_operations': 0
        }

    async def retry_operation(self, operation_name, operation_func, *args, **kwargs):
        """
        通用重试机制

        Args:
            operation_name (str): 操作名称，用于日志
            operation_func: 要重试的异步函数
            *args, **kwargs: 传递给操作函数的参数

        Returns:
            操作函数的返回值，如果所有重试都失败则返回None
        """
        for attempt in range(self.max_retries + 1):  # +1 因为第一次不算重试
            try:
                if attempt > 0:
                    logger.warning(f"🔄 {operation_name} - 第 {attempt} 次重试")
                    self.retry_stats['total_retries'] += 1
                    await asyncio.sleep(self.retry_delay)

                result = await operation_func(*args, **kwargs)

                if attempt > 0:
                    logger.info(f"✅ {operation_name} - 重试成功")
                    self.retry_stats['successful_retries'] += 1

                return result

            except Exception as e:
                if attempt < self.max_retries:
                    logger.warning(f"⚠️ {operation_name} - 尝试 {attempt + 1} 失败: {e}")
                    logger.info(f"⏳ 等待 {self.retry_delay} 秒后重试...")
                else:
                    logger.error(f"❌ {operation_name} - 所有重试都失败: {e}")
                    self.retry_stats['failed_operations'] += 1
                    return None

    async def safe_goto(self, page, url, timeout=30000):
        """
        安全的页面导航，带重试机制

        Args:
            page: Playwright 页面对象
            url (str): 目标URL
            timeout (int): 超时时间（毫秒）

        Returns:
            bool: 是否成功导航
        """
        async def _goto_operation():
            await page.goto(url, wait_until="domcontentloaded", timeout=timeout)
            await page.wait_for_load_state("networkidle", timeout=10000)
            return True

        result = await self.retry_operation(f"导航到 {url}", _goto_operation)
        return result is not None

    async def safe_evaluate(self, page, script, description="执行脚本"):
        """
        安全的页面脚本执行，带重试机制

        Args:
            page: Playwright 页面对象
            script (str): 要执行的JavaScript代码
            description (str): 操作描述

        Returns:
            脚本执行结果，失败时返回None
        """
        async def _evaluate_operation():
            return await page.evaluate(script)

        return await self.retry_operation(description, _evaluate_operation)

    async def precise_browse_page(self, page, duration):
        """
        精确控制页面浏览时间：滚动阶段 + 等待阶段

        Args:
            page: Playwright 页面对象
            duration (int): 总浏览时间（秒）
        """
        total_start_time = time.time()
        logger.info(f"开始精确浏览页面，总时长: {duration}秒")

        # 阶段1: 滚动到底部
        scroll_start_time = time.time()
        await self._scroll_to_bottom(page)
        scroll_end_time = time.time()
        scroll_duration = scroll_end_time - scroll_start_time

        logger.info(f"滚动阶段完成，耗时: {scroll_duration:.2f}秒")

        # 阶段2: 在底部等待剩余时间
        elapsed_time = time.time() - total_start_time
        remaining_time = max(0, duration - elapsed_time)

        if remaining_time > 0:
            logger.info(f"在页面底部等待剩余时间: {remaining_time:.2f}秒")
            await asyncio.sleep(remaining_time)

        total_duration = time.time() - total_start_time
        logger.info(f"页面浏览完成，实际总耗时: {total_duration:.2f}秒")

        return total_duration

    async def _scroll_to_bottom(self, page):
        """
        向下滚动直到页面底部（带重试机制）

        Args:
            page: Playwright 页面对象

        Returns:
            bool: 是否成功滚动到底部
        """
        logger.info("开始向下滚动到页面底部")

        scroll_position = 0
        scroll_count = 0
        consecutive_failures = 0
        max_consecutive_failures = 3

        while True:
            # 安全获取页面信息
            page_info = await self.safe_evaluate(
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
                logger.warning(f"获取页面信息失败，连续失败次数: {consecutive_failures}")

                if consecutive_failures >= max_consecutive_failures:
                    logger.error("连续获取页面信息失败，停止滚动")
                    return False

                await asyncio.sleep(2)  # 等待后重试
                continue

            # 重置连续失败计数
            consecutive_failures = 0

            # 检查是否已到达底部
            max_scroll = page_info['scrollHeight'] - page_info['clientHeight']
            if scroll_position >= max_scroll:
                logger.info(f"已到达页面底部，总共滚动 {scroll_count} 次")
                break

            # 向下滚动
            scroll_distance = random.randint(100, 250)
            scroll_position = min(scroll_position + scroll_distance, max_scroll)

            # 安全执行滚动
            try:
                await page.evaluate(f"window.scrollTo({{top: {scroll_position}, behavior: 'smooth'}})")
                scroll_count += 1
            except Exception as e:
                logger.warning(f"滚动操作失败: {e}，继续尝试")
                # 即使滚动失败，也要更新位置，避免无限循环
                pass

            # 随机停顿，模拟真实用户行为
            pause_time = random.uniform(0.5, 1.5)
            await asyncio.sleep(pause_time)

            # 偶尔长时间停顿，模拟阅读
            if random.random() < 0.1:  # 10% 概率
                reading_time = random.uniform(1.0, 3.0)
                await asyncio.sleep(reading_time)

        return True

    async def refresh_links(self, page):
        """
        刷新链接列表：返回主页并重新获取所有可用链接（带重试机制）

        Args:
            page: Playwright 页面对象

        Returns:
            bool: 是否成功刷新链接
        """
        logger.info("=== 开始刷新链接列表 ===")

        # 安全返回主页
        homepage_success = await self.safe_goto(page, self.base_url)
        if not homepage_success:
            logger.error("无法返回主页，链接刷新失败")
            return False

        logger.info("已返回主页")

        # 清空访问记录
        self.visited_links.clear()
        logger.info("已清空访问记录")

        # 重新获取链接（带重试）
        async def _get_links_operation():
            return await self.get_navigation_links(page)

        self.available_links = await self.retry_operation("获取导航链接", _get_links_operation)

        if self.available_links is None:
            self.available_links = []
            logger.error("获取链接失败，使用空链接列表")
            return False

        logger.info(f"重新获取到 {len(self.available_links)} 个可用链接")
        return len(self.available_links) > 0

    async def get_navigation_links(self, page):
        """
        获取页面中的导航链接（带重试机制）

        Args:
            page: Playwright 页面对象

        Returns:
            list: 链接列表，失败时返回空列表
        """
        # 获取主导航链接
        links = await self.safe_evaluate(
            page,
            """
            () => {
                const links = [];
                try {
                    // 获取主导航菜单链接
                    const navLinks = document.querySelectorAll('nav a, .globalnav a, .ac-gn-link');
                    navLinks.forEach(link => {
                        if (link.href && link.href.includes('apple.com/jp/') &&
                            !link.href.includes('#') &&
                            link.href !== window.location.href) {
                            links.push({
                                url: link.href,
                                text: link.textContent.trim()
                            });
                        }
                    });

                    // 获取产品页面链接
                    const productLinks = document.querySelectorAll('.tile a, .product-tile a, .hero a');
                    productLinks.forEach(link => {
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
                } catch (error) {
                    console.error('获取链接时出错:', error);
                    return [];
                }
            }
            """,
            "获取页面导航链接"
        )

        if links is None:
            logger.error("获取链接失败")
            return []

        # 去重并过滤屏蔽的链接
        unique_links = []
        seen_urls = set()
        for link in links:
            if link['url'] not in seen_urls:
                unique_links.append(link)
                seen_urls.add(link['url'])

        # 过滤屏蔽的链接
        filtered_links = filter_links(unique_links)

        logger.info(f"找到 {len(unique_links)} 个唯一链接，过滤后剩余 {len(filtered_links)} 个")
        return filtered_links

    async def browse_page(self, page, url, duration):
        """
        精确浏览指定页面（带重试机制）

        Args:
            page: Playwright 页面对象
            url (str): 要浏览的URL
            duration (int): 浏览时间（秒）

        Returns:
            float: 实际浏览时间，失败时返回0
        """
        # 获取当前页面标题（用于日志）
        try:
            current_title = await page.title() if page.url else "未知页面"
        except:
            current_title = "无法获取标题"

        logger.info(f"第 {self.current_minor_cycle}/8 次页面访问")
        logger.info(f"正在访问: {url}")
        logger.info(f"当前页面: {current_title}")

        # 安全导航到页面
        navigation_success = await self.safe_goto(page, url)
        if not navigation_success:
            logger.error(f"无法导航到页面: {url}")
            return 0

        # 安全获取新的页面标题
        page_title = await self.safe_evaluate(
            page,
            "document.title",
            "获取页面标题"
        )

        if page_title:
            logger.info(f"页面加载完成: {page_title}")
        else:
            logger.warning("无法获取页面标题，但继续浏览")

        # 记录访问的链接
        self.visited_links.append(url)

        # 精确控制浏览时间（带重试机制）
        try:
            actual_duration = await self.precise_browse_page(page, duration)
            return actual_duration
        except Exception as e:
            logger.error(f"浏览页面内容时出错: {e}")
            # 即使浏览失败，也要等待指定时间，保持时间一致性
            logger.info(f"浏览失败，但仍等待 {duration} 秒保持时间一致性")
            await asyncio.sleep(duration)
            return duration

    async def run(self):
        """
        运行双层循环浏览流程
        """
        total_pages = self.major_cycles * self.minor_cycles_per_major

        logger.info("开始启动浏览器...")
        logger.info(f"系统: {platform.system()}")
        logger.info(f"浏览时长: {self.browse_duration}秒/页面")
        logger.info(f"大循环次数: {self.major_cycles}")
        logger.info(f"每个大循环包含: {self.minor_cycles_per_major} 次页面访问")
        logger.info(f"总页面访问次数: {total_pages}")

        async with async_playwright() as p:
            # 根据系统选择浏览器
            if platform.system() == "Darwin":  # Mac
                browser = await p.webkit.launch(headless=False)
            else:  # Windows 和其他系统
                browser = await p.chromium.launch(headless=False)

            context = await browser.new_context(
                viewport={"width": 1920, "height": 1080},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            )

            page = await context.new_page()

            try:
                # 外层循环：大循环
                for major_cycle in range(self.major_cycles):
                    self.current_major_cycle = major_cycle + 1
                    logger.info(f"=== 大循环 {self.current_major_cycle}/{self.major_cycles} 开始 ===")

                    # 刷新链接列表
                    links_available = await self.refresh_links(page)
                    if not links_available:
                        logger.error("无法获取可用链接，跳过此大循环")
                        continue

                    # 内层循环：8次页面访问
                    for minor_cycle in range(self.minor_cycles_per_major):
                        self.current_minor_cycle = minor_cycle + 1
                        page_number = major_cycle * self.minor_cycles_per_major + minor_cycle + 1

                        logger.info(f"--- 大循环 {self.current_major_cycle}, 小循环 {self.current_minor_cycle}/8 (总第 {page_number}/{total_pages} 页) ---")

                        # 随机选择链接
                        if self.available_links:
                            selected_link = random.choice(self.available_links)
                            logger.info(f"随机选择链接: {selected_link['text']} ({selected_link['url']})")

                            # 浏览页面
                            actual_duration = await self.browse_page(
                                page, selected_link['url'], self.browse_duration
                            )

                            logger.info(f"页面浏览完成，实际耗时: {actual_duration:.2f}秒")
                        else:
                            logger.warning("没有可用链接，浏览主页")
                            await self.browse_page(page, self.base_url, self.browse_duration)

                    logger.info(f"=== 大循环 {self.current_major_cycle}/{self.major_cycles} 完成 ===")

                logger.info("🎉 所有浏览循环完成！")

                # 输出重试统计信息
                logger.info("=" * 50)
                logger.info("📊 重试机制统计报告")
                logger.info("=" * 50)
                logger.info(f"总重试次数: {self.retry_stats['total_retries']}")
                logger.info(f"成功重试次数: {self.retry_stats['successful_retries']}")
                logger.info(f"失败操作次数: {self.retry_stats['failed_operations']}")

                if self.retry_stats['total_retries'] > 0:
                    success_rate = (self.retry_stats['successful_retries'] / self.retry_stats['total_retries']) * 100
                    logger.info(f"重试成功率: {success_rate:.1f}%")
                else:
                    logger.info("重试成功率: 100% (无需重试)")

                logger.info("=" * 50)

            except Exception as e:
                logger.error(f"浏览过程中出错: {e}")
                logger.info("程序异常结束，输出重试统计:")
                logger.info(f"总重试次数: {self.retry_stats['total_retries']}")
                logger.info(f"失败操作次数: {self.retry_stats['failed_operations']}")

            finally:
                await browser.close()

def main():
    """
    主函数
    """
    print("Apple Japan Website Browser - 双层循环版本 (带重试机制)")
    print("=" * 70)
    print("功能说明：")
    print("- 大循环：每个大循环包含8次页面访问")
    print("- 小循环：每次页面访问包含滚动+等待阶段")
    print("- 总访问次数 = 大循环次数 × 8")
    print("- 重试机制：自动处理网络问题和页面加载失败")
    print("=" * 70)

    # 用户可以自定义配置
    try:
        duration = int(input("请输入每页浏览时间（秒，默认60）: ") or "60")
        major_cycles = int(input("请输入大循环次数（默认3，每个大循环8次页面访问）: ") or "3")

        # 高级配置选项
        advanced = input("是否配置高级选项？(y/N): ").lower() == 'y'
        if advanced:
            max_retries = int(input("请输入最大重试次数（默认3）: ") or "3")
            retry_delay = int(input("请输入重试间隔时间（秒，默认5）: ") or "5")
        else:
            max_retries = 3
            retry_delay = 5

        total_pages = major_cycles * 8
        estimated_time = total_pages * duration / 60  # 分钟

        print(f"\n配置确认：")
        print(f"- 每页浏览时间: {duration}秒")
        print(f"- 大循环次数: {major_cycles}")
        print(f"- 总页面访问次数: {total_pages}")
        print(f"- 预计总耗时: {estimated_time:.1f}分钟")
        print(f"- 最大重试次数: {max_retries}")
        print(f"- 重试间隔: {retry_delay}秒")

        confirm = input("\n确认开始浏览？(y/N): ").lower()
        if confirm != 'y':
            print("已取消")
            return

    except ValueError:
        duration = 60
        major_cycles = 3
        max_retries = 3
        retry_delay = 5
        print("使用默认配置: 60秒/页面, 3个大循环, 3次重试")

    browser = AppleWebsiteBrowser(
        browse_duration=duration,
        major_cycles=major_cycles,
        max_retries=max_retries,
        retry_delay=retry_delay
    )
    
    try:
        asyncio.run(browser.run())
    except KeyboardInterrupt:
        print("\n用户中断了浏览过程")
    except Exception as e:
        print(f"程序运行出错: {e}")

if __name__ == "__main__":
    main()
