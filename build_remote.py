#!/usr/bin/env python3
"""
远程构建脚本 - 支持在不同平台上构建
"""

import os
import sys
import platform
import subprocess
import json
from pathlib import Path

class RemoteBuilder:
    def __init__(self):
        self.current_platform = platform.system()
        self.project_files = [
            "simple_linken_gui.py",
            "linken_sphere_playwright_browser.py", 
            "linken_sphere_api.py",
            "build_cross_platform.py",
            "simple_icon_creator.py",
            "test_cross_platform_compatibility.py",
            "requirements.txt"
        ]
    
    def create_build_package(self):
        """创建构建包"""
        print("📦 创建构建包...")
        
        # 创建构建目录
        build_package_dir = Path("build_package")
        build_package_dir.mkdir(exist_ok=True)
        
        # 复制必要文件
        for file_path in self.project_files:
            if os.path.exists(file_path):
                import shutil
                shutil.copy2(file_path, build_package_dir / file_path)
                print(f"✅ 复制: {file_path}")
            else:
                print(f"⚠️ 文件不存在: {file_path}")
        
        # 创建构建脚本
        self.create_platform_scripts(build_package_dir)
        
        # 创建说明文件
        self.create_readme(build_package_dir)
        
        print(f"✅ 构建包创建完成: {build_package_dir}")
        return build_package_dir
    
    def create_platform_scripts(self, build_dir):
        """创建平台特定的构建脚本"""
        
        # macOS构建脚本
        macos_script = """#!/bin/bash
echo "🍎 macOS构建脚本"
echo "=================="

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3未安装，请先安装Python 3.8+"
    exit 1
fi

echo "✅ Python版本: $(python3 --version)"

# 安装依赖
echo "📦 安装依赖..."
pip3 install -r requirements.txt

# 创建图标
echo "🎨 创建图标..."
python3 simple_icon_creator.py

# 运行兼容性测试
echo "🧪 运行兼容性测试..."
python3 test_cross_platform_compatibility.py

# 构建应用
echo "🏗️ 构建macOS应用..."
python3 build_cross_platform.py

echo "✅ macOS构建完成！"
echo "📁 输出目录: dist/"
ls -la dist/
"""
        
        # Linux构建脚本
        linux_script = """#!/bin/bash
echo "🐧 Linux构建脚本"
echo "=================="

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3未安装，请先安装Python 3.8+"
    echo "Ubuntu/Debian: sudo apt install python3 python3-pip python3-tk"
    exit 1
fi

echo "✅ Python版本: $(python3 --version)"

# 安装系统依赖
echo "📦 安装系统依赖..."
if command -v apt &> /dev/null; then
    sudo apt update
    sudo apt install -y python3-tk python3-dev build-essential
elif command -v yum &> /dev/null; then
    sudo yum install -y tkinter python3-devel gcc
fi

# 安装Python依赖
echo "📦 安装Python依赖..."
pip3 install -r requirements.txt

# 创建图标
echo "🎨 创建图标..."
python3 simple_icon_creator.py

# 运行兼容性测试
echo "🧪 运行兼容性测试..."
python3 test_cross_platform_compatibility.py

# 构建应用
echo "🏗️ 构建Linux应用..."
python3 build_cross_platform.py

echo "✅ Linux构建完成！"
echo "📁 输出目录: dist/"
ls -la dist/
"""
        
        # Windows构建脚本
        windows_script = """@echo off
echo 🪟 Windows构建脚本
echo ==================

REM 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python未安装，请先安装Python 3.8+
    pause
    exit /b 1
)

echo ✅ Python版本:
python --version

REM 安装依赖
echo 📦 安装依赖...
pip install -r requirements.txt

REM 创建图标
echo 🎨 创建图标...
python simple_icon_creator.py

REM 运行兼容性测试
echo 🧪 运行兼容性测试...
python test_cross_platform_compatibility.py

REM 构建应用
echo 🏗️ 构建Windows应用...
python build_cross_platform.py

echo ✅ Windows构建完成！
echo 📁 输出目录: dist\
dir dist\
pause
"""
        
        # 写入脚本文件
        (build_dir / "build_macos.sh").write_text(macos_script, encoding='utf-8')
        (build_dir / "build_linux.sh").write_text(linux_script, encoding='utf-8')
        (build_dir / "build_windows.bat").write_text(windows_script, encoding='utf-8')
        
        # 设置执行权限 (Unix系统)
        if self.current_platform != "Windows":
            os.chmod(build_dir / "build_macos.sh", 0o755)
            os.chmod(build_dir / "build_linux.sh", 0o755)
        
        print("✅ 平台构建脚本创建完成")
    
    def create_readme(self, build_dir):
        """创建说明文件"""
        readme_content = """# Linken Sphere Apple Browser - 跨平台构建包

## 📋 使用说明

这个构建包包含了在不同平台上构建Linken Sphere Apple Browser的所有必要文件。

### 🍎 在macOS上构建

1. 打开终端，进入构建包目录
2. 运行构建脚本：
   ```bash
   chmod +x build_macos.sh
   ./build_macos.sh
   ```
3. 构建完成后，在`dist/`目录找到macOS可执行文件

### 🐧 在Linux上构建

1. 打开终端，进入构建包目录
2. 运行构建脚本：
   ```bash
   chmod +x build_linux.sh
   ./build_linux.sh
   ```
3. 构建完成后，在`dist/`目录找到Linux可执行文件

### 🪟 在Windows上构建

1. 打开命令提示符，进入构建包目录
2. 运行构建脚本：
   ```cmd
   build_windows.bat
   ```
3. 构建完成后，在`dist\`目录找到Windows可执行文件

## 📦 包含的文件

- `simple_linken_gui.py` - 主GUI程序
- `linken_sphere_playwright_browser.py` - 浏览器自动化
- `linken_sphere_api.py` - API接口
- `build_cross_platform.py` - 构建脚本
- `simple_icon_creator.py` - 图标创建
- `test_cross_platform_compatibility.py` - 兼容性测试
- `requirements.txt` - 依赖列表
- `build_*.sh` / `build_*.bat` - 平台构建脚本

## 🔧 系统要求

### 所有平台
- Python 3.8 或更高版本
- 互联网连接（用于下载依赖）

### macOS
- macOS 10.15+ (Catalina或更高)
- Xcode Command Line Tools

### Linux
- 现代Linux发行版（Ubuntu 20.04+, CentOS 8+等）
- 开发工具包（build-essential）

### Windows
- Windows 10+ (64位推荐)
- Visual Studio Build Tools（某些包需要）

## 🚀 构建结果

构建成功后，您将获得：
- 对应平台的可执行文件
- 应用程序图标
- 使用说明文档

## ❓ 故障排除

如果遇到问题：
1. 确保Python版本正确（3.8+）
2. 检查网络连接
3. 查看构建脚本的错误输出
4. 确保有足够的磁盘空间（至少1GB）

## 📞 技术支持

如有问题，请查看错误日志或联系开发者。
"""
        
        (build_dir / "README.md").write_text(readme_content, encoding='utf-8')
        print("✅ README.md 创建完成")
    
    def create_docker_build(self, build_dir):
        """创建Docker构建配置"""
        dockerfile_content = """# Linken Sphere Apple Browser - Linux构建容器
FROM python:3.10-slim

# 安装系统依赖
RUN apt-get update && apt-get install -y \\
    python3-tk \\
    python3-dev \\
    build-essential \\
    && rm -rf /var/lib/apt/lists/*

# 设置工作目录
WORKDIR /app

# 复制文件
COPY . .

# 安装Python依赖
RUN pip install -r requirements.txt

# 安装Playwright浏览器
RUN playwright install chromium

# 构建应用
RUN python3 build_cross_platform.py

# 输出构建结果
CMD ["ls", "-la", "dist/"]
"""
        
        docker_compose_content = """version: '3.8'
services:
  builder:
    build: .
    volumes:
      - ./dist:/app/dist
    command: python3 build_cross_platform.py
"""
        
        (build_dir / "Dockerfile").write_text(dockerfile_content, encoding='utf-8')
        (build_dir / "docker-compose.yml").write_text(docker_compose_content, encoding='utf-8')
        
        print("✅ Docker构建配置创建完成")

def main():
    """主函数"""
    print("🚀 Linken Sphere Apple Browser - 远程构建包生成器")
    print("=" * 60)
    
    builder = RemoteBuilder()
    
    # 创建构建包
    build_package_dir = builder.create_build_package()
    
    # 创建Docker配置
    builder.create_docker_build(build_package_dir)
    
    print("\n" + "=" * 60)
    print("📦 构建包生成完成！")
    print("=" * 60)
    print(f"📁 构建包位置: {build_package_dir}")
    print("\n🚀 下一步:")
    print("1. 将构建包复制到目标平台")
    print("2. 运行对应的构建脚本:")
    print("   - macOS: ./build_macos.sh")
    print("   - Linux: ./build_linux.sh") 
    print("   - Windows: build_windows.bat")
    print("3. 在dist/目录找到构建结果")

if __name__ == "__main__":
    main()
