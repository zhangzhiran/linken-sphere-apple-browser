#!/usr/bin/env python3
"""
自动安装脚本
"""

import subprocess
import sys
import platform

def run_command(command):
    """运行命令并显示输出"""
    print(f"执行: {command}")
    try:
        result = subprocess.run(command, shell=True, check=True, 
                              capture_output=True, text=True)
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"错误: {e}")
        print(f"输出: {e.stdout}")
        print(f"错误输出: {e.stderr}")
        return False

def main():
    """主安装流程"""
    print("Apple Website Browser 安装程序")
    print("=" * 40)
    print(f"系统: {platform.system()}")
    print(f"Python 版本: {sys.version}")
    
    # 检查 Python 版本
    if sys.version_info < (3, 7):
        print("错误: 需要 Python 3.7 或更高版本")
        return False
    
    # 安装依赖
    print("\n1. 安装 Python 依赖...")
    if not run_command(f"{sys.executable} -m pip install playwright"):
        print("依赖安装失败")
        return False
    
    # 安装浏览器
    print("\n2. 安装 Playwright 浏览器...")
    if not run_command(f"{sys.executable} -m playwright install"):
        print("浏览器安装失败")
        return False
    
    print("\n✅ 安装完成！")
    print("\n使用方法:")
    print("python apple_website_browser.py  # 完整版")
    print("python simple_browser.py        # 简化版")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
