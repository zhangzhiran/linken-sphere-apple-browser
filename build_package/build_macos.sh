#!/bin/bash
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
