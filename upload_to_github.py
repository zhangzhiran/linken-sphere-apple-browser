#!/usr/bin/env python3
"""
一键上传到GitHub并自动构建macOS程序
"""

import os
import sys
import subprocess
import json
from pathlib import Path

class GitHubUploader:
    def __init__(self):
        self.project_files = [
            "simple_linken_gui.py",
            "linken_sphere_playwright_browser.py", 
            "linken_sphere_api.py",
            "build_cross_platform.py",
            "simple_icon_creator.py",
            "test_cross_platform_compatibility.py",
            "requirements.txt",
            "app_icon.ico",
            "app_icon.png",
            ".github/workflows/build-cross-platform.yml"
        ]
    
    def check_git(self):
        """检查Git是否安装"""
        try:
            result = subprocess.run(["git", "--version"], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ Git已安装: {result.stdout.strip()}")
                return True
            else:
                print("❌ Git未安装")
                return False
        except FileNotFoundError:
            print("❌ Git未安装")
            return False
    
    def create_gitignore(self):
        """创建.gitignore文件"""
        gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# PyInstaller
*.manifest
*.spec

# Virtual environments
venv/
env/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log

# Temporary files
*.tmp
*.temp

# Build outputs (keep source, ignore built executables)
dist/*.exe
dist/LinkenSphereAppleBrowser
dist/*.app
dist/*.dmg

# But keep documentation and icons in dist
!dist/*.txt
!dist/*.ico
!dist/*.png
!dist/*.icns
"""
        
        with open(".gitignore", "w", encoding="utf-8") as f:
            f.write(gitignore_content)
        print("✅ 创建.gitignore文件")
    
    def create_readme(self):
        """创建项目README"""
        readme_content = """# 🍎 Linken Sphere Apple Browser

一个集成Linken Sphere指纹保护的Apple网站自动化浏览工具，支持多线程、实时控制和跨平台运行。

## ✨ 特性

- 🚀 **多线程浏览**: 支持多个线程同时运行
- 🎮 **实时控制**: 暂停、恢复、停止单个线程
- 🛡️ **指纹保护**: 集成Linken Sphere反检测技术
- 💾 **配置管理**: 保存和导入浏览配置
- 📊 **实时监控**: 详细的日志和状态显示
- 🌍 **跨平台**: 支持Windows、macOS、Linux

## 📦 下载

### 自动构建版本
[![Build Status](https://github.com/YOUR_USERNAME/YOUR_REPO/workflows/Build%20Cross-Platform%20Executables/badge.svg)](https://github.com/YOUR_USERNAME/YOUR_REPO/actions)

**最新版本**: [Releases页面](https://github.com/YOUR_USERNAME/YOUR_REPO/releases)

- 🪟 **Windows**: `LinkenSphereAppleBrowser-Windows.exe`
- 🍎 **macOS**: `LinkenSphereAppleBrowser-macOS`
- 🐧 **Linux**: `LinkenSphereAppleBrowser-Linux`

### 手动构建

如果您想自己构建：

```bash
# 克隆仓库
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git
cd YOUR_REPO

# 安装依赖
pip install -r requirements.txt

# 运行兼容性测试
python test_cross_platform_compatibility.py

# 构建可执行文件
python build_cross_platform.py
```

## 🚀 使用方法

### 1. 准备工作
- 确保Linken Sphere正在运行
- 至少有一个配置文件可用

### 2. 启动程序
- **Windows**: 双击 `LinkenSphereAppleBrowser.exe`
- **macOS**: 双击 `LinkenSphereAppleBrowser` 或从应用程序启动
- **Linux**: 运行 `./LinkenSphereAppleBrowser`

### 3. 配置参数
- **浏览时长**: 每个页面的停留时间
- **循环次数**: 总的浏览轮数
- **最大线程**: 并发线程数量

### 4. 开始浏览
- 点击"🚀 开始"按钮
- 实时查看日志和状态
- 使用控制按钮管理线程

## 🔧 系统要求

### 所有平台
- **Linken Sphere**: 必须安装并运行
- **网络连接**: 稳定的互联网连接
- **内存**: 4GB RAM (推荐8GB)

### Windows
- Windows 10+ (64位)
- 无需额外安装

### macOS  
- macOS 10.15+ (Catalina或更高)
- 无需额外安装

### Linux
- 现代Linux发行版
- GUI桌面环境
- 无需额外安装

## 🛠️ 开发

### 环境设置
```bash
# 安装Python依赖
pip install -r requirements.txt

# 安装Playwright浏览器
playwright install chromium

# 运行测试
python test_cross_platform_compatibility.py
```

### 构建
```bash
# 构建当前平台
python build_cross_platform.py

# 或使用构建包在其他平台构建
cd build_package
./build_macos.sh    # macOS
./build_linux.sh   # Linux
build_windows.bat  # Windows
```

## 📋 技术栈

- **GUI**: Tkinter (跨平台)
- **异步**: asyncio + threading
- **浏览器**: Playwright
- **HTTP**: requests
- **打包**: PyInstaller
- **CI/CD**: GitHub Actions

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📄 许可证

MIT License

## 📞 支持

如有问题，请：
1. 查看[Issues页面](https://github.com/YOUR_USERNAME/YOUR_REPO/issues)
2. 创建新的Issue
3. 查看使用说明文档

---

**🎉 享受自动化浏览的便利！**
"""
        
        with open("README.md", "w", encoding="utf-8") as f:
            f.write(readme_content)
        print("✅ 创建README.md文件")
    
    def init_git_repo(self):
        """初始化Git仓库"""
        try:
            # 检查是否已经是Git仓库
            result = subprocess.run(["git", "status"], capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ 已经是Git仓库")
                return True
            
            # 初始化Git仓库
            subprocess.run(["git", "init"], check=True)
            print("✅ 初始化Git仓库")
            
            # 添加所有文件
            subprocess.run(["git", "add", "."], check=True)
            print("✅ 添加文件到Git")
            
            # 提交
            subprocess.run(["git", "commit", "-m", "Initial commit: Linken Sphere Apple Browser"], check=True)
            print("✅ 创建初始提交")
            
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Git操作失败: {e}")
            return False
    
    def show_github_instructions(self):
        """显示GitHub上传说明"""
        instructions = """
🚀 GitHub上传说明
==================

现在您需要：

1. 📝 创建GitHub仓库
   - 访问 https://github.com
   - 点击 "New repository"
   - 输入仓库名称 (例如: linken-sphere-apple-browser)
   - 选择 "Public" (免费构建)
   - 不要勾选 "Initialize with README"
   - 点击 "Create repository"

2. 🔗 连接本地仓库到GitHub
   复制并运行GitHub显示的命令，类似：
   
   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
   git branch -M main
   git push -u origin main

3. ⏳ 等待自动构建
   - 上传完成后，点击 "Actions" 标签
   - 等待构建完成 (约10-15分钟)
   - 绿色✅表示成功

4. 📦 下载macOS程序
   - 点击 "Actions" → 最新的构建
   - 下载 "LinkenSphereAppleBrowser-macOS" 文件
   - 或查看 "Releases" 页面

🎯 构建完成后您将获得：
- LinkenSphereAppleBrowser-Windows.exe (Windows版本)
- LinkenSphereAppleBrowser-macOS (macOS版本) ← 这是您需要的！
- LinkenSphereAppleBrowser-Linux (Linux版本)

💡 提示：
- 构建是完全免费的
- 每次推送代码都会自动构建
- 所有平台的程序都会自动生成
"""
        print(instructions)
    
    def prepare_for_upload(self):
        """准备上传"""
        print("🚀 准备上传到GitHub...")
        print("=" * 50)
        
        # 检查Git
        if not self.check_git():
            print("\n❌ 请先安装Git:")
            print("   下载地址: https://git-scm.com/download/win")
            return False
        
        # 创建必要文件
        self.create_gitignore()
        self.create_readme()
        
        # 初始化Git仓库
        if not self.init_git_repo():
            return False
        
        # 显示说明
        self.show_github_instructions()
        
        return True

def main():
    """主函数"""
    print("🍎 Linken Sphere Apple Browser - GitHub自动构建设置")
    print("=" * 60)
    print("这个脚本将帮助您设置GitHub自动构建，生成macOS程序")
    print("=" * 60)
    
    uploader = GitHubUploader()
    
    if uploader.prepare_for_upload():
        print("\n" + "=" * 60)
        print("✅ 准备完成！")
        print("=" * 60)
        print("📋 下一步:")
        print("1. 按照上面的说明创建GitHub仓库")
        print("2. 上传代码到GitHub")
        print("3. 等待自动构建完成")
        print("4. 下载macOS程序")
        print("\n🎉 大约15分钟后您就能获得macOS程序！")
    else:
        print("\n❌ 准备失败，请检查错误信息")

if __name__ == "__main__":
    main()
