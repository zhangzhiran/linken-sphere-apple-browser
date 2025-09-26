@echo off
chcp 65001 >nul
title 🔒 Linken Sphere Apple Browser

echo.
echo 🔒 Linken Sphere Apple Website Browser
echo =====================================
echo.

REM 检查 Python 是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python 未安装或未添加到 PATH
    echo 请先安装 Python 3.7+ 并添加到系统 PATH
    pause
    exit /b 1
)

REM 检查必要文件
if not exist "linken_sphere_browser.py" (
    echo ❌ 找不到 linken_sphere_browser.py 文件
    echo 请确保在正确的目录中运行此脚本
    pause
    exit /b 1
)

if not exist "linken_sphere_api.py" (
    echo ❌ 找不到 linken_sphere_api.py 文件
    echo 请确保所有必要文件都存在
    pause
    exit /b 1
)

echo ✅ 环境检查通过
echo.

REM 检查依赖项
echo 🔍 检查 Python 依赖项...
python -c "import selenium, requests" >nul 2>&1
if errorlevel 1 (
    echo ⚠️ 缺少必要的 Python 依赖项
    echo 正在安装依赖项...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ❌ 依赖项安装失败
        pause
        exit /b 1
    )
)

echo ✅ 依赖项检查通过
echo.

REM 启动程序
echo 🚀 启动 Linken Sphere 浏览器...
echo.
python linken_sphere_browser.py

echo.
echo 程序已结束
pause
