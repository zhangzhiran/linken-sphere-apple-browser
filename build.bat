@echo off
chcp 65001 >nul
echo 🚀 Linken Sphere Apple Browser - Windows 打包工具
echo ================================================

echo 📋 检查环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误：未找到 Python，请先安装 Python 3.7+
    pause
    exit /b 1
)

echo ✅ Python 环境检查通过

echo.
echo 📦 开始打包...
python quick_build.py

echo.
echo 📁 打包结果：
if exist "dist\LinkenSphereAppleBrowser_Windows.exe" (
    echo ✅ 成功生成：dist\LinkenSphereAppleBrowser_Windows.exe
    dir "dist\LinkenSphereAppleBrowser_Windows.exe"
) else (
    echo ❌ 打包失败，请检查错误信息
)

echo.
echo 🎯 下一步：
echo 1. 将 dist 目录中的 .exe 文件复制到目标电脑
echo 2. 确保目标电脑安装了 Linken Sphere
echo 3. 双击运行 .exe 文件
echo.
pause
