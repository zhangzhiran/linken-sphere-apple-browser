#!/usr/bin/env python3
"""
URL屏蔽配置文件
定义需要屏蔽的URL模式
"""

# 屏蔽的URL模式列表
BLOCKED_URL_PATTERNS = [
    # 搜索相关页面
    '/search',
    '/search/',
    'apple.com/jp/search',
    
    # 可能添加的其他屏蔽页面
    # '/support/contact',  # 联系支持页面
    # '/legal/',           # 法律条款页面
    # '/privacy/',         # 隐私政策页面
]

# 屏蔽的URL关键词（更宽泛的匹配）
BLOCKED_KEYWORDS = [
    'search',
    # 'contact',
    # 'legal',
    # 'privacy',
    # 'terms',
]

def is_url_blocked(url):
    """
    检查URL是否应该被屏蔽
    
    Args:
        url (str): 要检查的URL
        
    Returns:
        bool: True表示应该屏蔽，False表示允许访问
    """
    if not url:
        return True
    
    url_lower = url.lower()
    
    # 检查精确模式匹配
    for pattern in BLOCKED_URL_PATTERNS:
        if pattern.lower() in url_lower:
            return True
    
    # 检查关键词匹配（可选，更严格的过滤）
    # for keyword in BLOCKED_KEYWORDS:
    #     if keyword.lower() in url_lower:
    #         return True
    
    return False

def get_blocked_patterns_js():
    """
    获取用于JavaScript的屏蔽模式数组
    
    Returns:
        str: JavaScript数组字符串
    """
    patterns_js = [f"'{pattern}'" for pattern in BLOCKED_URL_PATTERNS]
    return '[' + ', '.join(patterns_js) + ']'

def filter_links(links):
    """
    过滤链接列表，移除被屏蔽的链接
    
    Args:
        links (list): 链接列表，每个元素应该有'url'字段
        
    Returns:
        list: 过滤后的链接列表
    """
    filtered_links = []
    blocked_count = 0
    
    for link in links:
        url = link.get('url', '') if isinstance(link, dict) else str(link)
        
        if not is_url_blocked(url):
            filtered_links.append(link)
        else:
            blocked_count += 1
    
    if blocked_count > 0:
        print(f"🚫 已屏蔽 {blocked_count} 个不适合的链接")
    
    return filtered_links

# 使用示例
if __name__ == "__main__":
    # 测试URL屏蔽功能
    test_urls = [
        "https://www.apple.com/jp/",
        "https://www.apple.com/jp/search",
        "https://www.apple.com/jp/search/",
        "https://www.apple.com/jp/iphone/",
        "https://www.apple.com/jp/mac/",
        "https://www.apple.com/jp/search?q=iphone",
    ]
    
    print("URL屏蔽测试:")
    print("=" * 40)
    
    for url in test_urls:
        blocked = is_url_blocked(url)
        status = "🚫 屏蔽" if blocked else "✅ 允许"
        print(f"{status}: {url}")
    
    print("\nJavaScript屏蔽模式:")
    print(get_blocked_patterns_js())
