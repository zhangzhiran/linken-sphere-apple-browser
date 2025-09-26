#!/usr/bin/env python3
"""
Enhanced Cross-Platform Build System for Linken Sphere Apple Browser
Supports Windows (.exe), macOS (.app/.dmg), and Linux builds with proper icons and dependencies
"""

import os
import sys
import platform
import subprocess
import shutil
import json
from pathlib import Path

class CrossPlatformBuilder:
    def __init__(self):
        self.system = platform.system()
        self.app_name = "LinkenSphereAppleBrowser"
        self.script_name = "simple_linken_gui.py"
        self.build_dir = "dist"
        self.work_dir = "build"
        self.spec_dir = "build"

        # Platform-specific configurations
        self.icon_files = {
            "Windows": "app_icon.ico",
            "Darwin": "app_icon.icns",  # macOS prefers .icns
            "Linux": "app_icon.png"
        }

        # Required data files for all platforms
        self.data_files = [
            "linken_sphere_playwright_browser.py",
            "linken_sphere_api.py",
            "app_icon.ico",
            "app_icon.png"
        ]

        # Optional configuration files
        self.optional_files = [
            "linken_sphere_config.json",
            "config.json",
            "settings.ini"
        ]

        # Hidden imports required for all platforms
        self.hidden_imports = [
            "asyncio",
            "playwright",
            "playwright.async_api",
            "requests",
            "PIL",
            "PIL.Image",
            "PIL.ImageTk",
            "tkinter",
            "tkinter.ttk",
            "tkinter.messagebox",
            "tkinter.scrolledtext",
            "tkinter.filedialog",
            "threading",
            "json",
            "logging",
            "pathlib",
            "configparser"
        ]
        
    def check_dependencies(self):
        """检查构建依赖"""
        print("🔧 检查构建依赖...")

        # 检查Python版本
        python_version = sys.version_info
        if python_version < (3, 8):
            print(f"❌ Python版本过低: {python_version.major}.{python_version.minor}")
            print("   需要Python 3.8或更高版本")
            return False
        print(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}")

        # 检查PyInstaller
        try:
            import PyInstaller
            print(f"✅ PyInstaller {PyInstaller.__version__}")
        except ImportError:
            print("📦 安装PyInstaller...")
            try:
                subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
                print("✅ PyInstaller 安装完成")
            except subprocess.CalledProcessError:
                print("❌ PyInstaller 安装失败")
                return False

        # 检查Pillow (用于图标处理)
        try:
            import PIL
            print(f"✅ Pillow {PIL.__version__}")
        except ImportError:
            print("📦 安装Pillow...")
            try:
                subprocess.run([sys.executable, "-m", "pip", "install", "Pillow"], check=True)
                print("✅ Pillow 安装完成")
            except subprocess.CalledProcessError:
                print("❌ Pillow 安装失败")
                return False

        # 检查其他必要依赖
        required_packages = ["requests", "playwright"]
        for package in required_packages:
            try:
                __import__(package)
                print(f"✅ {package}")
            except ImportError:
                print(f"⚠️ 缺少依赖: {package}")
                print(f"   请运行: pip install {package}")

        return True
    
    def ensure_icons(self):
        """确保图标文件存在"""
        print("🎨 检查图标文件...")
        
        icon_file = self.icon_files.get(self.system, "app_icon.png")
        
        if not os.path.exists(icon_file):
            print(f"⚠️ 图标文件不存在: {icon_file}")
            print("🎨 创建默认图标...")
            
            # 运行图标创建脚本
            if os.path.exists("simple_icon_creator.py"):
                subprocess.run([sys.executable, "simple_icon_creator.py"], check=True)
                print("✅ 图标创建完成")
            else:
                print("❌ 图标创建脚本不存在")
                return False
        
        # 特殊处理macOS的ICNS文件
        if self.system == "Darwin" and icon_file.endswith('.icns'):
            if not os.path.exists(icon_file):
                self.create_icns_from_png()

        if os.path.exists(icon_file):
            print(f"✅ 图标文件就绪: {icon_file}")
            return True
        else:
            print(f"❌ 图标文件仍然不存在: {icon_file}")
            return False

    def create_icns_from_png(self):
        """从PNG创建macOS ICNS图标"""
        png_path = "app_icon.png"
        icns_path = "app_icon.icns"

        if not os.path.exists(png_path):
            print(f"❌ 源PNG文件不存在: {png_path}")
            return False

        try:
            # 方法1: 使用macOS的sips命令
            if self.system == "Darwin":
                subprocess.run([
                    "sips", "-s", "format", "icns",
                    png_path, "--out", icns_path
                ], check=True, capture_output=True)
                print(f"✅ 使用sips创建ICNS: {icns_path}")
                return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass

        try:
            # 方法2: 使用PIL创建多尺寸图标
            from PIL import Image
            import struct

            # 创建多个尺寸的图标
            sizes = [16, 32, 64, 128, 256, 512, 1024]
            images = []

            with Image.open(png_path) as img:
                for size in sizes:
                    resized = img.resize((size, size), Image.Resampling.LANCZOS)
                    images.append(resized)

            # 保存为ICNS (简化版本)
            # 注意：这是一个简化的实现，真正的ICNS格式更复杂
            images[0].save(icns_path, format='ICNS', append_images=images[1:])
            print(f"✅ 使用PIL创建ICNS: {icns_path}")
            return True

        except Exception as e:
            print(f"⚠️ 无法创建ICNS文件: {e}")
            # 回退到使用PNG
            if os.path.exists(png_path):
                shutil.copy2(png_path, icns_path)
                print(f"✅ 复制PNG作为ICNS: {icns_path}")
                return True

        return False

    def get_data_files(self):
        """获取所有需要打包的数据文件"""
        data_files = []

        # 添加必需的数据文件
        for file_path in self.data_files:
            if os.path.exists(file_path):
                abs_path = os.path.abspath(file_path)
                if self.system == "Windows":
                    data_files.append(f"{abs_path};.")
                else:
                    data_files.append(f"{abs_path}:.")
                print(f"✅ 添加数据文件: {file_path}")
            else:
                print(f"⚠️ 数据文件不存在: {file_path}")

        # 添加可选配置文件
        for file_path in self.optional_files:
            if os.path.exists(file_path):
                abs_path = os.path.abspath(file_path)
                if self.system == "Windows":
                    data_files.append(f"{abs_path};.")
                else:
                    data_files.append(f"{abs_path}:.")
                print(f"✅ 添加配置文件: {file_path}")

        return data_files

    def get_hidden_imports(self):
        """获取隐藏导入列表"""
        imports = []
        for module in self.hidden_imports:
            imports.extend(["--hidden-import", module])
        return imports

    def build_windows(self):
        """构建Windows可执行文件"""
        print("🪟 构建Windows可执行文件...")

        icon_path = self.icon_files["Windows"]

        # 确保图标文件存在于当前目录
        if not os.path.exists(icon_path):
            print(f"❌ 图标文件不存在: {icon_path}")
            return False

        # 获取绝对路径
        icon_abs_path = os.path.abspath(icon_path)
        script_abs_path = os.path.abspath(self.script_name)

        # 构建基础命令
        cmd = [
            sys.executable, "-m", "PyInstaller",
            "--onefile",
            "--windowed",
            "--name", self.app_name,
            "--distpath", self.build_dir,
            "--workpath", self.work_dir,
            "--specpath", self.spec_dir,
            "--clean",
            "--icon", icon_abs_path
        ]

        # 添加数据文件
        for data_file in self.get_data_files():
            cmd.extend(["--add-data", data_file])

        # 添加隐藏导入
        cmd.extend(self.get_hidden_imports())

        # 添加主脚本
        cmd.append(script_abs_path)
        
        try:
            subprocess.run(cmd, check=True)
            
            # 复制图标到输出目录
            if os.path.exists(icon_path):
                shutil.copy2(icon_path, os.path.join(self.build_dir, icon_path))
            
            exe_path = os.path.join(self.build_dir, f"{self.app_name}.exe")
            if os.path.exists(exe_path):
                size = os.path.getsize(exe_path) / (1024 * 1024)
                print(f"✅ Windows构建完成: {exe_path} ({size:.1f} MB)")
                return True
            else:
                print("❌ Windows构建失败: 可执行文件未生成")
                return False
                
        except subprocess.CalledProcessError as e:
            print(f"❌ Windows构建失败: {e}")
            return False
    
    def build_macos(self):
        """构建macOS应用程序包"""
        print("🍎 构建macOS应用程序包...")

        icon_path = self.icon_files["Darwin"]

        # 确保ICNS图标存在
        if not os.path.exists(icon_path):
            print(f"❌ macOS图标文件不存在: {icon_path}")
            return False

        # 获取绝对路径
        icon_abs_path = os.path.abspath(icon_path)
        script_abs_path = os.path.abspath(self.script_name)

        # 构建基础命令
        cmd = [
            sys.executable, "-m", "PyInstaller",
            "--onefile",
            "--windowed",
            "--name", self.app_name,
            "--distpath", self.build_dir,
            "--workpath", self.work_dir,
            "--specpath", self.spec_dir,
            "--clean",
            "--icon", icon_abs_path
        ]

        # 添加数据文件
        for data_file in self.get_data_files():
            cmd.extend(["--add-data", data_file])

        # 添加隐藏导入
        cmd.extend(self.get_hidden_imports())

        # 添加主脚本
        cmd.append(script_abs_path)
        
        try:
            subprocess.run(cmd, check=True)
            
            # 复制图标到输出目录
            if os.path.exists(self.icon_files["Darwin"]):
                shutil.copy2(self.icon_files["Darwin"], 
                           os.path.join(self.build_dir, self.icon_files["Darwin"]))
            
            app_path = os.path.join(self.build_dir, f"{self.app_name}")
            if os.path.exists(app_path):
                size = os.path.getsize(app_path) / (1024 * 1024)
                print(f"✅ macOS构建完成: {app_path} ({size:.1f} MB)")
                
                # 创建DMG文件（如果可能）
                self.create_dmg()
                return True
            else:
                print("❌ macOS构建失败: 应用程序未生成")
                return False
                
        except subprocess.CalledProcessError as e:
            print(f"❌ macOS构建失败: {e}")
            return False
    
    def build_linux(self):
        """构建Linux可执行文件"""
        print("🐧 构建Linux可执行文件...")

        icon_path = self.icon_files["Linux"]

        # 确保图标文件存在
        if not os.path.exists(icon_path):
            print(f"❌ Linux图标文件不存在: {icon_path}")
            return False

        # 获取绝对路径
        script_abs_path = os.path.abspath(self.script_name)

        # 构建基础命令
        cmd = [
            sys.executable, "-m", "PyInstaller",
            "--onefile",
            "--name", self.app_name,
            "--distpath", self.build_dir,
            "--workpath", self.work_dir,
            "--specpath", self.spec_dir,
            "--clean"
        ]

        # 添加数据文件
        for data_file in self.get_data_files():
            cmd.extend(["--add-data", data_file])

        # 添加隐藏导入
        cmd.extend(self.get_hidden_imports())

        # 添加主脚本
        cmd.append(script_abs_path)
        
        try:
            subprocess.run(cmd, check=True)
            
            # 复制图标到输出目录
            if os.path.exists(icon_path):
                shutil.copy2(icon_path, os.path.join(self.build_dir, icon_path))
            
            app_path = os.path.join(self.build_dir, self.app_name)
            if os.path.exists(app_path):
                # 设置执行权限
                os.chmod(app_path, 0o755)
                size = os.path.getsize(app_path) / (1024 * 1024)
                print(f"✅ Linux构建完成: {app_path} ({size:.1f} MB)")
                return True
            else:
                print("❌ Linux构建失败: 可执行文件未生成")
                return False
                
        except subprocess.CalledProcessError as e:
            print(f"❌ Linux构建失败: {e}")
            return False

    def verify_cross_platform_compatibility(self):
        """验证跨平台兼容性"""
        print("🔍 验证跨平台兼容性...")

        issues = []

        # 检查主要源文件
        required_files = [
            "simple_linken_gui.py",
            "linken_sphere_playwright_browser.py",
            "linken_sphere_api.py"
        ]

        for file_path in required_files:
            if not os.path.exists(file_path):
                issues.append(f"缺少必需文件: {file_path}")

        # 检查GUI兼容性
        try:
            import tkinter as tk
            print("✅ Tkinter GUI支持")
        except ImportError:
            issues.append("Tkinter GUI不可用")

        # 检查异步支持
        try:
            import asyncio
            print("✅ Asyncio异步支持")
        except ImportError:
            issues.append("Asyncio异步不可用")

        # 检查浏览器自动化
        try:
            import playwright
            print("✅ Playwright浏览器自动化")
        except ImportError:
            issues.append("Playwright浏览器自动化不可用")

        # 检查HTTP请求
        try:
            import requests
            print("✅ Requests HTTP库")
        except ImportError:
            issues.append("Requests HTTP库不可用")

        # 检查图像处理
        try:
            from PIL import Image, ImageTk
            print("✅ PIL图像处理")
        except ImportError:
            issues.append("PIL图像处理不可用")

        # 检查平台特定功能
        if self.system == "Darwin":
            # macOS特定检查
            try:
                subprocess.run(["sips", "--version"], capture_output=True, check=True)
                print("✅ macOS sips工具可用")
            except (subprocess.CalledProcessError, FileNotFoundError):
                print("⚠️ macOS sips工具不可用，将使用备用方法")

        # 检查Linken Sphere API端口
        try:
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('127.0.0.1', 36555))
            sock.close()
            if result == 0:
                print("✅ Linken Sphere API端口(36555)可访问")
            else:
                print("⚠️ Linken Sphere API端口(36555)不可访问")
        except Exception:
            print("⚠️ 无法检查Linken Sphere API端口")

        if issues:
            print("\n❌ 发现兼容性问题:")
            for issue in issues:
                print(f"   - {issue}")
            return False
        else:
            print("\n✅ 跨平台兼容性验证通过")
            return True

    def create_dmg(self):
        """创建macOS DMG安装包"""
        try:
            dmg_name = f"{self.app_name}.dmg"
            app_path = os.path.join(self.build_dir, self.app_name)
            
            if os.path.exists(app_path):
                # 使用hdiutil创建DMG
                subprocess.run([
                    "hdiutil", "create", "-volname", self.app_name,
                    "-srcfolder", app_path, "-ov", "-format", "UDZO",
                    os.path.join(self.build_dir, dmg_name)
                ], check=True, capture_output=True)
                
                print(f"✅ 创建DMG安装包: {dmg_name}")
            
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("⚠️ 无法创建DMG安装包")
    
    def create_usage_guide(self):
        """创建使用说明"""
        guide_content = f"""# {self.app_name} 使用说明

## 系统要求
- Linken Sphere 浏览器 (必须安装)
- 稳定的网络连接
- 操作系统: Windows 10+, macOS 10.15+, 或现代Linux发行版

## 使用方法
1. 确保Linken Sphere已安装并运行
2. 双击运行 {self.app_name}
3. 在GUI中配置参数
4. 点击"开始"按钮启动自动化

## 功能特点
✅ Linken Sphere 指纹保护
✅ 多线程并发支持
✅ 实时日志监控
✅ 配置保存/导入/导出
✅ 单独线程控制

## 故障排除
- 确保Linken Sphere正在运行
- 检查网络连接
- 查看日志输出获取详细信息

## 技术支持
如有问题，请查看日志文件或联系技术支持。
"""
        
        guide_path = os.path.join(self.build_dir, "使用说明.txt")
        with open(guide_path, 'w', encoding='utf-8') as f:
            f.write(guide_content)
        
        print(f"✅ 创建使用说明: {guide_path}")
    
    def build(self):
        """执行构建"""
        print(f"🚀 开始构建 {self.app_name} for {self.system}")
        print("=" * 60)

        # 验证跨平台兼容性
        if not self.verify_cross_platform_compatibility():
            print("❌ 跨平台兼容性验证失败")
            return False

        # 检查依赖
        if not self.check_dependencies():
            print("❌ 依赖检查失败")
            return False

        # 确保图标存在
        if not self.ensure_icons():
            print("⚠️ 图标准备失败，继续构建...")

        # 清理旧的构建文件
        if os.path.exists(self.build_dir):
            shutil.rmtree(self.build_dir)
        if os.path.exists("build"):
            shutil.rmtree("build")

        os.makedirs(self.build_dir, exist_ok=True)
        
        # 根据平台构建
        success = False
        if self.system == "Windows":
            success = self.build_windows()
        elif self.system == "Darwin":
            success = self.build_macos()
        elif self.system == "Linux":
            success = self.build_linux()
        else:
            print(f"❌ 不支持的平台: {self.system}")
            return False
        
        if success:
            # 创建使用说明
            self.create_usage_guide()
            
            print("\n🎉 构建完成!")
            print(f"📁 输出目录: {self.build_dir}")
            
            # 列出生成的文件
            if os.path.exists(self.build_dir):
                print("📋 生成的文件:")
                for item in os.listdir(self.build_dir):
                    item_path = os.path.join(self.build_dir, item)
                    if os.path.isfile(item_path):
                        size = os.path.getsize(item_path) / (1024 * 1024)
                        print(f"  - {item} ({size:.1f} MB)")
                    else:
                        print(f"  - {item}/ (目录)")
            
            return True
        else:
            print("❌ 构建失败")
            return False

def main():
    """主函数"""
    builder = CrossPlatformBuilder()
    
    if len(sys.argv) > 1:
        target_platform = sys.argv[1].lower()
        if target_platform in ["windows", "macos", "linux"]:
            # 强制指定平台
            platform_map = {
                "windows": "Windows",
                "macos": "Darwin", 
                "linux": "Linux"
            }
            builder.system = platform_map[target_platform]
            print(f"🎯 强制构建目标: {builder.system}")
    
    return builder.build()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
