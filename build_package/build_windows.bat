@echo off
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
echo 📁 输出目录: distdir distpause
