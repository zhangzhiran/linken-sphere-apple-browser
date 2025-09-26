#!/usr/bin/env python3
"""
快速打包脚本 - 一键生成可执行文件
"""

import os
import sys
import subprocess
import platform

def quick_build():
    """快速构建可执行文件"""
    print("🚀 快速构建 Linken Sphere Apple Browser")
    print("=" * 50)
    
    current_os = platform.system()
    print(f"检测到系统: {current_os}")
    
    # 1. 安装 PyInstaller
    print("\n📦 安装 PyInstaller...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
        print("✅ PyInstaller 安装完成")
    except:
        print("❌ PyInstaller 安装失败")
        return False
    
    # 2. 构建命令
    print("\n🔨 开始构建...")
    
    build_cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",  # 单文件模式
        "--noconsole" if current_os == "Windows" else "--console",  # Windows 隐藏控制台
        "--name", f"LinkenSphereAppleBrowser{'_' + current_os}",
        "--add-data", "blocked_urls.py;." if current_os == "Windows" else "blocked_urls.py:.",
        "--hidden-import", "playwright",
        "--hidden-import", "playwright.async_api",
        "--hidden-import", "requests",
        "--hidden-import", "asyncio",
        "linken_sphere_playwright_browser.py"
    ]
    
    try:
        subprocess.run(build_cmd, check=True)
        
        # 检查生成的文件
        if current_os == "Windows":
            exe_name = "LinkenSphereAppleBrowser_Windows.exe"
        else:
            exe_name = f"LinkenSphereAppleBrowser_{current_os}"
        
        exe_path = os.path.join("dist", exe_name)
        
        if os.path.exists(exe_path):
            size = os.path.getsize(exe_path) / (1024 * 1024)
            print(f"\n✅ 构建成功！")
            print(f"📁 文件位置: {exe_path}")
            print(f"📦 文件大小: {size:.1f} MB")
            
            # 创建使用说明
            create_usage_guide(exe_name)
            
            return True
        else:
            print("❌ 构建失败：找不到可执行文件")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ 构建失败: {e}")
        return False

def create_usage_guide(exe_name):
    """创建使用指南"""
    guide = f"""# {exe_name} 使用指南

## 🚀 快速开始

### 1. 准备工作
- 确保 Linken Sphere 正在运行
- 确保有可用的配置文件
- 确保网络连接正常

### 2. 运行程序
- Windows: 双击 {exe_name}
- Mac/Linux: 在终端中运行 ./{exe_name}

### 3. 程序功能
- 自动连接 Linken Sphere
- 浏览 Apple Japan 网站
- 3大循环 × 8小循环 = 24页
- 每页浏览60秒

## ⚠️ 注意事项

1. **Linken Sphere 必须先启动**
2. **需要有可用的配置文件**
3. **确保 API 端口 36555 可用**
4. **程序会生成日志文件**

## 🔧 故障排除

如果遇到问题：
1. 检查 Linken Sphere 是否运行
2. 检查网络连接
3. 查看日志文件了解详细错误信息

## 📞 技术支持

如需帮助，请提供：
- 操作系统信息
- 错误信息
- 日志文件内容
"""
    
    with open(f"{exe_name}_使用指南.txt", "w", encoding="utf-8") as f:
        f.write(guide)
    
    print(f"📝 已创建使用指南: {exe_name}_使用指南.txt")

if __name__ == "__main__":
    success = quick_build()
    
    if success:
        print("\n🎉 打包完成！可以将 dist 目录中的文件分发给其他用户。")
        print("\n💡 提示：")
        print("   - 可执行文件已包含所有必要的 Python 依赖")
        print("   - 用户仍需要安装 Linken Sphere")
        print("   - 用户需要有稳定的网络连接")
    else:
        print("\n❌ 打包失败，请检查错误信息。")
