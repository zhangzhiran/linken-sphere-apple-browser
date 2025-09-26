#!/usr/bin/env python3
"""
Linken Sphere + Apple Japan Website Browser
使用 Linken Sphere 指纹保护 + Playwright 自动浏览 Apple 日本官网的脚本
完全复制 apple_website_browser.py 的浏览逻辑
"""

import asyncio
import json
import logging
import random
import time
import requests
from playwright.async_api import async_playwright

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
        logging.FileHandler('linken_sphere_browser_log.txt', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class LinkenSphereAppleBrowser:
    """Linken Sphere + Apple Website Browser - 完全复制原始浏览逻辑"""

    def __init__(self, browse_duration=60, major_cycles=3, max_retries=3, retry_delay=5, profile_uuid=None):
        """
        初始化浏览器配置 - 与原始文件完全一致

        Args:
            browse_duration (int): 每个页面的浏览时间（秒）
            major_cycles (int): 大循环次数，每个大循环包含8次页面访问
            max_retries (int): 最大重试次数
            retry_delay (int): 重试间隔时间（秒）
            profile_uuid (str): 指定的 Linken Sphere 配置文件 UUID
        """
        self.browse_duration = browse_duration
        self.major_cycles = major_cycles
        self.minor_cycles_per_major = 8
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.profile_uuid = profile_uuid  # 指定的配置文件UUID

        # Linken Sphere API 配置
        self.api_host = "127.0.0.1"
        self.api_port = 36555
        self.linken_api_url = f"http://{self.api_host}:{self.api_port}"

        # Apple 网站配置 - 与原始文件一致
        self.base_url = "https://www.apple.com/jp/"

        # 浏览器状态
        self.session_data = None
        self.available_links = []
        self.visited_links = set()
        self.current_major_cycle = 0
        self.current_minor_cycle = 0

        # 统计信息 - 与原始文件一致
        self.retry_stats = {
            'total_retries': 0,
            'successful_retries': 0,
            'failed_operations': 0
        }

        # GUI 控制信号 (可选)
        self.stop_event = None
        self.pause_event = None
        self.thread_info = None
        self.gui_log_callback = None
        self.gui_update_callback = None

        logger.info("Linken Sphere Apple 浏览器初始化完成")
    
    def get_linken_sphere_profiles(self):
        """获取 Linken Sphere 配置文件列表"""
        try:
            response = requests.get(f"{self.linken_api_url}/sessions", timeout=10)
            response.raise_for_status()
            profiles = response.json()
            logger.info(f"获取到 {len(profiles)} 个 Linken Sphere 配置文件")
            return profiles
        except Exception as e:
            logger.error(f"获取 Linken Sphere 配置文件失败: {e}")
            return []

    def start_linken_sphere_session(self, profile_uuid, debug_port=12345):
        """启动 Linken Sphere 会话 - 使用发现的可用端口 10002"""
        try:
            payload = json.dumps({
                "uuid": profile_uuid,
                "headless": False,
                "debug_port": debug_port
            }, indent=4)

            headers = {'Content-Type': 'application/json'}
            response = requests.post(
                f"{self.linken_api_url}/sessions/start",
                data=payload,
                headers=headers,
                timeout=15
            )

            if response.status_code == 200:
                session_data = response.json()
                logger.info(f"✅ Linken Sphere 会话启动成功")
                logger.info(f"   调试端口: {session_data.get('debug_port')}")
                return session_data
            elif response.status_code == 409:
                logger.warning("⚠️ 会话已在运行，尝试连接现有会话")
                # 检查端口 10002 是否可用
                if self.check_debug_port_available(debug_port):
                    logger.info(f"✅ 发现端口 {debug_port} 可用，使用现有会话")
                    return {"debug_port": debug_port, "uuid": profile_uuid}
                else:
                    logger.error(f"端口 {debug_port} 不可用")
                    return None
            else:
                logger.error(f"启动会话失败: {response.status_code} - {response.text}")
                return None

        except Exception as e:
            logger.error(f"启动 Linken Sphere 会话异常: {e}")
            return None

    def check_debug_port_available(self, port):
        """检查调试端口是否可用"""
        try:
            response = requests.get(f"http://127.0.0.1:{port}/json", timeout=5)
            if response.status_code == 200:
                data = response.json()
                logger.info(f"端口 {port} 可用，找到 {len(data)} 个标签页")
                return True
            return False
        except:
            return False
    
    async def connect_to_linken_sphere_browser(self, debug_port):
        """连接到 Linken Sphere 浏览器 - 仅尝试连接，不使用备用方案"""
        try:
            playwright = await async_playwright().start()

            # 只尝试连接到 Linken Sphere 调试端口
            browser = await playwright.chromium.connect_over_cdp(f"http://127.0.0.1:{debug_port}")
            logger.info(f"✅ 成功连接到 Linken Sphere 浏览器 (端口: {debug_port})")
            return playwright, browser

        except Exception as e:
            logger.error(f"❌ 无法连接到 Linken Sphere 浏览器 (端口: {debug_port}): {e}")
            logger.error("请检查以下设置:")
            logger.error("1. 确保 Linken Sphere 正在运行")
            logger.error("2. 确保浏览器会话已启动")
            logger.error("3. 确保远程调试端口已启用")
            logger.error("4. 检查 Linken Sphere 中的 API 和调试设置")
            return None, None
    
    async def retry_operation(self, operation_name, operation_func, *args, **kwargs):
        """
        重试机制 - 与原始文件完全一致

        Args:
            operation_name (str): 操作名称
            operation_func: 要执行的异步函数
            *args, **kwargs: 传递给函数的参数

        Returns:
            操作结果，失败时返回None
        """
        for attempt in range(self.max_retries):
            try:
                self.retry_stats['total_retries'] += 1
                result = await operation_func(*args, **kwargs)
                if attempt > 0:
                    self.retry_stats['successful_retries'] += 1
                    logger.info(f"✅ {operation_name} - 重试成功 (第 {attempt + 1} 次)")
                return result

            except Exception as e:
                if attempt < self.max_retries - 1:
                    logger.warning(f"⚠️ {operation_name} - 第 {attempt + 1} 次尝试失败: {e}")
                    logger.info(f"⏳ 等待 {self.retry_delay} 秒后重试...")
                    await asyncio.sleep(self.retry_delay)
                else:
                    logger.error(f"❌ {operation_name} - 所有重试都失败: {e}")
                    self.retry_stats['failed_operations'] += 1
                    return None

    async def safe_goto(self, page, url, timeout=30000):
        """
        安全的页面导航，带重试机制 - 与原始文件完全一致

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
        安全的页面脚本执行，带重试机制 - 与原始文件完全一致

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
        向下滚动直到页面底部（带重试机制）- 与原始文件完全一致

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
        刷新链接列表：返回主页并重新获取所有可用链接（带重试机制）- 与原始文件完全一致

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
        获取页面中的导航链接（带重试机制）- 与原始文件完全一致

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

        # 使用屏蔽URL过滤器
        filtered_links = filter_links(unique_links)

        logger.info(f"找到 {len(unique_links)} 个唯一链接，过滤后剩余 {len(filtered_links)} 个")
        return filtered_links
    
    async def browse_page(self, page, url, duration):
        """
        精确浏览指定页面（带重试机制）- 与原始文件完全一致

        Args:
            page: Playwright 页面对象
            url (str): 目标URL
            duration (int): 浏览时间（秒）

        Returns:
            float: 实际浏览时间，失败时返回duration
        """
        logger.info(f"准备浏览页面: {url}")

        # 安全导航到页面
        navigation_success = await self.safe_goto(page, url)
        if not navigation_success:
            logger.error(f"导航到页面失败: {url}")
            # 即使导航失败，也要等待指定时间，保持时间一致性
            logger.info(f"导航失败，但仍等待 {duration} 秒保持时间一致性")
            await asyncio.sleep(duration)
            return duration

        logger.info(f"成功导航到页面: {url}")

        # 精确浏览页面
        try:
            actual_duration = await self.precise_browse_page(page, duration)
            return actual_duration
        except Exception as e:
            logger.error(f"浏览页面时出错: {e}")
            # 即使浏览失败，也要等待指定时间，保持时间一致性
            logger.info(f"浏览失败，但仍等待 {duration} 秒保持时间一致性")
            await asyncio.sleep(duration)
            return duration
    
    async def run(self):
        """
        运行双层循环浏览流程 - 与原始文件完全一致
        """
        total_pages = self.major_cycles * self.minor_cycles_per_major

        logger.info("开始启动浏览器...")
        logger.info(f"浏览时长: {self.browse_duration}秒/页面")
        logger.info(f"大循环次数: {self.major_cycles}")
        logger.info(f"每个大循环包含: {self.minor_cycles_per_major} 次页面访问")
        logger.info(f"总页面访问次数: {total_pages}")

        # 1. 获取 Linken Sphere 配置文件
        profiles = self.get_linken_sphere_profiles()
        if not profiles:
            logger.error("❌ 无法获取 Linken Sphere 配置文件")
            return False

        # 选择配置文件：如果指定了profile_uuid则使用指定的，否则使用第一个
        if self.profile_uuid:
            # 查找指定的配置文件
            profile = None
            for p in profiles:
                if p.get('uuid') == self.profile_uuid:
                    profile = p
                    break

            if not profile:
                logger.error(f"❌ 找不到指定的配置文件: {self.profile_uuid}")
                logger.info("可用的配置文件:")
                for p in profiles:
                    logger.info(f"  - {p.get('name')} ({p.get('uuid')})")
                return False
        else:
            # 使用第一个可用的配置文件
            profile = profiles[0]

        profile_uuid = profile.get('uuid')
        profile_name = profile.get('name')

        logger.info(f"使用 Linken Sphere 配置文件: {profile_name} ({profile_uuid})")

        # 2. 启动 Linken Sphere 会话
        self.session_data = self.start_linken_sphere_session(profile_uuid)
        if not self.session_data:
            logger.error("❌ 无法启动 Linken Sphere 会话")
            logger.error("请检查 Linken Sphere 是否正在运行并且 API 可用")
            return False

        debug_port = self.session_data.get('debug_port', 12345)

        # 3. 连接到 Linken Sphere 浏览器
        playwright, browser = await self.connect_to_linken_sphere_browser(debug_port)
        if not browser:
            logger.error("❌ 无法连接到 Linken Sphere 浏览器")
            logger.error("程序退出。请确保:")
            logger.error("1. Linken Sphere 正在运行")
            logger.error("2. 浏览器会话已启动")
            logger.error("3. 远程调试端口已启用")
            return False

        try:
            # 获取或创建页面 - 与原始文件的 context 创建方式一致
            contexts = browser.contexts
            if contexts:
                context = contexts[0]
                pages = context.pages
                if pages:
                    page = pages[0]
                else:
                    page = await context.new_page()
            else:
                context = await browser.new_context(
                    viewport={"width": 1920, "height": 1080},
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                )
                page = await context.new_page()

            # 外层循环：大循环 - 与原始文件完全一致
            for major_cycle in range(self.major_cycles):
                # 检查停止信号
                if self.stop_event and self.stop_event.is_set():
                    logger.info("收到停止信号，退出浏览循环")
                    if self.gui_log_callback:
                        self.gui_log_callback("🛑 收到停止信号，正在退出...")
                    break

                self.current_major_cycle = major_cycle + 1
                logger.info(f"=== 大循环 {self.current_major_cycle}/{self.major_cycles} 开始 ===")

                # 刷新链接列表
                links_available = await self.refresh_links(page)
                if not links_available:
                    logger.error("无法获取可用链接，跳过此大循环")
                    continue

                # 内层循环：8次页面访问
                for minor_cycle in range(self.minor_cycles_per_major):
                    # 检查停止信号
                    if self.stop_event and self.stop_event.is_set():
                        logger.info("收到停止信号，退出浏览循环")
                        if self.gui_log_callback:
                            self.gui_log_callback("🛑 收到停止信号，正在退出...")
                        break

                    # 检查暂停信号
                    if self.pause_event and not self.pause_event.is_set():
                        if self.thread_info:
                            self.thread_info['status'] = 'paused'
                        if self.gui_log_callback:
                            self.gui_log_callback("⏸️ 已暂停，等待恢复信号...")
                        if self.gui_update_callback:
                            self.gui_update_callback()

                        # 等待恢复信号
                        while self.pause_event and not self.pause_event.is_set():
                            if self.stop_event and self.stop_event.is_set():
                                logger.info("在暂停中收到停止信号")
                                if self.gui_log_callback:
                                    self.gui_log_callback("🛑 在暂停中收到停止信号")
                                return True
                            await asyncio.sleep(0.5)

                        if self.thread_info:
                            self.thread_info['status'] = 'running'
                        if self.gui_log_callback:
                            self.gui_log_callback("▶️ 已恢复运行")
                        if self.gui_update_callback:
                            self.gui_update_callback()

                    self.current_minor_cycle = minor_cycle + 1
                    page_number = major_cycle * self.minor_cycles_per_major + minor_cycle + 1

                    logger.info(f"--- 大循环 {self.current_major_cycle}, 小循环 {self.current_minor_cycle}/8 (总第 {page_number}/{total_pages} 页) ---")
                    if self.gui_log_callback:
                        self.gui_log_callback(f"📄 正在浏览第 {page_number}/{total_pages} 页")

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

                # 如果收到停止信号，跳出外层循环
                if self.stop_event and self.stop_event.is_set():
                    break

                logger.info(f"=== 大循环 {self.current_major_cycle}/{self.major_cycles} 完成 ===")

            logger.info("🎉 所有浏览循环完成！")

            # 输出重试统计信息 - 与原始文件完全一致
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
            return True

        except Exception as e:
            logger.error(f"浏览过程中出错: {e}")
            logger.info("程序异常结束，输出重试统计:")
            logger.info(f"总重试次数: {self.retry_stats['total_retries']}")
            logger.info(f"失败操作次数: {self.retry_stats['failed_operations']}")
            return False

        finally:
            if browser:
                await browser.close()
            if playwright:
                await playwright.stop()
    
async def main():
    """主函数"""
    print("🍎 Linken Sphere + Apple Japan 自动化浏览器")
    print("=" * 60)
    print("功能特点:")
    print("✅ Linken Sphere 指纹保护")
    print("✅ 完全复制原始浏览逻辑")
    print("✅ Apple Japan 网站自动化浏览")
    print("✅ 双层循环结构 (3大循环 × 8小循环)")
    print("✅ 智能重试机制")
    print("✅ 详细日志记录")
    print("=" * 60)

    # 创建浏览器实例
    browser = LinkenSphereAppleBrowser(
        browse_duration=60,  # 每页60秒
        major_cycles=3,      # 3个大循环
        max_retries=3,       # 最大重试3次
        retry_delay=5        # 重试间隔5秒
    )

    # 运行自动化
    success = await browser.run()

    if success:
        print("\n🎉 自动化浏览完成！")
    else:
        print("\n❌ 自动化浏览失败")
        print("请检查 Linken Sphere 设置和连接")

    return success

if __name__ == "__main__":
    asyncio.run(main())
