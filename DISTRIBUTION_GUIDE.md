# 🚀 Linken Sphere Apple Browser 分发指南

## 📦 打包步骤

### Windows 系统
```bash
# 方法1：使用批处理脚本（推荐）
build.bat

# 方法2：手动打包
python quick_build.py
```

### Mac/Linux 系统
```bash
# 方法1：使用Shell脚本（推荐）
./build.sh

# 方法2：手动打包
python3 quick_build.py
```

## 📁 生成的文件

打包完成后，`dist` 目录中会包含：

### Windows
- `LinkenSphereAppleBrowser_Windows.exe` - 主程序（约50-100MB）
- `LinkenSphereAppleBrowser_Windows.exe_使用指南.txt` - 使用说明

### Mac
- `LinkenSphereAppleBrowser_Darwin` - 主程序（约50-100MB）
- `LinkenSphereAppleBrowser_Darwin_使用指南.txt` - 使用说明

### Linux
- `LinkenSphereAppleBrowser_Linux` - 主程序（约50-100MB）
- `LinkenSphereAppleBrowser_Linux_使用指南.txt` - 使用说明

## 🎯 分发给其他用户

### 1. 准备分发包
```
LinkenSphereAppleBrowser_分发包/
├── LinkenSphereAppleBrowser_Windows.exe    # Windows版本
├── LinkenSphereAppleBrowser_Darwin         # Mac版本
├── LinkenSphereAppleBrowser_Linux          # Linux版本
├── 使用指南.txt                            # 详细使用说明
└── README.md                               # 快速开始指南
```

### 2. 用户系统要求

#### Windows
- Windows 10/11 (64位)
- 已安装 Linken Sphere
- 4GB+ RAM
- 稳定网络连接

#### Mac
- macOS 10.15+ (Catalina)
- 已安装 Linken Sphere
- 4GB+ RAM
- 稳定网络连接

#### Linux
- Ubuntu 18.04+ / CentOS 7+ / 其他现代发行版
- 已安装 Linken Sphere
- 4GB+ RAM
- 稳定网络连接

### 3. 用户使用步骤

#### Windows用户
1. 下载 `LinkenSphereAppleBrowser_Windows.exe`
2. 启动 Linken Sphere
3. 双击运行 `.exe` 文件
4. 程序自动开始浏览

#### Mac用户
1. 下载 `LinkenSphereAppleBrowser_Darwin`
2. 启动 Linken Sphere
3. 在终端中运行：`./LinkenSphereAppleBrowser_Darwin`
4. 或者双击运行（可能需要在安全设置中允许）

#### Linux用户
1. 下载 `LinkenSphereAppleBrowser_Linux`
2. 启动 Linken Sphere
3. 添加执行权限：`chmod +x LinkenSphereAppleBrowser_Linux`
4. 运行：`./LinkenSphereAppleBrowser_Linux`

## ⚠️ 重要注意事项

### 1. Linken Sphere 依赖
- **用户必须自行安装 Linken Sphere**
- 可执行文件不包含 Linken Sphere
- 需要确保 Linken Sphere API 可用（端口36555）

### 2. 网络要求
- 需要稳定的互联网连接
- 能够访问 apple.com/jp
- 防火墙不能阻止程序网络访问

### 3. 系统权限
- Windows：可能需要管理员权限
- Mac：可能需要在"安全性与隐私"中允许运行
- Linux：需要执行权限

## 🔧 故障排除

### 常见问题及解决方案

#### 1. "无法连接到 Linken Sphere"
**原因**：Linken Sphere 未运行或API不可用
**解决**：
- 启动 Linken Sphere
- 检查端口36555是否开放
- 重启 Linken Sphere

#### 2. "无法连接到调试端口"
**原因**：浏览器会话未启动或调试端口被占用
**解决**：
- 在 Linken Sphere 中启动浏览器会话
- 启用远程调试功能
- 检查端口9222是否可用

#### 3. Mac安全警告
**原因**：Mac系统安全机制
**解决**：
- 右键点击程序，选择"打开"
- 在"系统偏好设置 > 安全性与隐私"中允许运行

#### 4. 程序无响应
**原因**：网络问题或页面加载缓慢
**解决**：
- 检查网络连接
- 等待程序自动重试
- 查看日志文件了解详情

## 📊 程序特性

### 功能特点
- ✅ **指纹保护**：使用 Linken Sphere 的完整指纹保护
- ✅ **智能浏览**：模拟真实用户行为
- ✅ **自动重试**：网络错误自动恢复
- ✅ **详细日志**：完整的操作记录
- ✅ **跨平台**：支持 Windows、Mac、Linux

### 浏览模式
- **双层循环**：3大循环 × 8小循环 = 24页
- **精确时间**：每页浏览60秒
- **随机选择**：从可用链接中随机选择
- **智能滚动**：模拟真实阅读行为

## 📞 技术支持

如果用户遇到问题，请收集以下信息：
1. 操作系统版本
2. Linken Sphere 版本
3. 错误信息截图
4. 日志文件内容（`linken_sphere_browser_log.txt`）

## 🔄 更新说明

### 版本管理
- 每次打包都会生成带系统标识的文件名
- 建议在文件名中包含版本号
- 保持向后兼容性

### 更新流程
1. 修改源代码
2. 重新打包
3. 测试新版本
4. 分发给用户
5. 提供更新说明

---

**🎉 现在您可以将生成的可执行文件分发给任何用户，他们只需要安装 Linken Sphere 即可使用！**
