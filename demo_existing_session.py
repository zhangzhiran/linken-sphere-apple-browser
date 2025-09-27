#!/usr/bin/env python3
"""
演示使用现有浏览器会话功能
"""

import asyncio
import sys
import os

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from linken_sphere_playwright_browser import LinkenSphereAppleBrowser

def show_banner():
    """显示横幅"""
    print("🍎" + "=" * 58 + "🍎")
    print("🔗 Linken Sphere Apple Browser - 现有会话功能演示")
    print("🍎" + "=" * 58 + "🍎")
    print()

def show_instructions():
    """显示使用说明"""
    print("📋 使用说明:")
    print("1. 确保 Linken Sphere 正在运行")
    print("2. 手动启动任意一个配置文件的浏览器窗口")
    print("3. 保持浏览器窗口打开状态")
    print("4. 运行此演示程序")
    print()

async def demo_existing_session():
    """演示现有会话功能"""
    print("🔍 正在检测现有的浏览器会话...")
    
    # 创建浏览器实例
    browser = LinkenSphereAppleBrowser(
        browse_duration=20,  # 缩短演示时间
        major_cycles=1,      # 只运行1个大循环
        max_retries=2,
        use_existing_session=True  # 使用现有会话
    )
    
    # 检测现有会话
    existing_sessions = browser.find_existing_browser_sessions()
    
    if not existing_sessions:
        print("❌ 未发现现有的浏览器会话")
        print()
        print("请按照以下步骤操作:")
        print("1. 打开 Linken Sphere")
        print("2. 选择任意配置文件")
        print("3. 点击'启动浏览器'")
        print("4. 等待浏览器窗口完全加载")
        print("5. 重新运行此演示程序")
        return False
    
    print(f"✅ 发现 {len(existing_sessions)} 个现有会话:")
    for i, session in enumerate(existing_sessions):
        print(f"   {i+1}. 端口 {session['debug_port']} - {session['tabs_count']} 个标签页")
    print()
    
    # 询问用户是否继续
    try:
        response = input("是否开始演示自动化浏览? (y/n): ").strip().lower()
        if response not in ['y', 'yes', '是']:
            print("演示已取消")
            return False
    except KeyboardInterrupt:
        print("\n演示已取消")
        return False
    
    print()
    print("🚀 开始演示自动化浏览...")
    print("=" * 50)
    
    try:
        success = await browser.run()
        print("=" * 50)
        if success:
            print("✅ 演示完成！现有会话功能工作正常。")
        else:
            print("❌ 演示过程中出现问题")
        return success
    except KeyboardInterrupt:
        print("\n⏹️ 演示被用户中断")
        return False
    except Exception as e:
        print(f"❌ 演示过程中出现异常: {e}")
        return False

def show_feature_comparison():
    """显示功能对比"""
    print("\n📊 功能对比:")
    print("+" + "-" * 58 + "+")
    print("| 特性           | 现有会话模式 | 新会话模式   |")
    print("+" + "-" * 58 + "+")
    print("| 启动速度       | ⚡ 快速     | 🐌 较慢     |")
    print("| 资源占用       | 💚 低       | 🟡 中等     |")
    print("| 配置复杂度     | 🟢 简单     | 🟡 中等     |")
    print("| 指纹保持       | ✅ 完美     | ✅ 良好     |")
    print("| 多线程支持     | ✅ 支持     | ✅ 支持     |")
    print("| 推荐使用       | ⭐⭐⭐⭐⭐ | ⭐⭐⭐     |")
    print("+" + "-" * 58 + "+")

def main():
    """主函数"""
    show_banner()
    show_instructions()
    
    try:
        # 运行演示
        success = asyncio.run(demo_existing_session())
        
        # 显示功能对比
        show_feature_comparison()
        
        print("\n" + "🍎" + "=" * 58 + "🍎")
        if success:
            print("🎉 演示成功完成！你现在可以使用现有会话功能了。")
        else:
            print("💡 请按照说明准备环境后重新运行演示。")
        print("🍎" + "=" * 58 + "🍎")
        
    except KeyboardInterrupt:
        print("\n👋 演示已退出")
    except Exception as e:
        print(f"\n❌ 演示过程中出现未预期的错误: {e}")

if __name__ == "__main__":
    main()
