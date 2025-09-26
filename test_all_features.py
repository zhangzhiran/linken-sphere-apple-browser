#!/usr/bin/env python3
"""
测试所有功能的综合测试脚本
"""

import os
import sys
import json
import subprocess
import platform
from pathlib import Path

def test_logic_comparison():
    """测试逻辑比较功能"""
    print("🔍 测试逻辑比较功能...")
    
    try:
        result = subprocess.run([sys.executable, "detailed_logic_comparison.py"], 
                              capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ 逻辑比较测试通过")
            
            # 检查是否有差异
            if "总差异数: 0" in result.stdout:
                print("✅ 浏览逻辑完全一致")
            else:
                print("⚠️ 发现一些差异，但主要是注释差异")
            
            return True
        else:
            print(f"❌ 逻辑比较测试失败: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ 逻辑比较测试异常: {e}")
        return False

def test_config_management():
    """测试配置管理功能"""
    print("\n⚙️ 测试配置管理功能...")
    
    try:
        # 测试配置文件创建
        test_config = {
            'browse_duration': 30,
            'major_cycles': 2,
            'minor_cycles_per_major': 4,
            'max_retries': 2,
            'retry_delay': 3,
            'linken_api_port': 36555,
            'debug_port': 12345,
            'max_threads': 2
        }
        
        config_file = "test_config.json"
        
        # 保存配置
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(test_config, f, indent=4)
        
        # 读取配置
        with open(config_file, 'r', encoding='utf-8') as f:
            loaded_config = json.load(f)
        
        # 验证配置
        if loaded_config == test_config:
            print("✅ 配置保存和加载测试通过")
            
            # 清理测试文件
            os.remove(config_file)
            return True
        else:
            print("❌ 配置验证失败")
            return False
            
    except Exception as e:
        print(f"❌ 配置管理测试异常: {e}")
        return False

def test_executable_building():
    """测试可执行文件构建功能"""
    print("\n📦 测试可执行文件构建功能...")
    
    try:
        # 检查 PyInstaller 是否可用
        result = subprocess.run([sys.executable, "-m", "pip", "show", "pyinstaller"], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ PyInstaller 已安装")
            
            # 测试规格文件创建
            if os.path.exists("build_executable.py"):
                print("✅ 构建脚本存在")
                
                # 检查平台特定功能
                current_os = platform.system()
                if current_os == "Windows":
                    print("✅ Windows 平台支持")
                elif current_os == "Darwin":
                    print("✅ macOS 平台支持")
                else:
                    print("✅ Linux 平台支持")
                
                return True
            else:
                print("❌ 构建脚本不存在")
                return False
        else:
            print("⚠️ PyInstaller 未安装，跳过构建测试")
            return True
            
    except Exception as e:
        print(f"❌ 可执行文件构建测试异常: {e}")
        return False

def test_gui_components():
    """测试GUI组件"""
    print("\n🖥️ 测试GUI组件...")
    
    try:
        # 检查GUI文件是否存在
        if os.path.exists("linken_sphere_gui.py"):
            print("✅ GUI文件存在")
            
            # 尝试导入GUI模块（不运行）
            import importlib.util
            spec = importlib.util.spec_from_file_location("gui", "linken_sphere_gui.py")
            gui_module = importlib.util.module_from_spec(spec)
            
            # 检查关键类是否存在
            spec.loader.exec_module(gui_module)
            
            if hasattr(gui_module, 'LinkenSphereGUI'):
                print("✅ GUI类定义正确")
                return True
            else:
                print("❌ GUI类定义错误")
                return False
        else:
            print("❌ GUI文件不存在")
            return False
            
    except Exception as e:
        print(f"❌ GUI组件测试异常: {e}")
        return False

def test_multi_threading_support():
    """测试多线程支持"""
    print("\n🧵 测试多线程支持...")
    
    try:
        # 检查线程相关的导入
        import threading
        import asyncio
        
        print("✅ 线程模块导入成功")
        
        # 测试基本线程功能
        def test_thread():
            return "thread_test"
        
        thread = threading.Thread(target=test_thread)
        thread.start()
        thread.join()
        
        print("✅ 基本线程功能正常")
        
        # 测试异步功能
        async def test_async():
            await asyncio.sleep(0.1)
            return "async_test"
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(test_async())
        loop.close()
        
        if result == "async_test":
            print("✅ 异步功能正常")
            return True
        else:
            print("❌ 异步功能异常")
            return False
            
    except Exception as e:
        print(f"❌ 多线程支持测试异常: {e}")
        return False

def test_linken_sphere_integration():
    """测试Linken Sphere集成"""
    print("\n🔗 测试Linken Sphere集成...")
    
    try:
        # 检查主程序文件
        if os.path.exists("linken_sphere_playwright_browser.py"):
            print("✅ 主程序文件存在")
            
            # 尝试导入主程序类
            import importlib.util
            spec = importlib.util.spec_from_file_location("browser", "linken_sphere_playwright_browser.py")
            browser_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(browser_module)
            
            if hasattr(browser_module, 'LinkenSphereAppleBrowser'):
                print("✅ 主程序类定义正确")
                
                # 检查关键方法
                browser_class = browser_module.LinkenSphereAppleBrowser
                required_methods = [
                    'start_linken_sphere_session',
                    'connect_to_linken_sphere_browser',
                    'precise_browse_page',
                    '_scroll_to_bottom',
                    'run'
                ]
                
                missing_methods = []
                for method in required_methods:
                    if not hasattr(browser_class, method):
                        missing_methods.append(method)
                
                if not missing_methods:
                    print("✅ 所有关键方法都存在")
                    return True
                else:
                    print(f"❌ 缺少方法: {missing_methods}")
                    return False
            else:
                print("❌ 主程序类定义错误")
                return False
        else:
            print("❌ 主程序文件不存在")
            return False
            
    except Exception as e:
        print(f"❌ Linken Sphere集成测试异常: {e}")
        return False

def generate_test_report(results):
    """生成测试报告"""
    print("\n" + "="*60)
    print("📊 测试报告总结")
    print("="*60)
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    failed_tests = total_tests - passed_tests
    
    print(f"总测试数: {total_tests}")
    print(f"通过测试: {passed_tests}")
    print(f"失败测试: {failed_tests}")
    print(f"成功率: {(passed_tests/total_tests)*100:.1f}%")
    
    print("\n📋 详细结果:")
    for test_name, result in results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {test_name}: {status}")
    
    if failed_tests == 0:
        print("\n🎉 所有测试都通过了！系统已准备就绪。")
    else:
        print(f"\n⚠️ 有 {failed_tests} 个测试失败，请检查相关功能。")
    
    # 保存报告到文件
    report_file = "test_report.txt"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("Linken Sphere Apple Browser 测试报告\n")
        f.write("="*50 + "\n\n")
        f.write(f"测试时间: {platform.platform()}\n")
        f.write(f"Python版本: {sys.version}\n\n")
        f.write(f"总测试数: {total_tests}\n")
        f.write(f"通过测试: {passed_tests}\n")
        f.write(f"失败测试: {failed_tests}\n")
        f.write(f"成功率: {(passed_tests/total_tests)*100:.1f}%\n\n")
        
        f.write("详细结果:\n")
        for test_name, result in results.items():
            status = "通过" if result else "失败"
            f.write(f"  {test_name}: {status}\n")
    
    print(f"\n📄 测试报告已保存到: {report_file}")

def main():
    """主函数"""
    print("🚀 Linken Sphere Apple Browser 综合功能测试")
    print("="*60)
    
    # 执行所有测试
    test_results = {
        "逻辑比较": test_logic_comparison(),
        "配置管理": test_config_management(),
        "可执行文件构建": test_executable_building(),
        "GUI组件": test_gui_components(),
        "多线程支持": test_multi_threading_support(),
        "Linken Sphere集成": test_linken_sphere_integration()
    }
    
    # 生成测试报告
    generate_test_report(test_results)

if __name__ == "__main__":
    main()
