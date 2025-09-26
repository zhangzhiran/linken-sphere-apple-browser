#!/usr/bin/env python3
"""
逻辑比较工具 - 比较原始文件和 Linken Sphere 版本的差异
"""

import ast
import difflib
import re
from pathlib import Path

class LogicComparator:
    """逻辑比较器"""
    
    def __init__(self):
        self.original_file = "apple_website_browser .py"
        self.linken_file = "linken_sphere_playwright_browser.py"
        self.differences = []
        
    def read_file_content(self, filepath):
        """读取文件内容"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"❌ 读取文件失败 {filepath}: {e}")
            return ""
    
    def extract_methods(self, content, class_name):
        """提取类中的方法"""
        try:
            tree = ast.parse(content)
            methods = {}
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef) and node.name == class_name:
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            # 获取方法的源代码
                            method_lines = content.split('\n')[item.lineno-1:item.end_lineno]
                            methods[item.name] = '\n'.join(method_lines)
            
            return methods
        except Exception as e:
            print(f"❌ 解析文件失败: {e}")
            return {}
    
    def compare_method_logic(self, original_method, linken_method, method_name):
        """比较方法逻辑"""
        print(f"\n🔍 比较方法: {method_name}")
        print("=" * 50)
        
        if not original_method:
            print(f"⚠️ 原始文件中未找到方法: {method_name}")
            return
        
        if not linken_method:
            print(f"⚠️ Linken Sphere 文件中未找到方法: {method_name}")
            return
        
        # 标准化代码（移除注释和空行）
        original_normalized = self.normalize_code(original_method)
        linken_normalized = self.normalize_code(linken_method)
        
        if original_normalized == linken_normalized:
            print(f"✅ 方法逻辑完全一致")
        else:
            print(f"❌ 方法逻辑存在差异")
            
            # 显示差异
            diff = list(difflib.unified_diff(
                original_normalized.splitlines(keepends=True),
                linken_normalized.splitlines(keepends=True),
                fromfile=f"原始/{method_name}",
                tofile=f"Linken/{method_name}",
                lineterm=""
            ))
            
            if diff:
                print("\n📋 详细差异:")
                for line in diff[:20]:  # 限制显示行数
                    print(line.rstrip())
                if len(diff) > 20:
                    print(f"... (还有 {len(diff) - 20} 行差异)")
            
            self.differences.append({
                'method': method_name,
                'type': 'logic_difference',
                'description': f"方法 {method_name} 的逻辑存在差异"
            })
    
    def normalize_code(self, code):
        """标准化代码 - 移除注释、空行和多余空格"""
        lines = []
        for line in code.split('\n'):
            # 移除注释
            line = re.sub(r'#.*$', '', line)
            # 移除多余空格
            line = line.strip()
            # 跳过空行
            if line:
                lines.append(line)
        return '\n'.join(lines)
    
    def compare_key_methods(self):
        """比较关键方法"""
        print("🔍 开始逻辑比较分析")
        print("=" * 60)
        
        # 读取文件内容
        original_content = self.read_file_content(self.original_file)
        linken_content = self.read_file_content(self.linken_file)
        
        if not original_content or not linken_content:
            print("❌ 无法读取文件内容")
            return
        
        # 提取方法
        original_methods = self.extract_methods(original_content, "AppleWebsiteBrowser")
        linken_methods = self.extract_methods(linken_content, "LinkenSphereAppleBrowser")
        
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
        
        print(f"📋 原始文件方法数: {len(original_methods)}")
        print(f"📋 Linken 文件方法数: {len(linken_methods)}")
        
        # 比较每个关键方法
        for method_name in key_methods:
            original_method = original_methods.get(method_name, "")
            linken_method = linken_methods.get(method_name, "")
            self.compare_method_logic(original_method, linken_method, method_name)
        
        # 检查是否有新增或缺失的方法
        original_set = set(original_methods.keys())
        linken_set = set(linken_methods.keys())
        
        missing_in_linken = original_set - linken_set
        new_in_linken = linken_set - original_set
        
        if missing_in_linken:
            print(f"\n⚠️ Linken 版本中缺失的方法: {missing_in_linken}")
            for method in missing_in_linken:
                self.differences.append({
                    'method': method,
                    'type': 'missing_method',
                    'description': f"Linken 版本中缺失方法: {method}"
                })
        
        if new_in_linken:
            print(f"\n📋 Linken 版本中新增的方法: {new_in_linken}")
    
    def check_timing_controls(self):
        """检查时间控制逻辑"""
        print(f"\n🕒 检查时间控制逻辑")
        print("=" * 30)
        
        original_content = self.read_file_content(self.original_file)
        linken_content = self.read_file_content(self.linken_file)
        
        # 检查关键时间控制模式
        timing_patterns = [
            r'browse_duration\s*=\s*\d+',
            r'await\s+asyncio\.sleep\(',
            r'time\.time\(\)',
            r'random\.uniform\(',
            r'random\.randint\(',
            r'timeout\s*=\s*\d+'
        ]
        
        for pattern in timing_patterns:
            original_matches = re.findall(pattern, original_content)
            linken_matches = re.findall(pattern, linken_content)
            
            print(f"模式 '{pattern}':")
            print(f"  原始文件: {len(original_matches)} 个匹配")
            print(f"  Linken 文件: {len(linken_matches)} 个匹配")
            
            if len(original_matches) != len(linken_matches):
                self.differences.append({
                    'method': 'timing_control',
                    'type': 'timing_difference',
                    'description': f"时间控制模式 '{pattern}' 的使用次数不一致"
                })
    
    def generate_report(self):
        """生成比较报告"""
        print(f"\n📊 逻辑比较报告")
        print("=" * 50)
        
        if not self.differences:
            print("✅ 未发现逻辑差异 - 两个文件的浏览逻辑完全一致！")
        else:
            print(f"❌ 发现 {len(self.differences)} 个差异:")
            
            for i, diff in enumerate(self.differences, 1):
                print(f"\n{i}. {diff['description']}")
                print(f"   类型: {diff['type']}")
                print(f"   方法: {diff['method']}")
        
        # 生成修复建议
        self.generate_fix_suggestions()
    
    def generate_fix_suggestions(self):
        """生成修复建议"""
        if not self.differences:
            return
        
        print(f"\n🔧 修复建议")
        print("=" * 30)
        
        for diff in self.differences:
            if diff['type'] == 'missing_method':
                print(f"• 需要从原始文件复制方法: {diff['method']}")
            elif diff['type'] == 'logic_difference':
                print(f"• 需要检查并修正方法: {diff['method']}")
            elif diff['type'] == 'timing_difference':
                print(f"• 需要检查时间控制逻辑的一致性")

def main():
    """主函数"""
    comparator = LogicComparator()
    
    # 执行比较
    comparator.compare_key_methods()
    comparator.check_timing_controls()
    
    # 生成报告
    comparator.generate_report()

if __name__ == "__main__":
    main()
