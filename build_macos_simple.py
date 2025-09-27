#!/usr/bin/env python3
"""
简化的macOS构建脚本
专门用于在macOS系统上构建应用程序
"""

import os
import sys
import platform
import subprocess
import shutil
from pathlib import Path

class MacOSBuilder:
    def __init__(self):
        self.app_name = "LinkenSphereAppleBrowser"
        self.script_name = "simple_linken_gui.py"
        self.build_dir = "dist"
        self.work_dir = "build"
        
        # 检查是否在macOS上运行
        if platform.system() != "Darwin":
            print("❌ 此脚本只能在macOS系统上运行")
            sys.exit(1)
        
        print(f"🍎 macOS构建器初始化完成")
        print(f"系统版本: {platform.mac_ver()[0]}")
        print(f"系统架构: {platform.machine()}")

    def check_dependencies(self):
        """检查构建依赖"""
        print("🔍 检查构建依赖...")
        
        # 检查Python
        if sys.version_info < (3, 8):
            print("❌ 需要Python 3.8或更高版本")
            return False
        print(f"✅ Python {sys.version.split()[0]}")
        
        # 检查PyInstaller
        try:
            import PyInstaller
            print(f"✅ PyInstaller {PyInstaller.__version__}")
        except ImportError:
            print("❌ PyInstaller未安装")
            print("请运行: pip install PyInstaller")
            return False
        
        # 检查必需文件
        required_files = [
            self.script_name,
            "linken_sphere_playwright_browser.py",
            "linken_sphere_api.py"
        ]
        
        for file in required_files:
            if not os.path.exists(file):
                print(f"❌ 缺少必需文件: {file}")
                return False
            print(f"✅ {file}")
        
        return True

    def prepare_icon(self):
        """准备应用图标"""
        print("🎨 准备应用图标...")
        
        # 优先使用ICNS图标
        if os.path.exists("app_icon.icns"):
            print("✅ 找到ICNS图标")
            return "app_icon.icns"
        
        # 尝试从PNG创建ICNS
        if os.path.exists("app_icon.png"):
            print("🔄 从PNG创建ICNS图标...")
            try:
                cmd = [
                    "sips", "-s", "format", "icns",
                    "app_icon.png", "--out", "app_icon.icns"
                ]
                subprocess.run(cmd, check=True, capture_output=True)
                print("✅ ICNS图标创建成功")
                return "app_icon.icns"
            except subprocess.CalledProcessError:
                print("⚠️ ICNS创建失败，使用PNG图标")
                return "app_icon.png"
        
        print("⚠️ 未找到图标文件")
        return None

    def build_app(self):
        """构建应用程序"""
        print("🔨 开始构建应用程序...")
        
        # 清理旧构建
        if os.path.exists(self.build_dir):
            shutil.rmtree(self.build_dir)
        if os.path.exists(self.work_dir):
            shutil.rmtree(self.work_dir)
        
        # 准备图标
        icon_path = self.prepare_icon()
        
        # 构建命令
        cmd = [
            sys.executable, "-m", "PyInstaller",
            "--onefile",
            "--windowed",
            "--name", self.app_name,
            "--distpath", self.build_dir,
            "--workpath", self.work_dir,
            "--clean",
            "--osx-bundle-identifier", f"com.linkensphere.{self.app_name.lower()}",
            "--target-arch", "universal2"  # 支持Intel和Apple Silicon
        ]
        
        # 添加图标
        if icon_path:
            cmd.extend(["--icon", icon_path])
        
        # 添加数据文件
        data_files = [
            "linken_sphere_playwright_browser.py",
            "linken_sphere_api.py"
        ]
        
        for data_file in data_files:
            if os.path.exists(data_file):
                cmd.extend(["--add-data", f"{data_file}:."])
        
        # 添加配置文件（如果存在）
        config_files = [
            "linken_sphere_config.json",
            "config.json"
        ]
        
        for config_file in config_files:
            if os.path.exists(config_file):
                cmd.extend(["--add-data", f"{config_file}:."])
                print(f"📋 添加配置文件: {config_file}")
        
        # 添加隐藏导入
        hidden_imports = [
            "asyncio",
            "tkinter",
            "tkinter.ttk",
            "tkinter.messagebox",
            "tkinter.filedialog",
            "requests",
            "json",
            "threading",
            "pathlib"
        ]
        
        for module in hidden_imports:
            cmd.extend(["--hidden-import", module])
        
        # 添加主脚本
        cmd.append(self.script_name)
        
        try:
            print("⏳ 正在构建，请稍候...")
            subprocess.run(cmd, check=True)
            print("✅ PyInstaller构建完成")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ 构建失败: {e}")
            return False

    def post_build_setup(self):
        """构建后设置"""
        print("🔧 进行构建后设置...")
        
        # 查找生成的应用
        app_bundle = os.path.join(self.build_dir, f"{self.app_name}.app")
        app_executable = os.path.join(self.build_dir, self.app_name)
        
        if os.path.exists(app_bundle):
            print(f"✅ 找到应用包: {app_bundle}")
            
            # 设置可执行权限
            executable_path = os.path.join(app_bundle, "Contents", "MacOS", self.app_name)
            if os.path.exists(executable_path):
                os.chmod(executable_path, 0o755)
                print("✅ 设置可执行权限")
            
            # 获取大小
            size = self.get_directory_size(app_bundle) / (1024 * 1024)
            print(f"📦 应用包大小: {size:.1f} MB")
            
            return app_bundle
            
        elif os.path.exists(app_executable):
            print(f"✅ 找到可执行文件: {app_executable}")
            
            # 设置可执行权限
            os.chmod(app_executable, 0o755)
            print("✅ 设置可执行权限")
            
            # 获取大小
            size = os.path.getsize(app_executable) / (1024 * 1024)
            print(f"📦 可执行文件大小: {size:.1f} MB")
            
            return app_executable
        else:
            print("❌ 未找到构建输出")
            return None

    def create_dmg(self, app_path):
        """创建DMG安装包"""
        print("📀 创建DMG安装包...")
        
        dmg_path = os.path.join(self.build_dir, f"{self.app_name}.dmg")
        
        # 删除已存在的DMG
        if os.path.exists(dmg_path):
            os.remove(dmg_path)
        
        try:
            cmd = [
                "hdiutil", "create",
                "-volname", self.app_name,
                "-srcfolder", app_path,
                "-ov", "-format", "UDZO",
                dmg_path
            ]
            
            subprocess.run(cmd, check=True, capture_output=True)
            
            if os.path.exists(dmg_path):
                size = os.path.getsize(dmg_path) / (1024 * 1024)
                print(f"✅ DMG创建成功: {dmg_path} ({size:.1f} MB)")
                return True
            else:
                print("❌ DMG创建失败")
                return False
                
        except subprocess.CalledProcessError as e:
            print(f"⚠️ DMG创建失败: {e}")
            return False

    def get_directory_size(self, path):
        """获取目录大小"""
        total_size = 0
        for dirpath, _, filenames in os.walk(path):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                if os.path.exists(filepath):
                    total_size += os.path.getsize(filepath)
        return total_size

    def create_usage_guide(self):
        """创建使用说明"""
        guide_content = f"""# {self.app_name} - macOS版本使用说明

## 安装方法
1. 如果有DMG文件，双击打开并将应用拖拽到Applications文件夹
2. 如果是应用包(.app)，直接双击运行或移动到Applications文件夹
3. 如果是可执行文件，在终端中运行: ./{self.app_name}

## 运行方法
- 从Launchpad启动
- 从Applications文件夹启动
- 在终端中运行

## 故障排除
如果遇到"无法打开，因为它来自身份不明的开发者"错误：
1. 右键点击应用，选择"打开"
2. 或在系统偏好设置 > 安全性与隐私中允许运行

## 系统要求
- macOS 10.14或更高版本
- 支持Intel和Apple Silicon处理器

构建时间: {subprocess.run(['date'], capture_output=True, text=True).stdout.strip()}
构建系统: {platform.platform()}
"""
        
        guide_path = os.path.join(self.build_dir, "使用说明.txt")
        with open(guide_path, 'w', encoding='utf-8') as f:
            f.write(guide_content)
        
        print(f"📋 创建使用说明: {guide_path}")

    def build(self):
        """执行完整构建流程"""
        print("🚀 开始macOS应用构建")
        print("=" * 50)
        
        # 检查依赖
        if not self.check_dependencies():
            return False
        
        # 构建应用
        if not self.build_app():
            return False
        
        # 构建后设置
        app_path = self.post_build_setup()
        if not app_path:
            return False
        
        # 创建DMG（可选）
        self.create_dmg(app_path)
        
        # 创建使用说明
        self.create_usage_guide()
        
        print("\n🎉 构建完成!")
        print(f"📁 输出目录: {self.build_dir}")
        
        # 列出生成的文件
        if os.path.exists(self.build_dir):
            print("📋 生成的文件:")
            for item in sorted(os.listdir(self.build_dir)):
                item_path = os.path.join(self.build_dir, item)
                if os.path.isfile(item_path):
                    size = os.path.getsize(item_path) / (1024 * 1024)
                    print(f"  📄 {item} ({size:.1f} MB)")
                elif os.path.isdir(item_path):
                    size = self.get_directory_size(item_path) / (1024 * 1024)
                    print(f"  📁 {item}/ ({size:.1f} MB)")
        
        return True

def main():
    """主函数"""
    builder = MacOSBuilder()
    success = builder.build()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
