#!/usr/bin/env python3
"""
详细逻辑比较工具 - 逐行比较关键方法
"""

import re
import difflib

def read_file_lines(filepath):
    """读取文件行"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.readlines()
    except Exception as e:
        print(f"❌ 读取文件失败 {filepath}: {e}")
        return []

def extract_method_lines(lines, method_name):
    """提取方法的所有行"""
    method_lines = []
    in_method = False
    indent_level = 0
    
    for i, line in enumerate(lines):
        # 查找方法定义
        if f"def {method_name}(" in line:
            in_method = True
            indent_level = len(line) - len(line.lstrip())
            method_lines.append((i+1, line.rstrip()))
            continue
        
        if in_method:
            current_indent = len(line) - len(line.lstrip())
            
            # 如果是空行，继续
            if line.strip() == "":
                method_lines.append((i+1, line.rstrip()))
                continue
            
            # 如果缩进回到方法级别或更少，方法结束
            if current_indent <= indent_level and line.strip():
                break
            
            # 添加方法内的行
            method_lines.append((i+1, line.rstrip()))
    
    return method_lines

def normalize_line(line):
    """标准化行 - 移除注释和多余空格"""
    # 移除行尾注释
    line = re.sub(r'#.*$', '', line)
    # 标准化空格
    line = re.sub(r'\s+', ' ', line.strip())
    return line

def compare_methods():
    """比较关键方法"""
    print("🔍 详细逻辑比较分析")
    print("=" * 60)
    
    original_lines = read_file_lines("apple_website_browser .py")
    linken_lines = read_file_lines("linken_sphere_playwright_browser.py")
    
    if not original_lines or not linken_lines:
        print("❌ 无法读取文件")
        return
    
    # 关键方法列表
    key_methods = [
        'precise_browse_page',
        '_scroll_to_bottom',
        'refresh_links', 
        'get_navigation_links',
        'browse_page',
        'retry_operation',
        'safe_goto',
        'safe_evaluate'
    ]
    
    differences_found = 0
    
    for method_name in key_methods:
        print(f"\n🔍 比较方法: {method_name}")
        print("-" * 40)
        
        original_method = extract_method_lines(original_lines, method_name)
        linken_method = extract_method_lines(linken_lines, method_name)
        
        if not original_method:
            print(f"⚠️ 原始文件中未找到方法: {method_name}")
            continue
        
        if not linken_method:
            print(f"⚠️ Linken 文件中未找到方法: {method_name}")
            continue
        
        # 标准化并比较
        original_normalized = [normalize_line(line[1]) for line in original_method if normalize_line(line[1])]
        linken_normalized = [normalize_line(line[1]) for line in linken_method if normalize_line(line[1])]
        
        if original_normalized == linken_normalized:
            print(f"✅ 方法逻辑完全一致 ({len(original_normalized)} 行有效代码)")
        else:
            print(f"❌ 方法逻辑存在差异")
            differences_found += 1
            
            print(f"   原始文件: {len(original_normalized)} 行有效代码")
            print(f"   Linken 文件: {len(linken_normalized)} 行有效代码")
            
            # 显示前几行差异
            diff = list(difflib.unified_diff(
                original_normalized,
                linken_normalized,
                fromfile=f"原始/{method_name}",
                tofile=f"Linken/{method_name}",
                lineterm=""
            ))
            
            if diff:
                print("\n📋 主要差异:")
                for line in diff[:10]:
                    print(f"   {line}")
                if len(diff) > 10:
                    print(f"   ... (还有 {len(diff) - 10} 行差异)")
    
    return differences_found

def check_specific_patterns():
    """检查特定模式"""
    print(f"\n🔍 检查特定浏览模式")
    print("=" * 40)
    
    original_content = open("apple_website_browser .py", 'r', encoding='utf-8').read()
    linken_content = open("linken_sphere_playwright_browser.py", 'r', encoding='utf-8').read()
    
    # 关键模式检查
    patterns = {
        '滚动距离': r'random\.randint\(100,\s*250\)',
        '滚动暂停': r'random\.uniform\(0\.5,\s*1\.5\)',
        '阅读时间': r'random\.uniform\(1\.0,\s*3\.0\)',
        '阅读概率': r'random\.random\(\)\s*<\s*0\.1',
        '浏览时长': r'browse_duration\s*=\s*60',
        '大循环次数': r'major_cycles\s*=\s*3',
        '小循环次数': r'minor_cycles_per_major\s*=\s*8',
        '重试次数': r'max_retries\s*=\s*3',
        '重试延迟': r'retry_delay\s*=\s*5'
    }
    
    pattern_differences = 0
    
    for pattern_name, pattern in patterns.items():
        original_matches = re.findall(pattern, original_content)
        linken_matches = re.findall(pattern, linken_content)
        
        print(f"{pattern_name}:")
        print(f"  原始: {len(original_matches)} 个匹配 {original_matches}")
        print(f"  Linken: {len(linken_matches)} 个匹配 {linken_matches}")
        
        if original_matches != linken_matches:
            print(f"  ❌ 模式不一致")
            pattern_differences += 1
        else:
            print(f"  ✅ 模式一致")
    
    return pattern_differences

def check_timing_logic():
    """检查时间控制逻辑"""
    print(f"\n🕒 检查时间控制逻辑")
    print("=" * 40)
    
    original_lines = read_file_lines("apple_website_browser .py")
    linken_lines = read_file_lines("linken_sphere_playwright_browser.py")
    
    # 提取 precise_browse_page 方法
    original_timing = extract_method_lines(original_lines, "precise_browse_page")
    linken_timing = extract_method_lines(linken_lines, "precise_browse_page")
    
    if original_timing and linken_timing:
        print("📋 时间控制方法对比:")
        
        # 提取关键时间控制行
        timing_keywords = ['time.time()', 'asyncio.sleep', 'duration', 'elapsed', 'remaining']
        
        original_timing_lines = []
        linken_timing_lines = []
        
        for line_num, line in original_timing:
            if any(keyword in line for keyword in timing_keywords):
                original_timing_lines.append(normalize_line(line))
        
        for line_num, line in linken_timing:
            if any(keyword in line for keyword in timing_keywords):
                linken_timing_lines.append(normalize_line(line))
        
        print(f"原始文件时间控制行数: {len(original_timing_lines)}")
        print(f"Linken 文件时间控制行数: {len(linken_timing_lines)}")
        
        if original_timing_lines == linken_timing_lines:
            print("✅ 时间控制逻辑完全一致")
            return 0
        else:
            print("❌ 时间控制逻辑存在差异")
            return 1
    else:
        print("⚠️ 无法找到时间控制方法")
        return 1

def main():
    """主函数"""
    print("🔍 Linken Sphere 与原始文件逻辑比较")
    print("=" * 60)
    
    # 比较方法
    method_differences = compare_methods()
    
    # 检查特定模式
    pattern_differences = check_specific_patterns()
    
    # 检查时间控制
    timing_differences = check_timing_logic()
    
    # 总结
    total_differences = method_differences + pattern_differences + timing_differences
    
    print(f"\n📊 比较结果总结")
    print("=" * 40)
    print(f"方法逻辑差异: {method_differences}")
    print(f"模式差异: {pattern_differences}")
    print(f"时间控制差异: {timing_differences}")
    print(f"总差异数: {total_differences}")
    
    if total_differences == 0:
        print("\n🎉 完美！两个文件的浏览逻辑完全一致！")
    else:
        print(f"\n⚠️ 发现 {total_differences} 个差异，需要修复")

if __name__ == "__main__":
    main()
