#!/usr/bin/env python3
"""
Linken Sphere 手动集成模式
当 API 不可用时的替代方案
"""

import time
import random
import platform
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, WebDriverException
from typing import List, Dict, Optional

try:
    from blocked_urls import filter_links
except ImportError:
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
        logging.FileHandler('linken_sphere_manual_log.txt', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class LinkenSphereManualBrowser:
    """
    Linken Sphere 手动集成浏览器
    当 API 不可用时，通过手动配置的 Chrome 端口连接
    """
    
    def __init__(self, browse_duration=60, major_cycles=3, max_retries=3, retry_delay=5,
                 chrome_debug_port=9222):
        """
        初始化浏览器配置
        
        Args:
            browse_duration (int): 每个页面的浏览时间（秒）
            major_cycles (int): 大循环次数
            max_retries (int): 最大重试次数
            retry_delay (int): 重试间隔时间（秒）
            chrome_debug_port (int): Chrome 调试端口
        """
        self.browse_duration = browse_duration
        self.major_cycles = major_cycles
        self.minor_cycles_per_major = 8
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
        
        # Chrome 调试端口
        self.chrome_debug_port = chrome_debug_port
        self.driver = None
    
    def print_manual_setup_instructions(self):
        """打印手动设置说明"""
        print("🔧 Linken Sphere 手动集成模式")
        print("=" * 60)
        print("由于 API 不可用，请按照以下步骤手动设置：")
        print()
        print("步骤 1: 在 Linken Sphere 中创建配置文件")
        print("  - 打开 Linken Sphere 应用程序")
        print("  - 创建新的浏览器配置文件")
        print("  - 设置适合的指纹参数（时区：Asia/Tokyo，语言：日语）")
        print()
        print("步骤 2: 启动浏览器并启用调试模式")
        print("  - 在 Linken Sphere 中启动您创建的配置文件")
        print("  - 确保浏览器以调试模式运行")
        print(f"  - 调试端口应该是：{self.chrome_debug_port}")
        print()
        print("步骤 3: 确认浏览器已启动")
        print("  - 浏览器窗口应该已经打开")
        print("  - 可以手动访问任何网站测试")
        print()
        print("完成上述步骤后，本程序将连接到您的 Linken Sphere 浏览器")
        print("=" * 60)
    
    def wait_for_user_confirmation(self) -> bool:
        """等待用户确认设置完成"""
        print("\n⏳ 请完成上述手动设置步骤")
        
        while True:
            try:
                response = input("\n是否已完成设置并启动了 Linken Sphere 浏览器？(y/n/help): ").lower().strip()
                
                if response == 'y' or response == 'yes':
                    return True
                elif response == 'n' or response == 'no':
                    print("❌ 请先完成设置后再继续")
                    return False
                elif response == 'help':
                    self.print_manual_setup_instructions()
                else:
                    print("请输入 y (是) 或 n (否) 或 help (帮助)")
                    
            except KeyboardInterrupt:
                print("\n❌ 用户取消操作")
                return False
    
    def connect_to_linken_sphere_browser(self) -> bool:
        """连接到 Linken Sphere 浏览器"""
        try:
            logger.info(f"正在连接到 Linken Sphere 浏览器 (端口: {self.chrome_debug_port})")
            
            chrome_options = Options()
            chrome_options.add_experimental_option("debuggerAddress", f"127.0.0.1:{self.chrome_debug_port}")
            
            # 尝试连接
            self.driver = webdriver.Chrome(options=chrome_options)
            
            # 测试连接
            current_url = self.driver.current_url
            logger.info(f"✅ 成功连接到 Linken Sphere 浏览器")
            logger.info(f"当前页面: {current_url}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ 连接失败: {e}")
            logger.info("可能的原因：")
            logger.info("1. Linken Sphere 浏览器未启动")
            logger.info("2. 调试端口不正确")
            logger.info("3. 浏览器未以调试模式运行")
            return False
    
    def initialize_browser(self) -> bool:
        """初始化浏览器连接"""
        # 显示手动设置说明
        self.print_manual_setup_instructions()
        
        # 等待用户确认
        if not self.wait_for_user_confirmation():
            return False
        
        # 尝试连接
        max_attempts = 3
        for attempt in range(max_attempts):
            if attempt > 0:
                print(f"\n🔄 重试连接 (第 {attempt + 1} 次)")
                
                # 询问是否更改端口
                try:
                    change_port = input(f"是否尝试不同的端口？当前端口：{self.chrome_debug_port} (y/n): ").lower()
                    if change_port == 'y':
                        new_port = input("请输入新的端口号 (默认 9222): ").strip()
                        if new_port.isdigit():
                            self.chrome_debug_port = int(new_port)
                except KeyboardInterrupt:
                    return False
            
            if self.connect_to_linken_sphere_browser():
                return True
            
            if attempt < max_attempts - 1:
                print("⏳ 请检查 Linken Sphere 设置，然后按回车继续...")
                try:
                    input()
                except KeyboardInterrupt:
                    return False
        
        logger.error("❌ 无法连接到 Linken Sphere 浏览器")
        return False
    
    def retry_operation(self, operation_name, operation_func, *args, **kwargs):
        """通用重试机制"""
        for attempt in range(self.max_retries + 1):
            try:
                if attempt > 0:
                    logger.warning(f"🔄 {operation_name} - 第 {attempt} 次重试")
                    self.retry_stats['total_retries'] += 1
                    time.sleep(self.retry_delay)
                
                result = operation_func(*args, **kwargs)
                
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
    
    def safe_goto(self, url: str, timeout: int = 30) -> bool:
        """安全的页面导航"""
        def _goto_operation():
            self.driver.get(url)
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            return True
        
        result = self.retry_operation(f"导航到 {url}", _goto_operation)
        return result is not None
    
    def scroll_to_bottom(self) -> bool:
        """向下滚动到页面底部"""
        logger.info("开始向下滚动到页面底部")
        
        try:
            last_height = self.driver.execute_script("return document.body.scrollHeight")
            scroll_count = 0
            
            while True:
                # 随机滚动距离
                scroll_distance = random.randint(100, 300)
                self.driver.execute_script(f"window.scrollBy(0, {scroll_distance});")
                scroll_count += 1
                
                # 随机停顿
                pause_time = random.uniform(0.5, 1.5)
                time.sleep(pause_time)
                
                # 检查是否到达底部
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                current_position = self.driver.execute_script("return window.pageYOffset + window.innerHeight")
                
                if current_position >= new_height * 0.95:  # 到达95%位置认为是底部
                    logger.info(f"已到达页面底部，总共滚动 {scroll_count} 次")
                    break
                
                # 偶尔长时间停顿，模拟阅读
                if random.random() < 0.1:
                    reading_time = random.uniform(1.0, 3.0)
                    time.sleep(reading_time)
                
                last_height = new_height
            
            return True
            
        except Exception as e:
            logger.error(f"滚动操作失败: {e}")
            return False
    
    def precise_browse_page(self, duration: int) -> float:
        """精确控制页面浏览时间"""
        total_start_time = time.time()
        logger.info(f"开始精确浏览页面，总时长: {duration}秒")
        
        # 阶段1: 滚动到底部
        scroll_start_time = time.time()
        self.scroll_to_bottom()
        scroll_end_time = time.time()
        scroll_duration = scroll_end_time - scroll_start_time
        
        logger.info(f"滚动阶段完成，耗时: {scroll_duration:.2f}秒")
        
        # 阶段2: 在底部等待剩余时间
        elapsed_time = time.time() - total_start_time
        remaining_time = max(0, duration - elapsed_time)
        
        if remaining_time > 0:
            logger.info(f"在页面底部等待剩余时间: {remaining_time:.2f}秒")
            time.sleep(remaining_time)
        
        total_duration = time.time() - total_start_time
        logger.info(f"页面浏览完成，实际总耗时: {total_duration:.2f}秒")
        
        return total_duration
    
    def get_navigation_links(self) -> List[Dict]:
        """获取页面中的导航链接"""
        try:
            # 等待页面加载完成
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "a"))
            )
            
            # 获取所有链接
            link_elements = self.driver.find_elements(By.CSS_SELECTOR, 
                "nav a, .globalnav a, .ac-gn-link, .tile a, .product-tile a, .hero a")
            
            links = []
            for element in link_elements:
                try:
                    href = element.get_attribute('href')
                    text = element.text.strip()
                    
                    if (href and 'apple.com/jp/' in href and 
                        '#' not in href and href != self.driver.current_url):
                        links.append({
                            'url': href,
                            'text': text or 'No Text'
                        })
                except Exception:
                    continue
            
            # 去重
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
            
        except Exception as e:
            logger.error(f"获取链接失败: {e}")
            return []
    
    def refresh_links(self) -> bool:
        """刷新链接列表"""
        logger.info("=== 开始刷新链接列表 ===")
        
        # 返回主页
        if not self.safe_goto(self.base_url):
            logger.error("无法返回主页，链接刷新失败")
            return False
        
        logger.info("已返回主页")
        
        # 清空访问记录
        self.visited_links.clear()
        logger.info("已清空访问记录")
        
        # 重新获取链接
        self.available_links = self.get_navigation_links()
        
        if not self.available_links:
            logger.error("获取链接失败")
            return False
        
        logger.info(f"重新获取到 {len(self.available_links)} 个可用链接")
        return True
    
    def browse_page(self, url: str, duration: int) -> float:
        """浏览指定页面"""
        try:
            current_title = self.driver.title if self.driver else "未知页面"
        except:
            current_title = "无法获取标题"
        
        logger.info(f"第 {self.current_minor_cycle}/8 次页面访问")
        logger.info(f"正在访问: {url}")
        logger.info(f"当前页面: {current_title}")
        
        # 导航到页面
        if not self.safe_goto(url):
            logger.error(f"无法导航到页面: {url}")
            return 0
        
        # 获取新的页面标题
        try:
            page_title = self.driver.title
            logger.info(f"页面加载完成: {page_title}")
        except:
            logger.warning("无法获取页面标题，但继续浏览")
        
        # 记录访问的链接
        self.visited_links.append(url)
        
        # 精确控制浏览时间
        try:
            actual_duration = self.precise_browse_page(duration)
            return actual_duration
        except Exception as e:
            logger.error(f"浏览页面内容时出错: {e}")
            # 即使浏览失败，也要等待指定时间
            logger.info(f"浏览失败，但仍等待 {duration} 秒保持时间一致性")
            time.sleep(duration)
            return duration
    
    def run(self):
        """运行双层循环浏览流程"""
        total_pages = self.major_cycles * self.minor_cycles_per_major
        
        logger.info("开始启动 Linken Sphere 手动集成浏览器...")
        logger.info(f"系统: {platform.system()}")
        logger.info(f"浏览时长: {self.browse_duration}秒/页面")
        logger.info(f"大循环次数: {self.major_cycles}")
        logger.info(f"每个大循环包含: {self.minor_cycles_per_major} 次页面访问")
        logger.info(f"总页面访问次数: {total_pages}")
        
        try:
            # 初始化浏览器连接
            if not self.initialize_browser():
                logger.error("浏览器初始化失败")
                return
            
            # 外层循环：大循环
            for major_cycle in range(self.major_cycles):
                self.current_major_cycle = major_cycle + 1
                logger.info(f"=== 大循环 {self.current_major_cycle}/{self.major_cycles} 开始 ===")
                
                # 刷新链接列表
                if not self.refresh_links():
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
                        actual_duration = self.browse_page(
                            selected_link['url'], self.browse_duration
                        )
                        
                        logger.info(f"页面浏览完成，实际耗时: {actual_duration:.2f}秒")
                    else:
                        logger.warning("没有可用链接，浏览主页")
                        self.browse_page(self.base_url, self.browse_duration)
                
                logger.info(f"=== 大循环 {self.current_major_cycle}/{self.major_cycles} 完成 ===")
            
            logger.info("🎉 所有浏览循环完成！")
            
            # 输出重试统计信息
            self._print_retry_stats()
            
        except Exception as e:
            logger.error(f"浏览过程中出错: {e}")
            logger.info("程序异常结束，输出重试统计:")
            logger.info(f"总重试次数: {self.retry_stats['total_retries']}")
            logger.info(f"失败操作次数: {self.retry_stats['failed_operations']}")
        
        finally:
            self.cleanup()
    
    def _print_retry_stats(self):
        """打印重试统计信息"""
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
    
    def cleanup(self):
        """清理资源"""
        try:
            if self.driver:
                # 注意：不要关闭 Linken Sphere 浏览器，只是断开连接
                logger.info("断开与 Linken Sphere 浏览器的连接")
                self.driver.quit()
        except Exception as e:
            logger.error(f"清理资源时出错: {e}")


