#!/usr/bin/env python3
"""
Cross-Platform Compatibility Test for Linken Sphere Apple Browser
Tests all platform-specific functionality and dependencies
"""

import os
import sys
import platform
import subprocess
import importlib
import socket
import json
from pathlib import Path

class CrossPlatformTester:
    def __init__(self):
        self.system = platform.system()
        self.issues = []
        self.warnings = []
        
    def test_python_environment(self):
        """测试Python环境"""
        print("🐍 测试Python环境...")
        
        # Python版本
        version = sys.version_info
        if version < (3, 8):
            self.issues.append(f"Python版本过低: {version.major}.{version.minor}")
        else:
            print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
        
        # 平台信息
        print(f"✅ 平台: {self.system} {platform.machine()}")
        print(f"✅ 架构: {platform.architecture()[0]}")
        
    def test_required_modules(self):
        """测试必需模块"""
        print("\n📦 测试必需模块...")
        
        required_modules = {
            'tkinter': 'GUI界面',
            'asyncio': '异步编程',
            'threading': '多线程',
            'json': 'JSON处理',
            'pathlib': '路径处理',
            'configparser': '配置文件',
            'logging': '日志记录'
        }
        
        for module, description in required_modules.items():
            try:
                importlib.import_module(module)
                print(f"✅ {module} - {description}")
            except ImportError:
                self.issues.append(f"缺少核心模块: {module} ({description})")
    
    def test_optional_modules(self):
        """测试可选模块"""
        print("\n🔧 测试可选模块...")
        
        optional_modules = {
            'requests': 'HTTP请求',
            'playwright': '浏览器自动化',
            'PIL': '图像处理'
        }
        
        for module, description in optional_modules.items():
            try:
                importlib.import_module(module)
                print(f"✅ {module} - {description}")
            except ImportError:
                self.warnings.append(f"缺少可选模块: {module} ({description})")
    
    def test_gui_functionality(self):
        """测试GUI功能"""
        print("\n🖥️ 测试GUI功能...")
        
        try:
            import tkinter as tk
            from tkinter import ttk, messagebox, scrolledtext, filedialog
            
            # 创建测试窗口
            root = tk.Tk()
            root.withdraw()  # 隐藏窗口
            
            # 测试基本组件
            frame = ttk.Frame(root)
            button = ttk.Button(frame, text="Test")
            entry = ttk.Entry(frame)
            text = scrolledtext.ScrolledText(frame)
            
            print("✅ Tkinter基本组件")
            
            # 测试图标支持
            try:
                if self.system == "Windows":
                    # Windows图标测试
                    if os.path.exists("app_icon.ico"):
                        root.iconbitmap("app_icon.ico")
                        print("✅ Windows图标支持")
                    else:
                        self.warnings.append("Windows图标文件不存在")
                else:
                    # macOS/Linux图标测试
                    if os.path.exists("app_icon.png"):
                        try:
                            from PIL import Image, ImageTk
                            img = Image.open("app_icon.png")
                            photo = ImageTk.PhotoImage(img)
                            root.iconphoto(True, photo)
                            print("✅ PNG图标支持")
                        except ImportError:
                            self.warnings.append("PIL不可用，无法设置PNG图标")
                    else:
                        self.warnings.append("PNG图标文件不存在")
            
            except Exception as e:
                self.warnings.append(f"图标设置失败: {e}")
            
            root.destroy()
            
        except Exception as e:
            self.issues.append(f"GUI功能测试失败: {e}")
    
    def test_file_operations(self):
        """测试文件操作"""
        print("\n📁 测试文件操作...")
        
        # 测试路径处理
        try:
            from pathlib import Path
            test_path = Path("test_file.txt")
            
            # 写入测试
            test_path.write_text("test", encoding='utf-8')
            
            # 读取测试
            content = test_path.read_text(encoding='utf-8')
            
            # 删除测试文件
            test_path.unlink()
            
            print("✅ 文件读写操作")
            
        except Exception as e:
            self.issues.append(f"文件操作失败: {e}")
        
        # 测试配置文件
        try:
            import configparser
            config = configparser.ConfigParser()
            config['DEFAULT'] = {'test': 'value'}
            
            with open('test_config.ini', 'w') as f:
                config.write(f)
            
            config.read('test_config.ini')
            os.remove('test_config.ini')
            
            print("✅ 配置文件处理")
            
        except Exception as e:
            self.issues.append(f"配置文件处理失败: {e}")
    
    def test_network_connectivity(self):
        """测试网络连接"""
        print("\n🌐 测试网络连接...")
        
        # 测试Linken Sphere API端口
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex(('127.0.0.1', 36555))
            sock.close()
            
            if result == 0:
                print("✅ Linken Sphere API端口(36555)可访问")
            else:
                self.warnings.append("Linken Sphere API端口(36555)不可访问")
                
        except Exception as e:
            self.warnings.append(f"网络测试失败: {e}")
    
    def test_platform_specific(self):
        """测试平台特定功能"""
        print(f"\n🔧 测试{self.system}平台特定功能...")
        
        if self.system == "Windows":
            # Windows特定测试
            try:
                import winreg
                print("✅ Windows注册表访问")
            except ImportError:
                self.warnings.append("Windows注册表访问不可用")
                
        elif self.system == "Darwin":
            # macOS特定测试
            try:
                result = subprocess.run(["sips", "--version"], 
                                      capture_output=True, check=True)
                print("✅ macOS sips工具")
            except (subprocess.CalledProcessError, FileNotFoundError):
                self.warnings.append("macOS sips工具不可用")
                
        elif self.system == "Linux":
            # Linux特定测试
            try:
                result = subprocess.run(["which", "python3"], 
                                      capture_output=True, check=True)
                print("✅ Linux Python3路径")
            except (subprocess.CalledProcessError, FileNotFoundError):
                self.warnings.append("Linux Python3路径检查失败")
    
    def test_source_files(self):
        """测试源文件"""
        print("\n📄 测试源文件...")
        
        required_files = [
            "simple_linken_gui.py",
            "linken_sphere_playwright_browser.py",
            "linken_sphere_api.py"
        ]
        
        for file_path in required_files:
            if os.path.exists(file_path):
                print(f"✅ {file_path}")
            else:
                self.issues.append(f"缺少源文件: {file_path}")
        
        # 测试图标文件
        icon_files = ["app_icon.ico", "app_icon.png"]
        for icon_file in icon_files:
            if os.path.exists(icon_file):
                print(f"✅ {icon_file}")
            else:
                self.warnings.append(f"缺少图标文件: {icon_file}")
    
    def run_all_tests(self):
        """运行所有测试"""
        print("🧪 Linken Sphere Apple Browser - 跨平台兼容性测试")
        print("=" * 70)
        
        self.test_python_environment()
        self.test_required_modules()
        self.test_optional_modules()
        self.test_gui_functionality()
        self.test_file_operations()
        self.test_network_connectivity()
        self.test_platform_specific()
        self.test_source_files()
        
        # 输出结果
        print("\n" + "=" * 70)
        print("📊 测试结果总结")
        print("=" * 70)
        
        if not self.issues and not self.warnings:
            print("🎉 所有测试通过！应用程序完全兼容当前平台。")
            return True
        
        if self.issues:
            print("❌ 发现严重问题:")
            for issue in self.issues:
                print(f"   - {issue}")
        
        if self.warnings:
            print("⚠️ 发现警告:")
            for warning in self.warnings:
                print(f"   - {warning}")
        
        if not self.issues:
            print("\n✅ 核心功能兼容，可以继续构建")
            return True
        else:
            print("\n❌ 存在严重兼容性问题，需要解决后再构建")
            return False

def main():
    """主函数"""
    tester = CrossPlatformTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🚀 可以运行构建脚本:")
        print("   python build_cross_platform.py")
    else:
        print("\n🔧 请先解决兼容性问题")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
