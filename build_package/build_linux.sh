#!/bin/bash
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
