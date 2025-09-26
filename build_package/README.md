# Linken Sphere Apple Browser - 跨平台构建包

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
