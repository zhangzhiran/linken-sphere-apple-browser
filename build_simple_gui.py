#!/usr/bin/env python3
"""
简化版GUI的构建脚本
创建紧凑、易用的可执行文件
"""

import os
import sys
import platform
import subprocess
from pathlib import Path

def check_dependencies():
    """检查依赖"""
    print("🔍 检查依赖...")

    # 检查 PyInstaller
    try:
        result = subprocess.run([sys.executable, "-m", "PyInstaller", "--version"],
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ pyinstaller")
        else:
            print("❌ pyinstaller")
            return False
    except:
        print("❌ pyinstaller")
        return False

    # 检查其他包
    required_packages = ['playwright', 'requests']
    missing_packages = []

    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package}")

    if missing_packages:
        print(f"\n⚠️ 缺少依赖: {', '.join(missing_packages)}")
        print("请运行: pip install " + " ".join(missing_packages))
        return False

    return True

def create_simple_spec():
    """创建简化版规格文件"""
    print("📝 创建规格文件...")
    
    current_os = platform.system()
    
    if current_os == "Windows":
        exe_name = "LinkenSphereAppleBrowser.exe"
        console_mode = "False"  # Windows使用窗口模式
    else:
        exe_name = "LinkenSphereAppleBrowser"
        console_mode = "True"   # Mac/Linux保持控制台
    
    spec_content = f'''# -*- mode: python ; coding: utf-8 -*-
# 简化版 Linken Sphere Apple Browser 构建规格

import sys
import os
from pathlib import Path

# 获取 Playwright 路径
try:
    import playwright
    playwright_path = Path(playwright.__file__).parent
    playwright_data = [(str(playwright_path / "driver"), "playwright/driver")]
except ImportError:
    playwright_data = []

block_cipher = None

# 数据文件
datas = [
    ('blocked_urls.py', '.'),
    ('simple_linken_gui.py', '.'),
    ('linken_sphere_playwright_browser.py', '.'),
]

# 添加 Playwright 数据
datas.extend(playwright_data)

# 检查配置文件
if os.path.exists('linken_sphere_config.json'):
    datas.append(('linken_sphere_config.json', '.'))

a = Analysis(
    ['simple_linken_gui.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=[
        'playwright',
        'playwright.async_api',
        'playwright._impl',
        'playwright._impl._api_structures',
        'playwright._impl._connection',
        'playwright._impl._helper',
        'requests',
        'asyncio',
        'json',
        'threading',
        'tkinter',
        'tkinter.ttk',
        'tkinter.messagebox',
        'tkinter.scrolledtext',
        'tkinter.filedialog',
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'PIL',
        'cv2',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

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
)
'''
    
    with open('simple_gui.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print("✅ 规格文件创建完成")

def build_executable():
    """构建可执行文件"""
    print("🔨 开始构建...")
    
    try:
        # 清理旧文件
        if os.path.exists('dist'):
            import shutil
            shutil.rmtree('dist')
        if os.path.exists('build'):
            import shutil
            shutil.rmtree('build')
        
        # 运行 PyInstaller
        cmd = [sys.executable, "-m", "PyInstaller", "simple_gui.spec", "--clean", "--noconfirm"]
        
        print("📦 运行 PyInstaller...")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ 构建成功！")
            
            # 检查输出文件
            current_os = platform.system()
            if current_os == "Windows":
                exe_path = "dist/LinkenSphereAppleBrowser.exe"
            else:
                exe_path = "dist/LinkenSphereAppleBrowser"
            
            if os.path.exists(exe_path):
                size = os.path.getsize(exe_path)
                size_mb = size / (1024 * 1024)
                print(f"📦 文件: {exe_path}")
                print(f"📏 大小: {size_mb:.1f} MB")
                
                # 创建使用说明
                create_usage_guide()
                
                return True
            else:
                print("❌ 找不到输出文件")
                return False
        else:
            print("❌ 构建失败:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ 构建异常: {e}")
        return False

def create_usage_guide():
    """创建使用说明"""
    print("📖 创建使用说明...")
    
    guide_content = """# Linken Sphere Apple Browser 使用说明

## 🚀 快速开始

1. **启动程序**
   - Windows: 双击 `LinkenSphereAppleBrowser.exe`
   - Mac/Linux: 运行 `./LinkenSphereAppleBrowser`

2. **配置参数**
   - 浏览时长: 每页停留时间（默认60秒）
   - 大循环: 主循环次数（默认3次）
   - 小循环: 每个大循环的页面数（默认8页）
   - 线程数: 同时运行的浏览器数量（默认2个）

3. **开始自动化**
   - 点击 "🚀 开始" 按钮
   - 程序会自动连接 Linken Sphere
   - 开始自动浏览 Apple Japan 网站

## ⚙️ 功能说明

### 配置管理
- **💾 保存**: 保存当前配置
- **📁 导入**: 从文件导入配置
- **📤 导出**: 导出配置到文件

### 线程控制
- **🚀 开始**: 启动第一个线程
- **⏹️ 停止**: 停止所有线程
- **➕ 新线程**: 创建额外的线程
- **🗑️ 清理**: 清理已完成的线程

### 状态监控
- 实时显示运行状态
- 显示活跃线程数量
- 列出所有线程及其状态

### 日志功能
- 实时显示操作日志
- **🗑️ 清空**: 清空日志显示
- **💾 保存**: 保存日志到文件

## 🔧 系统要求

- **Linken Sphere**: 必须安装并运行
- **网络**: 稳定的互联网连接
- **内存**: 建议 4GB+ RAM
- **系统**: Windows 10+, macOS 10.15+, 或现代 Linux

## ⚠️ 注意事项

1. **启动前准备**
   - 确保 Linken Sphere 正在运行
   - 确保网络连接稳定
   - 建议关闭其他占用资源的程序

2. **多线程使用**
   - 建议最多使用 2-3 个线程
   - 过多线程可能影响性能
   - 每个线程需要独立的 Linken Sphere 会话

3. **配置建议**
   - 浏览时长不要设置过短（建议 ≥ 30秒）
   - 循环次数根据需要调整
   - 保存配置以便下次使用

## 🆘 故障排除

### 连接失败
- 检查 Linken Sphere 是否运行
- 确认 API 端口 36555 可用
- 重启 Linken Sphere 后重试

### 线程无法启动
- 检查是否达到最大线程数限制
- 确认有足够的系统资源
- 查看日志了解具体错误

### 程序无响应
- 等待当前操作完成
- 使用 "⏹️ 停止" 按钮停止所有线程
- 重启程序

## 📞 技术支持

如遇问题，请提供：
1. 操作系统版本
2. Linken Sphere 版本
3. 错误日志内容
4. 配置文件内容

---
版本: 1.0 | 更新日期: 2024
"""
    
    with open('dist/使用说明.txt', 'w', encoding='utf-8') as f:
        f.write(guide_content)
    
    print("✅ 使用说明已创建")

def main():
    """主函数"""
    print("🚀 Linken Sphere Apple Browser 简化版构建")
    print("=" * 50)
    
    # 检查依赖
    if not check_dependencies():
        return
    
    # 创建规格文件
    create_simple_spec()
    
    # 构建可执行文件
    if build_executable():
        print("\n🎉 构建完成！")
        print("📁 输出目录: dist/")
        print("📖 使用说明: dist/使用说明.txt")
        
        current_os = platform.system()
        if current_os == "Windows":
            print("🚀 运行: dist/LinkenSphereAppleBrowser.exe")
        else:
            print("🚀 运行: ./dist/LinkenSphereAppleBrowser")
    else:
        print("\n❌ 构建失败")

if __name__ == "__main__":
    main()
