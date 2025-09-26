@echo off
chcp 65001 >nul
echo Apple Website Browser - Windows 启动脚本
echo ==========================================

REM 检查 Python 是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到 Python，请先安装 Python 3.7+
    pause
    exit /b 1
)

REM 检查是否已安装依赖
python -c "import playwright" >nul 2>&1
if errorlevel 1 (
    echo 首次运行，正在安装依赖...
    python setup.py
    if errorlevel 1 (
        echo 安装失败
        pause
        exit /b 1
    )
)

echo.
echo 选择运行模式:
echo 1. 🖥️  图形界面版 (推荐，美观易用)
echo 2. 📝 完整版双层循环 (命令行，带重试机制)
echo 3. ⚡ 简化版双层循环 (命令行，带重试机制)
echo 4. 🧪 滚动行为测试
echo 5. 🔄 双层循环逻辑测试
echo 6. 🌐 网络重试机制测试
echo 7. 🚫 URL屏蔽功能测试
echo 8. 🎨 创建程序图标
echo.
set /p choice="请输入选择 (1-8): "

if "%choice%"=="1" (
    echo 启动图形界面版...
    python apple_browser_gui.py
) else if "%choice%"=="2" (
    python apple_website_browser.py
) else if "%choice%"=="3" (
    python simple_browser.py
) else if "%choice%"=="4" (
    python test_scroll.py
) else if "%choice%"=="5" (
    python test_dual_loop.py
) else if "%choice%"=="6" (
    python test_network_retry.py
) else if "%choice%"=="7" (
    python test_url_blocking.py
) else if "%choice%"=="8" (
    python create_icon.py
) else (
    echo 无效选择，使用图形界面版
    python apple_browser_gui.py
)

pause
