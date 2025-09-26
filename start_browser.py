#!/usr/bin/env python3
"""
Apple Website Browser 启动器
支持多种浏览器模式选择
"""

import sys
import os
import subprocess
import platform

def print_banner():
    """打印程序横幅"""
    print("🍎 Apple Website Browser 启动器")
    print("=" * 60)
    print("支持多种浏览器模式和配置选项")
    print("=" * 60)

def check_dependencies():
    """检查依赖项"""
    print("🔍 检查依赖项...")
    
    missing_deps = []
    
    # 检查 Python 模块
    try:
        import playwright
        print("✅ Playwright 已安装")
    except ImportError:
        missing_deps.append("playwright")
    
    try:
        import selenium
        print("✅ Selenium 已安装")
    except ImportError:
        missing_deps.append("selenium")
    
    try:
        import requests
        print("✅ Requests 已安装")
    except ImportError:
        missing_deps.append("requests")
    
    if missing_deps:
        print(f"\n❌ 缺少依赖项: {', '.join(missing_deps)}")
        print("请运行以下命令安装:")
        print("pip install -r requirements.txt")
        return False
    
    print("✅ 所有依赖项都已安装")
    return True

def show_menu():
    """显示主菜单"""
    print("\n📋 请选择浏览器模式:")
    print("1. 🎨 图形界面版 (推荐)")
    print("2. 🎭 Playwright 版 (完整功能)")
    print("3. 🔒 Linken Sphere API 版 (需要支持API的套餐)")
    print("4. 🔧 Linken Sphere 手动版 (API不可用时)")
    print("5. 🚀 简化版 (快速测试)")
    print("6. 🧪 测试工具")
    print("7. ❓ 帮助和说明")
    print("0. 🚪 退出")
    print("-" * 40)

