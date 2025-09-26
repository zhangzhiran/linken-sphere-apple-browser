# Linken Sphere 集成指南

## 📖 概述

本项目已集成 Linken Sphere 指纹浏览器，可以提供更好的反检测能力和指纹管理功能。

## 🔧 Linken Sphere 设置

### 1. 安装和启动 Linken Sphere

1. 从官网下载并安装 Linken Sphere：https://docs.ls.app/
2. 启动 Linken Sphere 应用程序
3. 确保 API 服务已启用（默认端口：3001）

### 2. API 配置

Linken Sphere API 默认配置：
- **地址**: `127.0.0.1`
- **端口**: `3001`
- **协议**: HTTP

⚠️ **重要提示**: API 功能仅在特定套餐中可用。如果您看到 "API is not available with the desktop's tariff" 错误，说明您的套餐不支持 API 自动化。

### 3. 验证连接

运行诊断工具检查连接状态：

```bash
python diagnose_linken_sphere.py
```

或者运行完整测试：

```bash
python test_linken_sphere.py
```

### 4. API 不可用时的解决方案

如果 API 不可用，您有以下选择：

#### 选项 1: 升级套餐
- 联系 Linken Sphere 升级到支持 API 的套餐
- 通常需要商业版或企业版许可证

#### 选项 2: 使用手动集成模式
- 运行 `python linken_sphere_manual.py`
- 手动在 Linken Sphere 中启动浏览器
- 程序通过调试端口连接到浏览器

#### 选项 3: 使用标准浏览器
- 运行 `python apple_website_browser.py`
- 使用标准 Chrome 浏览器（无指纹保护）

## 🚀 使用方法

### 方法1：自动 API 模式（需要支持 API 的套餐）

```bash
python linken_sphere_browser.py
```

运行后会提示配置选项：
1. 每页浏览时间
2. 大循环次数
3. 是否使用 Linken Sphere
4. Linken Sphere API 配置

### 方法2：手动集成模式（API 不可用时）

```bash
python linken_sphere_manual.py
```

手动模式步骤：
1. 在 Linken Sphere 中创建配置文件
2. 手动启动浏览器（确保调试模式开启）
3. 程序自动连接到浏览器进行自动化

### 方法3：直接代码调用

```python
from linken_sphere_browser import LinkenSphereBrowser

# 配置 Linken Sphere
linken_sphere_config = {
    'api_host': '127.0.0.1',
    'api_port': 3001,
    'api_key': None,  # 如果需要API密钥
    'profile_name': 'Apple Browser Profile'
}

# 创建浏览器实例
browser = LinkenSphereBrowser(
    browse_duration=60,
    major_cycles=3,
    linken_sphere_config=linken_sphere_config
)

# 运行浏览器
browser.run()
```

## 🔍 功能特点

### 自动配置文件管理
- 自动创建适合 Apple 网站的浏览器配置文件
- 智能设置时区、语言、User-Agent 等参数
- 支持 Windows、Mac、Linux 系统适配

### 指纹保护
- Canvas 指纹噪声
- WebGL 指纹伪装
- WebRTC 泄露防护
- 字体指纹保护

### 会话管理
- 自动启动和停止浏览器会话
- 会话状态监控
- 异常情况下的自动清理

## ⚙️ 配置选项

### 基础配置

```python
linken_sphere_config = {
    'api_host': '127.0.0.1',      # API 服务器地址
    'api_port': 3001,             # API 端口
    'api_key': None,              # API 密钥（可选）
    'profile_name': 'My Profile'  # 配置文件名称
}
```

### 高级配置

可以通过修改 `LinkenSphereProfileManager.create_default_profile()` 方法来自定义配置文件：

```python
profile_config = {
    "name": "Custom Profile",
    "browser": "chrome",  # 或 "firefox"
    "os": {
        "name": "Windows",
        "version": "10"
    },
    "screen": {
        "width": 1920,
        "height": 1080
    },
    "timezone": "Asia/Tokyo",
    "language": "ja-JP,ja;q=0.9,en;q=0.8",
    "proxy": {
        "type": "http",
        "host": "proxy.example.com",
        "port": 8080,
        "username": "user",
        "password": "pass"
    }
}
```

## 🔄 回退机制

如果 Linken Sphere 不可用，程序会自动回退到标准 Chrome 浏览器：

1. **检测失败**: 无法连接到 Linken Sphere API
2. **自动回退**: 使用标准 Chrome 浏览器
3. **功能保持**: 所有浏览功能正常工作
4. **日志记录**: 详细记录回退原因

## 📊 监控和日志

### 日志文件
- `linken_sphere_browser_log.txt` - 详细的运行日志
- 包含 API 调用、会话管理、错误信息等

### 实时监控
```python
# 检查会话状态
session_info = manager.api.get_session_info(session_id)

# 查看活动会话
active_sessions = manager.active_sessions
```

## 🛠️ 故障排除

### 常见问题

1. **连接失败**
   ```
   ❌ 无法连接到 Linken Sphere API
   ```
   - 检查 Linken Sphere 是否正在运行
   - 验证 API 端口（默认3001）
   - 检查防火墙设置

2. **会话创建失败**
   ```
   ❌ 创建 Linken Sphere 会话失败
   ```
   - 检查配置文件是否有效
   - 验证系统资源是否充足
   - 查看 Linken Sphere 应用程序日志

3. **浏览器连接失败**
   ```
   ❌ 无法连接到 WebDriver 端点
   ```
   - 检查 Chrome/Chromium 是否已安装
   - 验证 WebDriver 端口是否可用
   - 尝试重启 Linken Sphere

### 调试模式

启用详细日志：

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📚 API 参考

### LinkenSphereManager 主要方法

- `initialize()` - 初始化连接
- `create_browser_session(profile_name)` - 创建浏览器会话
- `close_session(session_id)` - 关闭会话
- `close_all_sessions()` - 关闭所有会话

### LinkenSphereAPI 主要方法

- `check_connection()` - 检查连接状态
- `get_profiles()` - 获取配置文件列表
- `create_profile(config)` - 创建配置文件
- `start_session(profile_id)` - 启动会话
- `stop_session(session_id)` - 停止会话

## 🔗 相关链接

- [Linken Sphere 官方文档](https://docs.ls.app/)
- [API 自动化文档](https://docs.ls.app/v1/api-automation/cn)
- [配置文件参数说明](https://docs.ls.app/v1/profiles/)

## 📝 注意事项

1. **许可证**: 确保您有有效的 Linken Sphere 许可证
2. **资源占用**: Linken Sphere 会占用额外的系统资源
3. **网络要求**: 某些功能可能需要稳定的网络连接
4. **兼容性**: 建议使用最新版本的 Linken Sphere
