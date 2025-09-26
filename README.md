# 🍎 Linken Sphere Apple Browser

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
