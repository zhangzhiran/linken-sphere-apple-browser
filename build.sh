#!/bin/bash

echo "🚀 Linken Sphere Apple Browser - Mac/Linux 打包工具"
echo "================================================"

# 检查 Python
echo "📋 检查环境..."
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误：未找到 Python3，请先安装 Python 3.7+"
    exit 1
fi

echo "✅ Python 环境检查通过"
python3 --version

echo ""
echo "📦 开始打包..."
python3 quick_build.py

echo ""
echo "📁 打包结果："
if [[ "$OSTYPE" == "darwin"* ]]; then
    # Mac
    if [ -f "dist/LinkenSphereAppleBrowser_Darwin" ]; then
        echo "✅ 成功生成：dist/LinkenSphereAppleBrowser_Darwin"
        ls -lh "dist/LinkenSphereAppleBrowser_Darwin"
    else
        echo "❌ 打包失败，请检查错误信息"
    fi
else
    # Linux
    if [ -f "dist/LinkenSphereAppleBrowser_Linux" ]; then
        echo "✅ 成功生成：dist/LinkenSphereAppleBrowser_Linux"
        ls -lh "dist/LinkenSphereAppleBrowser_Linux"
    else
        echo "❌ 打包失败，请检查错误信息"
    fi
fi

echo ""
echo "🎯 下一步："
echo "1. 将 dist 目录中的可执行文件复制到目标电脑"
echo "2. 确保目标电脑安装了 Linken Sphere"
echo "3. 运行可执行文件"
echo ""
