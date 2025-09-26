@echo off
chcp 65001 >nul
title Apple Website Browser GUI

echo.
echo 🍎 Apple Website Browser - 图形界面版
echo ========================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: 未找到Python，请先安装Python 3.7+
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo ✅ Python 已安装
echo.

REM 检查必要的依赖
echo 🔍 检查依赖包...
python -c "import tkinter" >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: tkinter 未安装，这是Python的标准库
    echo 请重新安装Python并确保包含tkinter
    pause
    exit /b 1
)

python -c "import playwright" >nul 2>&1
if errorlevel 1 (
    echo ⚠️ 警告: playwright 未安装
    echo 正在安装 playwright...
    pip install playwright
    if errorlevel 1 (
        echo ❌ 安装失败，请手动运行: pip install playwright
        pause
        exit /b 1
    )
    echo 正在安装浏览器引擎...
    playwright install
)

echo ✅ 依赖检查完成
echo.

REM 创建图标（如果不存在）
if not exist "apple_icon.png" (
    echo 🎨 创建程序图标...
    python create_icon.py
    echo.
)

REM 启动GUI
echo 🚀 启动图形界面...
echo.
python apple_browser_gui.py

if errorlevel 1 (
    echo.
    echo ❌ 程序运行出错
    echo 请检查错误信息或联系技术支持
    pause
)

echo.
echo 👋 程序已退出
pause