def run_gui_version():
    """运行图形界面版"""
    print("🎨 启动图形界面版...")
    
    if not os.path.exists("apple_browser_gui.py"):
        print("❌ 找不到 apple_browser_gui.py 文件")
        return False
    
    try:
        subprocess.run([sys.executable, "apple_browser_gui.py"], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 启动失败: {e}")
        return False
    except KeyboardInterrupt:
        print("\n⏹️ 用户中断")
        return True

def run_playwright_version():
    """运行 Playwright 版"""
    print("🎭 启动 Playwright 版...")
    
    if not os.path.exists("apple_website_browser .py"):
        print("❌ 找不到 apple_website_browser .py 文件")
        return False
    
    try:
        subprocess.run([sys.executable, "apple_website_browser .py"], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 启动失败: {e}")
        return False
    except KeyboardInterrupt:
        print("\n⏹️ 用户中断")
        return True

def run_linken_sphere_api_version():
    """运行 Linken Sphere API 版"""
    print("🔒 启动 Linken Sphere API 版...")

    if not os.path.exists("linken_sphere_browser.py"):
        print("❌ 找不到 linken_sphere_browser.py 文件")
        return False

    # 检查 Linken Sphere 连接
    print("🔍 检查 Linken Sphere API 连接...")
    try:
        from linken_sphere_api import LinkenSphereAPI
        api = LinkenSphereAPI()
        if api.check_connection():
            print("✅ Linken Sphere API 连接正常")
        else:
            print("⚠️ 无法连接到 Linken Sphere API")
            print("💡 提示：如果API不可用，请尝试选项4（手动版）")
            return False
    except ImportError:
        print("⚠️ Linken Sphere API 模块不可用")
        return False
    except Exception as e:
        print(f"⚠️ Linken Sphere API 检查失败: {e}")
        print("💡 提示：如果API不可用，请尝试选项4（手动版）")
        return False

    try:
        subprocess.run([sys.executable, "linken_sphere_browser.py"], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 启动失败: {e}")
        return False
    except KeyboardInterrupt:
        print("\n⏹️ 用户中断")
        return True

def run_linken_sphere_manual_version():
    """运行 Linken Sphere 手动版"""
    print("🔧 启动 Linken Sphere 手动版...")

    if not os.path.exists("linken_sphere_manual.py"):
        print("❌ 找不到 linken_sphere_manual.py 文件")
        return False

    # 检查 Linken Sphere 进程
    print("🔍 检查 Linken Sphere 进程...")
    try:
        import psutil
        linken_processes = []
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if proc.info['name'] and 'linken' in proc.info['name'].lower():
                    linken_processes.append(proc.info['name'])
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        if linken_processes:
            print(f"✅ 检测到 Linken Sphere 进程: {len(linken_processes)} 个")
        else:
            print("⚠️ 未检测到 Linken Sphere 进程")
            print("请确保 Linken Sphere 应用程序正在运行")
    except ImportError:
        print("⚠️ 无法检查进程状态（psutil 未安装）")
    except Exception as e:
        print(f"⚠️ 进程检查失败: {e}")

    try:
        subprocess.run([sys.executable, "linken_sphere_manual.py"], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 启动失败: {e}")
        return False
    except KeyboardInterrupt:
        print("\n⏹️ 用户中断")
        return True

def run_simple_version():
    """运行简化版"""
    print("🚀 启动简化版...")
    
    if not os.path.exists("simple_browser.py"):
        print("❌ 找不到 simple_browser.py 文件")
        return False
    
    try:
        subprocess.run([sys.executable, "simple_browser.py"], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 启动失败: {e}")
        return False
    except KeyboardInterrupt:
        print("\n⏹️ 用户中断")
        return True

def show_test_menu():
    """显示测试菜单"""
    print("\n🧪 测试工具菜单:")
    print("1. 🔗 Linken Sphere 连接测试")
    print("2. 📜 滚动功能测试")
    print("3. 🔄 双层循环测试")
    print("4. 🌐 网络重试测试")
    print("5. 🚫 URL 屏蔽测试")
    print("0. 🔙 返回主菜单")
    print("-" * 40)
    
    while True:
        try:
            choice = input("请选择测试工具 (0-5): ").strip()
            
            if choice == "0":
                return
            elif choice == "1":
                run_linken_sphere_test()
            elif choice == "2":
                run_scroll_test()
            elif choice == "3":
                run_dual_loop_test()
            elif choice == "4":
                run_network_test()
            elif choice == "5":
                run_url_blocking_test()
            else:
                print("❌ 无效选择，请输入 0-5")
                
        except KeyboardInterrupt:
            print("\n🔙 返回主菜单")
            return

def run_linken_sphere_test():
    """运行 Linken Sphere 测试"""
    print("🔗 启动 Linken Sphere 连接测试...")
    
    if not os.path.exists("test_linken_sphere.py"):
        print("❌ 找不到 test_linken_sphere.py 文件")
        return
    
    try:
        subprocess.run([sys.executable, "test_linken_sphere.py"])
    except KeyboardInterrupt:
        print("\n⏹️ 测试中断")

def run_scroll_test():
    """运行滚动测试"""
    print("📜 启动滚动功能测试...")
    
    if not os.path.exists("test_scroll.py"):
        print("❌ 找不到 test_scroll.py 文件")
        return
    
    try:
        subprocess.run([sys.executable, "test_scroll.py"])
    except KeyboardInterrupt:
        print("\n⏹️ 测试中断")

def run_dual_loop_test():
    """运行双层循环测试"""
    print("🔄 启动双层循环测试...")
    
    if not os.path.exists("test_dual_loop.py"):
        print("❌ 找不到 test_dual_loop.py 文件")
        return
    
    try:
        subprocess.run([sys.executable, "test_dual_loop.py"])
    except KeyboardInterrupt:
        print("\n⏹️ 测试中断")

def run_network_test():
    """运行网络重试测试"""
    print("🌐 启动网络重试测试...")
    
    if not os.path.exists("test_network_retry.py"):
        print("❌ 找不到 test_network_retry.py 文件")
        return
    
    try:
        subprocess.run([sys.executable, "test_network_retry.py"])
    except KeyboardInterrupt:
        print("\n⏹️ 测试中断")

def run_url_blocking_test():
    """运行 URL 屏蔽测试"""
    print("🚫 启动 URL 屏蔽测试...")
    
    if not os.path.exists("test_url_blocking.py"):
        print("❌ 找不到 test_url_blocking.py 文件")
        return
    
    try:
        subprocess.run([sys.executable, "test_url_blocking.py"])
    except KeyboardInterrupt:
        print("\n⏹️ 测试中断")

def show_help():
    """显示帮助信息"""
    print("\n❓ 帮助和说明")
    print("=" * 60)
    print("🎨 图形界面版:")
    print("   - 美观的现代化GUI界面")
    print("   - 实时配置和监控功能")
    print("   - 推荐新用户使用")
    print()
    print("🎭 Playwright 版:")
    print("   - 完整功能的命令行版本")
    print("   - 智能双层循环浏览系统")
    print("   - 精确时间控制和重试机制")
    print()
    print("🔒 Linken Sphere API 版:")
    print("   - 通过API自动管理指纹浏览器")
    print("   - 自动创建和配置浏览器配置文件")
    print("   - 需要支持API的 Linken Sphere 套餐")
    print()
    print("🔧 Linken Sphere 手动版:")
    print("   - 手动启动 Linken Sphere 浏览器")
    print("   - 程序通过调试端口连接")
    print("   - 适用于API不可用的套餐")
    print()
    print("🚀 简化版:")
    print("   - 基础功能的轻量版本")
    print("   - 适合快速测试和学习")
    print()
    print("🧪 测试工具:")
    print("   - 各种功能的独立测试")
    print("   - 验证系统配置和连接")
    print("   - 包含 Linken Sphere 连接测试")
    print("=" * 60)

    input("\n按回车键返回主菜单...")

def main():
    """主函数"""
    print_banner()
    
    # 检查依赖项
    if not check_dependencies():
        print("\n请先安装依赖项后再运行")
        return
    
    while True:
        show_menu()
        
        try:
            choice = input("请选择 (0-7): ").strip()

            if choice == "0":
                print("👋 再见！")
                break
            elif choice == "1":
                run_gui_version()
            elif choice == "2":
                run_playwright_version()
            elif choice == "3":
                run_linken_sphere_api_version()
            elif choice == "4":
                run_linken_sphere_manual_version()
            elif choice == "5":
                run_simple_version()
            elif choice == "6":
                show_test_menu()
            elif choice == "7":
                show_help()
            else:
                print("❌ 无效选择，请输入 0-7")
                
        except KeyboardInterrupt:
            print("\n👋 再见！")
            break
        except Exception as e:
            print(f"❌ 发生错误: {e}")


if __name__ == "__main__":
    main()
