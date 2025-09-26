#!/usr/bin/env python3
"""
跨平台可执行文件构建脚本
支持 Windows (.exe) 和 Mac (.app) 打包
"""

import os
import sys
import platform
import subprocess
import shutil
from pathlib import Path

def install_dependencies():
    """安装打包所需的依赖"""
    print("📦 安装打包依赖...")
    
    dependencies = [
        "pyinstaller>=5.0",
        "playwright>=1.40.0",
        "requests>=2.31.0"
    ]
    
    for dep in dependencies:
        print(f"   安装 {dep}...")
        subprocess.run([sys.executable, "-m", "pip", "install", dep], check=True)
    
    # 安装 Playwright 浏览器
    print("   安装 Playwright 浏览器...")
    subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], check=True)

def create_spec_file():
    """创建增强的 PyInstaller 规格文件"""
    current_os = platform.system()

    # 根据平台设置不同的配置
    if current_os == "Windows":
        exe_name = "LinkenSphereAppleBrowser.exe"
        console_mode = "False"  # Windows 使用窗口模式
        icon_file = "icon='app_icon.ico'," if Path("app_icon.ico").exists() else ""
    elif current_os == "Darwin":
        exe_name = "LinkenSphereAppleBrowser"
        console_mode = "True"   # Mac 保持控制台
        icon_file = "icon='app_icon.icns'," if Path("app_icon.icns").exists() else ""
    else:
        exe_name = "LinkenSphereAppleBrowser"
        console_mode = "True"
        icon_file = ""

    spec_content = f'''# -*- mode: python ; coding: utf-8 -*-
# Enhanced PyInstaller spec for cross-platform Linken Sphere Apple Browser

import sys
import os
from pathlib import Path

# 获取 Playwright 浏览器路径
try:
    import playwright
    playwright_path = Path(playwright.__file__).parent
    playwright_data = [(str(playwright_path / "driver"), "playwright/driver")]
except ImportError:
    playwright_data = []
    print("Warning: Playwright not found, browser automation may not work")

block_cipher = None

# 收集所有必要的数据文件
datas = [
    # 配置文件
    ('blocked_urls.py', '.'),
]

# 添加 Playwright 数据（如果可用）
datas.extend(playwright_data)

# 检查并添加可选文件
optional_files = [
    'config.json',
    'settings.ini',
    'app_icon.ico',
    'app_icon.icns',
    'README.md'
]

for file in optional_files:
    if os.path.exists(file):
        datas.append((file, '.'))

# 主程序分析
a = Analysis(
    ['linken_sphere_playwright_browser.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=[
        # Playwright 相关
        'playwright',
        'playwright.async_api',
        'playwright._impl',
        'playwright._impl._api_structures',
        'playwright._impl._connection',
        'playwright._impl._helper',
        'playwright._impl._browser_type',
        'playwright._impl._page',
        'playwright._impl._frame',
        # 网络和异步
        'requests',
        'requests.adapters',
        'requests.auth',
        'requests.cookies',
        'urllib3',
        'asyncio',
        'asyncio.events',
        'asyncio.queues',
        # 标准库
        'json',
        'logging',
        'logging.handlers',
        'random',
        'time',
        'platform',
        'pathlib',
        'threading',
        'multiprocessing',
        # GUI 相关（为后续 GUI 版本准备）
        'tkinter',
        'tkinter.ttk',
        'tkinter.messagebox',
        'tkinter.filedialog',
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[
        # 排除不需要的模块以减小文件大小
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'PIL',
        'cv2',
        'tensorflow',
        'torch',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# 可执行文件配置
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='{exe_name}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console={console_mode},
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    {icon_file}
)

# Mac App Bundle 配置
{"app = BUNDLE(" if current_os == "Darwin" else "# app = BUNDLE("}
{"    exe," if current_os == "Darwin" else "#     exe,"}
{"    name='LinkenSphereAppleBrowser.app'," if current_os == "Darwin" else "#     name='LinkenSphereAppleBrowser.app',"}
{"    icon='app_icon.icns'," if current_os == "Darwin" and Path("app_icon.icns").exists() else "#     icon='app_icon.icns',"}
{"    bundle_identifier='com.linkensphere.applebrowser'," if current_os == "Darwin" else "#     bundle_identifier='com.linkensphere.applebrowser',"}
{"    info_plist={{" if current_os == "Darwin" else "#     info_plist={{"}
{"        'CFBundleShortVersionString': '1.0.0'," if current_os == "Darwin" else "#         'CFBundleShortVersionString': '1.0.0',"}
{"        'CFBundleVersion': '1.0.0'," if current_os == "Darwin" else "#         'CFBundleVersion': '1.0.0',"}
{"        'NSHighResolutionCapable': True," if current_os == "Darwin" else "#         'NSHighResolutionCapable': True,"}
{"    }}," if current_os == "Darwin" else "#     }},"}
{")" if current_os == "Darwin" else "# )"}
'''

    with open('linken_sphere_browser.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)

    print("✅ 创建增强的 PyInstaller 规格文件完成")
    print(f"   目标平台: {current_os}")
    print(f"   可执行文件: {exe_name}")
    print(f"   控制台模式: {console_mode}")

def create_requirements_file():
    """创建 requirements.txt 文件"""
    requirements = """# Linken Sphere Apple Browser 依赖
playwright>=1.40.0
requests>=2.31.0
asyncio-compat>=0.1.2

# 打包依赖
pyinstaller>=5.0
"""
    
    with open('requirements.txt', 'w', encoding='utf-8') as f:
        f.write(requirements)
    
    print("✅ 创建 requirements.txt 完成")

def create_build_scripts():
    """创建构建脚本"""
    current_os = platform.system()
    
    if current_os == "Windows":
        # Windows 批处理脚本
        batch_script = """@echo off
echo 🚀 构建 Linken Sphere Apple Browser (Windows)
echo ================================================

echo 📦 安装依赖...
pip install -r requirements.txt
playwright install chromium

echo 🔨 构建可执行文件...
pyinstaller linken_sphere_browser.spec --clean --noconfirm

echo ✅ 构建完成！
echo 可执行文件位置: dist\\LinkenSphereAppleBrowser.exe
pause
"""
        with open('build_windows.bat', 'w', encoding='utf-8') as f:
            f.write(batch_script)
        
    else:
        # Mac/Linux shell 脚本
        shell_script = """#!/bin/bash
echo "🚀 构建 Linken Sphere Apple Browser (Mac/Linux)"
echo "================================================"

echo "📦 安装依赖..."
pip3 install -r requirements.txt
playwright install chromium

echo "🔨 构建可执行文件..."
pyinstaller linken_sphere_browser.spec --clean --noconfirm

echo "✅ 构建完成！"
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "应用程序位置: dist/LinkenSphereAppleBrowser.app"
else
    echo "可执行文件位置: dist/LinkenSphereAppleBrowser"
fi
"""
        with open('build_mac_linux.sh', 'w', encoding='utf-8') as f:
            f.write(shell_script)
        
        # 添加执行权限
        os.chmod('build_mac_linux.sh', 0o755)
    
    print(f"✅ 创建 {current_os} 构建脚本完成")

def create_readme():
    """创建使用说明"""
    readme_content = """# Linken Sphere Apple Browser 可执行文件

## 📋 系统要求

### Windows
- Windows 10/11 (64位)
- 至少 4GB RAM
- 2GB 可用磁盘空间

### Mac
- macOS 10.15+ (Catalina 或更新版本)
- 至少 4GB RAM
- 2GB 可用磁盘空间

## 🚀 使用方法

### Windows
1. 双击 `LinkenSphereAppleBrowser.exe`
2. 确保 Linken Sphere 正在运行
3. 程序会自动开始浏览流程

### Mac
1. 双击 `LinkenSphereAppleBrowser.app`
2. 如果出现安全警告，请在"系统偏好设置 > 安全性与隐私"中允许运行
3. 确保 Linken Sphere 正在运行
4. 程序会自动开始浏览流程

## ⚙️ 配置要求

### Linken Sphere 设置
1. **启动 Linken Sphere**
2. **创建配置文件**（如果没有的话）
3. **启用 API 功能**：
   - 检查端口 36555 是否可用
   - 确保远程调试端口已启用
4. **启动浏览器会话**

### 网络要求
- 稳定的互联网连接
- 能够访问 apple.com/jp

## 🔧 故障排除

### 常见问题

#### 1. "无法连接到 Linken Sphere"
**解决方案**：
- 确保 Linken Sphere 正在运行
- 检查 API 端口 36555 是否开放
- 重启 Linken Sphere 并重新启动浏览器会话

#### 2. "无法连接到调试端口"
**解决方案**：
- 在 Linken Sphere 中启用远程调试
- 检查防火墙设置
- 尝试重新启动浏览器会话

#### 3. Mac 安全警告
**解决方案**：
- 右键点击应用程序，选择"打开"
- 或在"系统偏好设置 > 安全性与隐私"中允许运行

### 日志文件
程序运行时会生成日志文件：
- `linken_sphere_browser_log.txt` - 详细运行日志

## 📊 程序功能

- **双层循环浏览**：3大循环 × 8小循环 = 24页
- **智能重试机制**：网络错误自动重试
- **指纹保护**：使用 Linken Sphere 的指纹保护功能
- **详细日志**：完整的操作记录

## 🆘 技术支持

如果遇到问题，请检查日志文件并提供以下信息：
1. 操作系统版本
2. Linken Sphere 版本
3. 错误信息
4. 日志文件内容
"""
    
    with open('README.md', 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print("✅ 创建使用说明完成")

def build_executable():
    """构建可执行文件"""
    print("🔨 开始构建可执行文件...")

    try:
        # 运行 PyInstaller
        subprocess.run([
            sys.executable, "-m", "PyInstaller",
            "linken_sphere_browser.spec",
            "--clean",
            "--noconfirm"
        ], check=True)

        current_os = platform.system()
        if current_os == "Windows":
            exe_path = "dist/LinkenSphereAppleBrowser.exe"
        elif current_os == "Darwin":
            exe_path = "dist/LinkenSphereAppleBrowser.app"
        else:
            exe_path = "dist/LinkenSphereAppleBrowser"

        if os.path.exists(exe_path):
            print(f"✅ 构建成功！可执行文件位置: {exe_path}")

            # 获取文件大小
            if current_os == "Darwin":
                # Mac App Bundle
                size = sum(os.path.getsize(os.path.join(dirpath, filename))
                          for dirpath, dirnames, filenames in os.walk(exe_path)
                          for filename in filenames)
            else:
                size = os.path.getsize(exe_path)

            size_mb = size / (1024 * 1024)
            print(f"📦 文件大小: {size_mb:.1f} MB")

            # 平台特定的后处理
            if current_os == "Darwin":
                post_process_macos(exe_path)
            elif current_os == "Windows":
                post_process_windows(exe_path)

        else:
            print("❌ 构建失败：找不到可执行文件")

    except subprocess.CalledProcessError as e:
        print(f"❌ 构建失败: {e}")

def post_process_macos(app_path):
    """Mac 后处理：代码签名和公证"""
    print("\n🍎 Mac 后处理...")

    # 检查是否有代码签名证书
    try:
        result = subprocess.run(
            ["security", "find-identity", "-v", "-p", "codesigning"],
            capture_output=True, text=True
        )

        if "Developer ID Application" in result.stdout:
            print("✅ 发现开发者证书，开始代码签名...")

            # 代码签名
            subprocess.run([
                "codesign", "--force", "--verify", "--verbose", "--sign",
                "Developer ID Application", app_path
            ], check=True)

            print("✅ 代码签名完成")

            # 创建 DMG
            create_dmg(app_path)

        else:
            print("⚠️ 未找到开发者证书，跳过代码签名")
            print("💡 要进行代码签名，请：")
            print("   1. 注册 Apple Developer Program")
            print("   2. 下载并安装开发者证书")
            print("   3. 重新运行构建脚本")

    except subprocess.CalledProcessError as e:
        print(f"⚠️ 代码签名失败: {e}")
    except FileNotFoundError:
        print("⚠️ 未找到 codesign 工具")

def create_dmg(app_path):
    """创建 DMG 安装包"""
    print("📦 创建 DMG 安装包...")

    dmg_name = "LinkenSphereAppleBrowser-1.0.0.dmg"

    try:
        # 创建临时目录
        temp_dir = "temp_dmg"
        os.makedirs(temp_dir, exist_ok=True)

        # 复制应用到临时目录
        subprocess.run(["cp", "-R", app_path, temp_dir], check=True)

        # 创建 DMG
        subprocess.run([
            "hdiutil", "create", "-volname", "Linken Sphere Apple Browser",
            "-srcfolder", temp_dir, "-ov", "-format", "UDZO", dmg_name
        ], check=True)

        # 清理临时目录
        subprocess.run(["rm", "-rf", temp_dir], check=True)

        print(f"✅ DMG 创建完成: {dmg_name}")

    except subprocess.CalledProcessError as e:
        print(f"❌ DMG 创建失败: {e}")

def post_process_windows(exe_path):
    """Windows 后处理"""
    print("\n🪟 Windows 后处理...")

    # 检查文件属性
    try:
        import win32api
        info = win32api.GetFileVersionInfo(exe_path, "\\")
        print(f"✅ 可执行文件验证通过")

        # 创建安装包（如果有 NSIS）
        create_windows_installer(exe_path)

    except ImportError:
        print("⚠️ 未安装 pywin32，跳过文件验证")
    except Exception as e:
        print(f"⚠️ 文件验证失败: {e}")

def create_windows_installer(exe_path):
    """创建 Windows 安装包"""
    print("📦 检查 NSIS 安装包工具...")

    # 检查是否有 NSIS
    nsis_paths = [
        "C:\\Program Files (x86)\\NSIS\\makensis.exe",
        "C:\\Program Files\\NSIS\\makensis.exe"
    ]

    nsis_exe = None
    for path in nsis_paths:
        if os.path.exists(path):
            nsis_exe = path
            break

    if nsis_exe:
        print("✅ 发现 NSIS，可以创建安装包")
        print("💡 要创建安装包，请运行 create_installer.nsi 脚本")
    else:
        print("⚠️ 未找到 NSIS，无法创建安装包")
        print("💡 要创建安装包，请：")
        print("   1. 下载并安装 NSIS (https://nsis.sourceforge.io/)")
        print("   2. 重新运行构建脚本")

def main():
    """主函数"""
    print("🚀 Linken Sphere Apple Browser 可执行文件构建工具")
    print("=" * 60)
    print(f"当前系统: {platform.system()} {platform.machine()}")
    print("=" * 60)
    
    # 检查必要文件
    if not os.path.exists('linken_sphere_playwright_browser.py'):
        print("❌ 找不到主程序文件: linken_sphere_playwright_browser.py")
        return
    
    try:
        # 1. 安装依赖
        install_dependencies()
        
        # 2. 创建配置文件
        create_spec_file()
        create_requirements_file()
        create_build_scripts()
        create_readme()
        
        # 3. 构建可执行文件
        build_executable()
        
        print("\n🎉 所有任务完成！")
        print("=" * 60)
        print("📁 生成的文件:")
        print("   - dist/ (可执行文件目录)")
        print("   - requirements.txt (依赖列表)")
        print("   - README.md (使用说明)")
        print("   - build_*.bat/.sh (构建脚本)")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ 构建过程出错: {e}")

if __name__ == "__main__":
    main()
