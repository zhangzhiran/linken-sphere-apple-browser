#!/usr/bin/env python3
"""
Linken Sphere + Apple Japan Website Browser 集成版
结合 Linken Sphere 指纹保护与 Apple 网站自动化浏览
"""

import asyncio
import json
import logging
import random
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

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
    """Linken Sphere + Apple 网站自动化浏览器"""
    
    def __init__(self, browse_duration=60, major_cycles=3, max_retries=3):
        """
        初始化浏览器配置
        
        Args:
            browse_duration (int): 每个页面的浏览时间（秒）
            major_cycles (int): 大循环次数，每个大循环包含8次页面访问
            max_retries (int): 最大重试次数
        """
        self.browse_duration = browse_duration
        self.major_cycles = major_cycles
        self.minor_cycles_per_major = 8
        self.max_retries = max_retries
        
        # Linken Sphere API 配置
        self.api_host = "127.0.0.1"
        self.api_port = 36555
        self.base_url = f"http://{self.api_host}:{self.api_port}"
        
        # Apple 网站配置
        self.apple_base_url = "https://www.apple.com/jp/"
        
        # 浏览器和会话状态
        self.driver = None
        self.session_data = None
        self.available_links = []
        
        # 统计信息
        self.retry_stats = {
            'total_retries': 0,
            'successful_retries': 0,
            'failed_operations': 0
        }
        
        logger.info("Linken Sphere Apple 浏览器初始化完成")
    
    def get_profiles(self):
        """获取 Linken Sphere 配置文件列表"""
        try:
            response = requests.get(f"{self.base_url}/sessions", timeout=10)
            response.raise_for_status()
            profiles = response.json()
            logger.info(f"获取到 {len(profiles)} 个配置文件")
            return profiles
        except Exception as e:
            logger.error(f"获取配置文件失败: {e}")
            return []
    
    def start_linken_sphere_session(self, profile_uuid, debug_port=9222):
        """启动 Linken Sphere 会话"""
        try:
            payload = json.dumps({
                "uuid": profile_uuid,
                "headless": False,
                "debug_port": debug_port
            }, indent=4)
            
            headers = {'Content-Type': 'application/json'}
            response = requests.post(
                f"{self.base_url}/sessions/start", 
                data=payload, 
                headers=headers, 
                timeout=15
            )
            
            if response.status_code == 200:
                session_data = response.json()
                logger.info(f"✅ Linken Sphere 会话启动成功")
                logger.info(f"   调试端口: {session_data.get('debug_port')}")
                logger.info(f"   配置文件UUID: {session_data.get('uuid')}")
                return session_data
            elif response.status_code == 409:
                logger.warning("⚠️ 会话已在运行，尝试连接现有会话")
                return {"debug_port": debug_port, "uuid": profile_uuid}
            else:
                logger.error(f"启动会话失败: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"启动 Linken Sphere 会话异常: {e}")
            return None
    
    def connect_to_browser(self, debug_port):
        """连接到 Linken Sphere 浏览器"""
        try:
            chrome_options = Options()
            chrome_options.add_experimental_option("debuggerAddress", f"127.0.0.1:{debug_port}")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            
            # 连接到现有的浏览器实例
            self.driver = webdriver.Chrome(options=chrome_options)
            logger.info(f"✅ 成功连接到 Linken Sphere 浏览器 (端口: {debug_port})")
            return True
            
        except Exception as e:
            logger.error(f"连接浏览器失败: {e}")
            return False
    
    def safe_execute(self, operation_name, operation_func, *args, **kwargs):
        """安全执行操作，带重试机制"""
        for attempt in range(self.max_retries):
            try:
                self.retry_stats['total_retries'] += 1
                result = operation_func(*args, **kwargs)
                if attempt > 0:
                    self.retry_stats['successful_retries'] += 1
                    logger.info(f"✅ {operation_name} - 重试成功 (第 {attempt + 1} 次)")
                return result
                
            except Exception as e:
                if attempt < self.max_retries - 1:
                    logger.warning(f"⚠️ {operation_name} - 第 {attempt + 1} 次尝试失败: {e}")
                    time.sleep(2)
                else:
                    logger.error(f"❌ {operation_name} - 所有重试都失败: {e}")
                    self.retry_stats['failed_operations'] += 1
                    return None
    
    def get_apple_links(self):
        """获取 Apple 网站的链接"""
        def _get_links():
            self.driver.get(self.apple_base_url)
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # 获取所有链接
            links = self.driver.find_elements(By.TAG_NAME, "a")
            valid_links = []
            
            for link in links:
                try:
                    href = link.get_attribute("href")
                    text = link.text.strip()
                    
                    if (href and href.startswith("https://www.apple.com/jp/") 
                        and text and len(text) > 0
                        and "search" not in href.lower()):
                        
                        valid_links.append({
                            "url": href,
                            "text": text[:50]  # 限制文本长度
                        })
                except:
                    continue
            
            # 去重
            unique_links = []
            seen_urls = set()
            for link in valid_links:
                if link["url"] not in seen_urls:
                    unique_links.append(link)
                    seen_urls.add(link["url"])
            
            logger.info(f"获取到 {len(unique_links)} 个有效链接")
            return unique_links
        
        links = self.safe_execute("获取Apple链接", _get_links)
        if links:
            self.available_links = links
            return True
        return False
    
    def scroll_to_bottom(self):
        """滚动到页面底部"""
        def _scroll():
            last_height = self.driver.execute_script("return document.body.scrollHeight")
            
            while True:
                # 滚动到底部
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                
                # 计算新的滚动高度
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height
            
            logger.info("页面滚动到底部完成")
            return True
        
        return self.safe_execute("滚动页面", _scroll)
    
    def browse_page(self, url, duration):
        """浏览指定页面"""
        def _browse():
            logger.info(f"开始浏览页面: {url}")
            start_time = time.time()
            
            # 导航到页面
            self.driver.get(url)
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # 滚动到底部
            self.scroll_to_bottom()
            
            # 等待剩余时间
            elapsed = time.time() - start_time
            remaining = max(0, duration - elapsed)
            
            if remaining > 0:
                logger.info(f"在页面底部等待 {remaining:.2f} 秒")
                time.sleep(remaining)
            
            total_duration = time.time() - start_time
            logger.info(f"页面浏览完成，耗时: {total_duration:.2f} 秒")
            return total_duration
        
        return self.safe_execute(f"浏览页面 {url}", _browse)
    
    def run_automation(self):
        """运行完整的自动化流程"""
        try:
            logger.info("🚀 开始 Linken Sphere + Apple 自动化浏览")
            logger.info("=" * 60)
            
            # 1. 获取配置文件
            profiles = self.get_profiles()
            if not profiles:
                logger.error("❌ 无法获取配置文件")
                return False
            
            profile = profiles[0]
            profile_uuid = profile.get('uuid')
            profile_name = profile.get('name')
            
            logger.info(f"使用配置文件: {profile_name} ({profile_uuid})")
            
            # 2. 启动 Linken Sphere 会话
            self.session_data = self.start_linken_sphere_session(profile_uuid)
            if not self.session_data:
                logger.error("❌ 无法启动 Linken Sphere 会话")
                return False
            
            debug_port = self.session_data.get('debug_port', 9222)
            
            # 3. 连接到浏览器
            if not self.connect_to_browser(debug_port):
                logger.error("❌ 无法连接到浏览器")
                return False
            
            # 4. 开始自动化浏览
            total_pages = self.major_cycles * self.minor_cycles_per_major
            logger.info(f"开始浏览流程:")
            logger.info(f"  大循环次数: {self.major_cycles}")
            logger.info(f"  每个大循环: {self.minor_cycles_per_major} 次页面访问")
            logger.info(f"  总页面数: {total_pages}")
            logger.info(f"  每页浏览时长: {self.browse_duration} 秒")
            
            # 外层循环：大循环
            for major_cycle in range(self.major_cycles):
                current_major = major_cycle + 1
                logger.info(f"=== 大循环 {current_major}/{self.major_cycles} 开始 ===")
                
                # 刷新链接列表
                if not self.get_apple_links():
                    logger.error("无法获取链接，跳过此大循环")
                    continue
                
                # 内层循环：8次页面访问
                for minor_cycle in range(self.minor_cycles_per_major):
                    current_minor = minor_cycle + 1
                    page_number = major_cycle * self.minor_cycles_per_major + minor_cycle + 1
                    
                    logger.info(f"--- 大循环 {current_major}, 小循环 {current_minor}/8 (总第 {page_number}/{total_pages} 页) ---")
                    
                    # 随机选择链接
                    if self.available_links:
                        selected_link = random.choice(self.available_links)
                        logger.info(f"随机选择: {selected_link['text']} ({selected_link['url']})")
                        
                        # 浏览页面
                        self.browse_page(selected_link['url'], self.browse_duration)
                    else:
                        logger.warning("没有可用链接，浏览主页")
                        self.browse_page(self.apple_base_url, self.browse_duration)
                
                logger.info(f"=== 大循环 {current_major}/{self.major_cycles} 完成 ===")
            
            logger.info("🎉 所有浏览循环完成！")
            self._print_stats()
            return True
            
        except Exception as e:
            logger.error(f"自动化流程异常: {e}")
            return False
        
        finally:
            if self.driver:
                logger.info("关闭浏览器连接")
                self.driver.quit()
    
    def _print_stats(self):
        """打印统计信息"""
        logger.info("=" * 50)
        logger.info("📊 自动化统计报告")
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

def main():
    """主函数"""
    print("🍎 Linken Sphere + Apple Japan 自动化浏览器")
    print("=" * 60)
    print("功能特点:")
    print("✅ Linken Sphere 指纹保护")
    print("✅ Apple Japan 网站自动化浏览")
    print("✅ 双层循环结构 (3大循环 × 8小循环)")
    print("✅ 智能重试机制")
    print("✅ 详细日志记录")
    print("=" * 60)
    
    # 创建浏览器实例
    browser = LinkenSphereAppleBrowser(
        browse_duration=60,  # 每页60秒
        major_cycles=3,      # 3个大循环
        max_retries=3        # 最大重试3次
    )
    
    # 运行自动化
    success = browser.run_automation()
    
    if success:
        print("\n🎉 自动化浏览完成！")
    else:
        print("\n❌ 自动化浏览失败")
    
    return success

if __name__ == "__main__":
    main()
