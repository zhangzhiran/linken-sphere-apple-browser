# 🔧 Linken Sphere 集成问题解决方案

## 📋 问题诊断结果

根据您遇到的 `SystemExit: 1` 错误和我们的诊断，问题的根本原因是：

**Linken Sphere API 在您当前的套餐中不可用**

错误信息：`{"error":"API is not available with the desktop's tariff"}`

## 🎯 解决方案

我为您提供了 **3种解决方案**，您可以根据需要选择：

### 方案1: 手动集成模式 ⭐ **推荐**

使用新创建的手动集成脚本，无需API即可使用 Linken Sphere：

```bash
python linken_sphere_manual.py
```

**优点**：
- ✅ 保留 Linken Sphere 的指纹保护功能
- ✅ 无需升级套餐
- ✅ 完全自动化的浏览流程

**使用步骤**：
1. 在 Linken Sphere 中手动创建配置文件
2. 启动浏览器（确保调试模式开启）
3. 运行脚本，程序自动连接并控制浏览器

### 方案2: 升级 Linken Sphere 套餐

联系 Linken Sphere 升级到支持 API 的套餐：

```bash
python linken_sphere_browser.py  # 升级后可用
```

**优点**：
- ✅ 完全自动化，无需手动操作
- ✅ 支持批量配置文件管理

**缺点**：
- ❌ 需要额外费用

### 方案3: 使用标准浏览器

使用原有的 Playwright 版本：

```bash
python apple_website_browser.py
```

**优点**：
- ✅ 完全免费
- ✅ 功能完整

**缺点**：
- ❌ 无指纹保护

## 🚀 快速开始

### 立即使用手动集成模式

1. **运行统一启动器**：
   ```bash
   python start_browser.py
   ```

2. **选择选项 4**：`🔧 Linken Sphere 手动版`

3. **按照屏幕提示操作**：
   - 程序会显示详细的设置说明
   - 在 Linken Sphere 中创建配置文件
   - 启动浏览器
   - 确认设置完成

4. **开始自动化浏览**

## 🔍 诊断工具

我还为您创建了几个诊断工具：

### 1. 完整诊断
```bash
python diagnose_linken_sphere.py
```
- 检查 Linken Sphere 连接状态
- 验证进程和端口
- 提供详细的解决建议

### 2. API 端点探测
```bash
python probe_linken_sphere_api.py
```
- 探测所有可能的 API 端点
- 分析响应状态
- 确定 API 可用性

### 3. 集成测试
```bash
python test_linken_sphere.py
```
- 完整的功能测试
- API 连接测试
- 会话管理测试

## 📁 新增文件说明

我为您创建了以下新文件：

1. **`linken_sphere_manual.py`** - 手动集成模式的主程序
2. **`diagnose_linken_sphere.py`** - 诊断工具
3. **`probe_linken_sphere_api.py`** - API 探测工具
4. **`start_browser.py`** - 统一启动器（更新）
5. **`LINKEN_SPHERE_GUIDE.md`** - 详细使用指南（更新）
6. **`start_linken_sphere.bat`** - Windows 批处理启动脚本

## 🔧 配置说明

### 手动模式配置

手动模式需要以下配置：

- **Chrome 调试端口**: 默认 9222
- **Linken Sphere 配置文件**: 手动创建
- **浏览器启动**: 手动启动并确保调试模式

### 推荐的 Linken Sphere 配置

在创建配置文件时，建议使用以下设置：

- **时区**: Asia/Tokyo
- **语言**: ja-JP,ja;q=0.9,en;q=0.8
- **屏幕分辨率**: 1920x1080
- **User-Agent**: Chrome 最新版本
- **Canvas 指纹**: 启用噪声
- **WebGL 指纹**: 启用伪装

## 📞 技术支持

如果您在使用过程中遇到问题：

1. **查看日志文件**：
   - `linken_sphere_manual_log.txt`
   - `linken_sphere_browser_log.txt`

2. **运行诊断工具**：
   ```bash
   python diagnose_linken_sphere.py
   ```

3. **检查常见问题**：
   - Linken Sphere 是否正在运行
   - 浏览器是否以调试模式启动
   - 端口是否被占用

## 🎉 总结

通过手动集成模式，您可以：

- ✅ 继续使用 Linken Sphere 的指纹保护功能
- ✅ 无需升级套餐或支付额外费用
- ✅ 保持完全自动化的浏览流程
- ✅ 享受与 API 模式相同的功能

**立即开始**：运行 `python start_browser.py` 并选择选项 4！
