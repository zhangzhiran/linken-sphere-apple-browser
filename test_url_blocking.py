#!/usr/bin/env python3
"""
URL屏蔽功能测试脚本
验证搜索页面和其他不需要的页面是否被正确屏蔽
"""

import asyncio
from playwright.async_api import async_playwright
from blocked_urls import is_url_blocked, filter_links

async def test_url_blocking():
    """测试URL屏蔽功能"""
    print("🧪 URL屏蔽功能测试")
    print("=" * 50)
    
    # 测试URL列表
    test_urls = [
        "https://www.apple.com/jp/",
        "https://www.apple.com/jp/search",
        "https://www.apple.com/jp/search/",
        "https://www.apple.com/jp/search?q=iphone",
        "https://www.apple.com/jp/iphone/",
        "https://www.apple.com/jp/mac/",
        "https://www.apple.com/jp/ipad/",
        "https://www.apple.com/jp/watch/",
        "https://www.apple.com/jp/airpods/",
        "https://www.apple.com/jp/tv/",
    ]
    
    print("1. 静态URL屏蔽测试:")
    print("-" * 30)
    
    for url in test_urls:
        blocked = is_url_blocked(url)
        status = "🚫 屏蔽" if blocked else "✅ 允许"
        print(f"{status}: {url}")
    
    print("\n2. 链接过滤测试:")
    print("-" * 30)
    
    # 模拟链接列表
    mock_links = [
        {"url": "https://www.apple.com/jp/iphone/", "text": "iPhone"},
        {"url": "https://www.apple.com/jp/search", "text": "搜索"},
        {"url": "https://www.apple.com/jp/mac/", "text": "Mac"},
        {"url": "https://www.apple.com/jp/search/", "text": "搜索页面"},
        {"url": "https://www.apple.com/jp/ipad/", "text": "iPad"},
    ]
    
    print(f"原始链接数量: {len(mock_links)}")
    for link in mock_links:
        print(f"  - {link['text']}: {link['url']}")
    
    filtered_links = filter_links(mock_links)
    print(f"\n过滤后链接数量: {len(filtered_links)}")
    for link in filtered_links:
        print(f"  ✅ {link['text']}: {link['url']}")

async def test_real_page_links():
    """测试真实页面的链接获取和过滤"""
    print("\n3. 真实页面链接获取测试:")
    print("-" * 30)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)  # 无头模式，更快
        page = await browser.new_page()
        
        try:
            print("正在访问 Apple 日本官网...")
            await page.goto("https://www.apple.com/jp/", timeout=30000)
            await page.wait_for_load_state("networkidle", timeout=10000)
            
            # 获取所有链接
            all_links = await page.evaluate("""
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
            
            if all_links:
                # 去重
                unique_links = []
                seen_urls = set()
                for link in all_links:
                    if link['url'] not in seen_urls:
                        unique_links.append(link)
                        seen_urls.add(link['url'])
                
                print(f"找到 {len(unique_links)} 个唯一链接")
                
                # 查找搜索相关链接
                search_links = [link for link in unique_links if 'search' in link['url'].lower()]
                if search_links:
                    print(f"\n发现 {len(search_links)} 个搜索相关链接:")
                    for link in search_links:
                        print(f"  🔍 {link['text'][:30]}...: {link['url']}")
                else:
                    print("\n✅ 没有发现搜索相关链接")
                
                # 应用过滤
                filtered_links = filter_links(unique_links)
                print(f"\n过滤后剩余 {len(filtered_links)} 个链接")
                
                # 显示前10个过滤后的链接
                print("\n前10个允许的链接:")
                for i, link in enumerate(filtered_links[:10], 1):
                    print(f"  {i:2d}. {link['text'][:40]}...")
                    print(f"      {link['url']}")
                
                # 验证过滤效果
                remaining_search = [link for link in filtered_links if 'search' in link['url'].lower()]
                if remaining_search:
                    print(f"\n⚠️ 警告: 仍有 {len(remaining_search)} 个搜索链接未被过滤!")
                    for link in remaining_search:
                        print(f"  ❌ {link['url']}")
                else:
                    print("\n✅ 所有搜索链接都已被成功过滤!")
                
            else:
                print("❌ 未能获取到任何链接")
                
        except Exception as e:
            print(f"❌ 测试过程中出错: {e}")
        
        finally:
            await browser.close()

async def main():
    """主测试函数"""
    print("URL屏蔽功能综合测试")
    print("此测试将验证搜索页面屏蔽功能是否正常工作")
    print()
    
    # 运行静态测试
    await test_url_blocking()
    
    # 运行真实页面测试
    try:
        await test_real_page_links()
    except Exception as e:
        print(f"真实页面测试失败: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 测试总结:")
    print("- 如果看到搜索链接被标记为'🚫 屏蔽'，说明屏蔽功能正常")
    print("- 如果真实页面测试显示'所有搜索链接都已被成功过滤'，说明功能完全正常")
    print("- 如果有警告信息，可能需要调整屏蔽规则")
    print("=" * 50)

if __name__ == "__main__":
    asyncio.run(main())