def main():
    """主函数"""
    print("Linken Sphere 手动集成模式")
    print("=" * 70)
    print("当 API 不可用时的替代方案")
    print("=" * 70)
    
    # 用户配置
    try:
        duration = int(input("请输入每页浏览时间（秒，默认60）: ") or "60")
        major_cycles = int(input("请输入大循环次数（默认3，每个大循环8次页面访问）: ") or "3")
        
        # Chrome 调试端口配置
        debug_port_input = input("请输入 Chrome 调试端口（默认9222）: ").strip()
        debug_port = int(debug_port_input) if debug_port_input.isdigit() else 9222
        
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
        print(f"- Chrome 调试端口: {debug_port}")
        print(f"- 最大重试次数: {max_retries}")
        print(f"- 重试间隔: {retry_delay}秒")
        
        confirm = input("\n确认开始浏览？(y/N): ").lower()
        if confirm != 'y':
            print("已取消")
            return
        
    except ValueError:
        duration = 60
        major_cycles = 3
        debug_port = 9222
        max_retries = 3
        retry_delay = 5
        print("使用默认配置: 60秒/页面, 3个大循环, 端口9222, 3次重试")
    
    browser = LinkenSphereManualBrowser(
        browse_duration=duration,
        major_cycles=major_cycles,
        max_retries=max_retries,
        retry_delay=retry_delay,
        chrome_debug_port=debug_port
    )
    
    try:
        browser.run()
    except KeyboardInterrupt:
        print("\n用户中断了浏览过程")
        browser.cleanup()
    except Exception as e:
        print(f"程序运行出错: {e}")
        browser.cleanup()


if __name__ == "__main__":
    main()
