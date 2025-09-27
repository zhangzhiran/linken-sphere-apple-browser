#!/usr/bin/env python3
"""
创建macOS分发包
生成可直接分发给用户的macOS应用程序
"""

import os
import sys
import platform
import subprocess
import shutil
import json
from pathlib import Path

class MacOSDistributionBuilder:
    def __init__(self):
        self.app_name = "LinkenSphereAppleBrowser"
        self.script_name = "simple_linken_gui.py"
        self.build_dir = "dist"
        self.distribution_dir = "macOS_Distribution"
        
        print("🍎 macOS分发包构建器")
        print("=" * 50)

    def check_environment(self):
        """检查构建环境"""
        print("🔍 检查构建环境...")
        
        # 检查必需文件
        required_files = [
            self.script_name,
            "linken_sphere_playwright_browser.py",
            "linken_sphere_api.py"
        ]
        
        missing_files = []
        for file in required_files:
            if not os.path.exists(file):
                missing_files.append(file)
            else:
                print(f"✅ {file}")
        
        if missing_files:
            print("❌ 缺少必需文件:")
            for file in missing_files:
                print(f"   - {file}")
            return False
        
        # 检查PyInstaller
        try:
            import PyInstaller
            print(f"✅ PyInstaller {PyInstaller.__version__}")
        except ImportError:
            print("❌ PyInstaller未安装")
            print("请运行: pip install PyInstaller")
            return False
        
        return True

    def create_standalone_executable(self):
        """创建独立可执行文件"""
        print("🔨 创建独立可执行文件...")
        
        # 清理旧构建
        if os.path.exists(self.build_dir):
            shutil.rmtree(self.build_dir)
        if os.path.exists("build"):
            shutil.rmtree("build")
        
        # 准备图标
        icon_path = None
        if os.path.exists("app_icon.icns"):
            icon_path = "app_icon.icns"
        elif os.path.exists("app_icon.png"):
            # 尝试创建ICNS
            try:
                if platform.system() == "Darwin":
                    subprocess.run([
                        "sips", "-s", "format", "icns",
                        "app_icon.png", "--out", "app_icon.icns"
                    ], check=True, capture_output=True)
                    icon_path = "app_icon.icns"
                    print("✅ 从PNG创建ICNS图标")
                else:
                    icon_path = "app_icon.png"
            except:
                icon_path = "app_icon.png" if os.path.exists("app_icon.png") else None
        
        # 构建命令
        cmd = [
            sys.executable, "-m", "PyInstaller",
            "--onefile",
            "--windowed",
            "--name", self.app_name,
            "--distpath", self.build_dir,
            "--clean"
        ]
        
        # 添加图标
        if icon_path:
            cmd.extend(["--icon", icon_path])
            print(f"📱 使用图标: {icon_path}")
        
        # macOS特定选项
        if platform.system() == "Darwin":
            cmd.extend([
                "--osx-bundle-identifier", f"com.linkensphere.{self.app_name.lower()}",
                "--target-arch", "universal2"  # 支持Intel和Apple Silicon
            ])
        
        # 添加数据文件
        data_files = [
            "linken_sphere_playwright_browser.py",
            "linken_sphere_api.py"
        ]
        
        for data_file in data_files:
            if os.path.exists(data_file):
                cmd.extend(["--add-data", f"{data_file}:."])
        
        # 添加配置文件
        config_files = [
            "linken_sphere_config.json",
            "config.json"
        ]
        
        for config_file in config_files:
            if os.path.exists(config_file):
                cmd.extend(["--add-data", f"{config_file}:."])
        
        # 添加隐藏导入
        hidden_imports = [
            "asyncio", "tkinter", "tkinter.ttk", "tkinter.messagebox",
            "tkinter.filedialog", "requests", "json", "threading",
            "pathlib", "urllib.parse", "urllib.request", "ssl",
            "socket", "time", "datetime", "logging", "os", "sys"
        ]
        
        for module in hidden_imports:
            cmd.extend(["--hidden-import", module])
        
        # 添加主脚本
        cmd.append(self.script_name)
        
        try:
            print("⏳ 正在构建，请稍候...")
            subprocess.run(cmd, check=True)
            print("✅ 可执行文件构建完成")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ 构建失败: {e}")
            return False

    def create_distribution_package(self):
        """创建分发包"""
        print("📦 创建分发包...")
        
        # 创建分发目录
        if os.path.exists(self.distribution_dir):
            shutil.rmtree(self.distribution_dir)
        os.makedirs(self.distribution_dir)
        
        # 查找构建的应用
        app_bundle = os.path.join(self.build_dir, f"{self.app_name}.app")
        app_executable = os.path.join(self.build_dir, self.app_name)
        
        if os.path.exists(app_bundle):
            # 复制应用包
            dest_app = os.path.join(self.distribution_dir, f"{self.app_name}.app")
            shutil.copytree(app_bundle, dest_app)
            
            # 设置权限
            executable_path = os.path.join(dest_app, "Contents", "MacOS", self.app_name)
            if os.path.exists(executable_path):
                os.chmod(executable_path, 0o755)
            
            print(f"✅ 应用包已复制: {dest_app}")
            main_app = dest_app
            
        elif os.path.exists(app_executable):
            # 复制可执行文件
            dest_executable = os.path.join(self.distribution_dir, self.app_name)
            shutil.copy2(app_executable, dest_executable)
            os.chmod(dest_executable, 0o755)
            
            print(f"✅ 可执行文件已复制: {dest_executable}")
            main_app = dest_executable
        else:
            print("❌ 未找到构建的应用")
            return False
        
        # 复制图标文件
        for icon_file in ["app_icon.icns", "app_icon.png", "app_icon.ico"]:
            if os.path.exists(icon_file):
                shutil.copy2(icon_file, self.distribution_dir)
                print(f"📱 复制图标: {icon_file}")
        
        # 复制配置文件
        for config_file in ["linken_sphere_config.json", "config.json"]:
            if os.path.exists(config_file):
                shutil.copy2(config_file, self.distribution_dir)
                print(f"⚙️ 复制配置: {config_file}")
        
        return main_app

    def create_installer_script(self):
        """创建安装脚本"""
        installer_script = f"""#!/bin/bash
# {self.app_name} macOS安装脚本

echo "🍎 {self.app_name} 安装程序"
echo "================================"

# 检查系统
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "❌ 此应用只能在macOS系统上运行"
    exit 1
fi

echo "✅ 检测到macOS系统: $(sw_vers -productVersion)"

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${{BASH_SOURCE[0]}}" )" &> /dev/null && pwd )"

# 检查应用文件
if [[ -d "$SCRIPT_DIR/{self.app_name}.app" ]]; then
    APP_PATH="$SCRIPT_DIR/{self.app_name}.app"
    echo "✅ 找到应用包: {self.app_name}.app"
elif [[ -f "$SCRIPT_DIR/{self.app_name}" ]]; then
    APP_PATH="$SCRIPT_DIR/{self.app_name}"
    echo "✅ 找到可执行文件: {self.app_name}"
else
    echo "❌ 未找到应用文件"
    exit 1
fi

# 询问安装位置
echo ""
echo "选择安装方式:"
echo "1) 安装到Applications文件夹 (推荐)"
echo "2) 在当前位置运行"
echo "3) 退出"
echo ""
read -p "请选择 (1-3): " choice

case $choice in
    1)
        echo "📁 安装到Applications文件夹..."
        if [[ -d "$APP_PATH" ]]; then
            cp -R "$APP_PATH" "/Applications/"
            echo "✅ 安装完成: /Applications/{self.app_name}.app"
            echo "🚀 可以从Launchpad或Applications文件夹启动"
        else
            cp "$APP_PATH" "/Applications/"
            echo "✅ 安装完成: /Applications/{self.app_name}"
            echo "🚀 可以从Applications文件夹启动"
        fi
        ;;
    2)
        echo "🚀 启动应用..."
        if [[ -d "$APP_PATH" ]]; then
            open "$APP_PATH"
        else
            "$APP_PATH"
        fi
        ;;
    3)
        echo "👋 安装已取消"
        exit 0
        ;;
    *)
        echo "❌ 无效选择"
        exit 1
        ;;
esac
"""
        
        installer_path = os.path.join(self.distribution_dir, "install.sh")
        with open(installer_path, 'w', encoding='utf-8') as f:
            f.write(installer_script)
        
        os.chmod(installer_path, 0o755)
        print(f"📋 创建安装脚本: install.sh")

    def create_readme(self):
        """创建说明文件"""
        readme_content = f"""# {self.app_name} - macOS版本

## 📋 系统要求
- macOS 10.14 或更高版本
- 支持Intel和Apple Silicon处理器

## 🚀 安装方法

### 方法1: 使用安装脚本 (推荐)
1. 双击 `install.sh` 或在终端中运行: `./install.sh`
2. 选择安装到Applications文件夹
3. 从Launchpad或Applications文件夹启动

### 方法2: 手动安装
1. 将 `{self.app_name}.app` 拖拽到Applications文件夹
2. 从Launchpad启动应用

### 方法3: 直接运行
- 双击应用文件直接运行

## 🔧 故障排除

### 无法打开应用
如果遇到"无法打开，因为它来自身份不明的开发者"错误：

1. **方法1**: 右键点击应用，选择"打开"，然后点击"打开"
2. **方法2**: 系统偏好设置 > 安全性与隐私 > 通用 > 点击"仍要打开"
3. **方法3**: 在终端中运行:
   ```bash
   xattr -cr {self.app_name}.app
   ```

### 权限问题
如果应用无法启动，请在终端中运行:
```bash
chmod +x {self.app_name}
# 或
chmod +x {self.app_name}.app/Contents/MacOS/{self.app_name}
```

## 📞 支持
如果遇到问题，请检查:
1. 系统版本是否符合要求
2. 是否有足够的磁盘空间
3. 网络连接是否正常

## 📁 文件说明
- `{self.app_name}.app` - 主应用程序
- `install.sh` - 安装脚本
- `README.txt` - 本说明文件
- `app_icon.*` - 应用图标文件
- `*.json` - 配置文件

构建时间: {subprocess.run(['date'], capture_output=True, text=True).stdout.strip() if platform.system() == 'Darwin' else 'Unknown'}
"""
        
        readme_path = os.path.join(self.distribution_dir, "README.txt")
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        print(f"📖 创建说明文件: README.txt")

    def create_dmg(self):
        """创建DMG安装包"""
        if platform.system() != "Darwin":
            print("⚠️ DMG创建需要在macOS上运行")
            return False
        
        print("💿 创建DMG安装包...")
        
        dmg_path = f"{self.app_name}_macOS.dmg"
        
        # 删除已存在的DMG
        if os.path.exists(dmg_path):
            os.remove(dmg_path)
        
        try:
            cmd = [
                "hdiutil", "create",
                "-volname", f"{self.app_name} Installer",
                "-srcfolder", self.distribution_dir,
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

    def build_distribution(self):
        """构建完整分发包"""
        print("🚀 开始构建macOS分发包")
        print("=" * 50)
        
        # 检查环境
        if not self.check_environment():
            return False
        
        # 创建可执行文件
        if not self.create_standalone_executable():
            return False
        
        # 创建分发包
        main_app = self.create_distribution_package()
        if not main_app:
            return False
        
        # 创建安装脚本
        self.create_installer_script()
        
        # 创建说明文件
        self.create_readme()
        
        # 创建DMG（如果在macOS上）
        if platform.system() == "Darwin":
            self.create_dmg()
        
        print("\n🎉 分发包创建完成!")
        print(f"📁 分发目录: {self.distribution_dir}/")
        
        # 显示文件列表
        if os.path.exists(self.distribution_dir):
            print("\n📋 分发包内容:")
            for item in sorted(os.listdir(self.distribution_dir)):
                item_path = os.path.join(self.distribution_dir, item)
                if os.path.isfile(item_path):
                    size = os.path.getsize(item_path) / (1024 * 1024)
                    print(f"  📄 {item} ({size:.1f} MB)")
                elif os.path.isdir(item_path):
                    print(f"  📁 {item}/")
        
        # 显示DMG文件
        dmg_file = f"{self.app_name}_macOS.dmg"
        if os.path.exists(dmg_file):
            size = os.path.getsize(dmg_file) / (1024 * 1024)
            print(f"\n💿 DMG安装包: {dmg_file} ({size:.1f} MB)")
        
        print("\n📤 分发说明:")
        print(f"1. 将整个 '{self.distribution_dir}' 文件夹打包发送给用户")
        if os.path.exists(dmg_file):
            print(f"2. 或者直接发送 '{dmg_file}' DMG文件")
        print("3. 用户双击 install.sh 即可安装")
        
        return True

def main():
    """主函数"""
    builder = MacOSDistributionBuilder()
    success = builder.build_distribution()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
