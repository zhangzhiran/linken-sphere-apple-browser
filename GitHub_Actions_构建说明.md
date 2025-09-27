# GitHub Actions 自动构建macOS应用

## 🎯 概述

通过GitHub Actions，您可以在云端自动构建可直接分发给用户的macOS应用程序，无需本地macOS环境。

## 🚀 快速开始

### 1. 手动触发构建

最简单的方式：

1. **访问**: https://github.com/zhangzhiran/linken-sphere-apple-browser/actions
2. **选择**: "Build macOS Distribution Package" 工作流
3. **点击**: "Run workflow" 按钮
4. **等待**: 5-10分钟构建完成
5. **下载**: 从Artifacts或Releases下载构建结果

### 2. 自动触发构建

推送代码时自动构建：
```bash
git push origin main  # 推送到main分支自动触发
```

创建版本标签时自动发布：
```bash
git tag v1.0.0
git push origin v1.0.0  # 自动创建Release
```

## 📦 构建产物

### 🎯 用户分发文件

构建完成后会生成以下文件供用户下载：

#### 1. DMG安装包 (推荐)
- **文件名**: `LinkenSphereAppleBrowser-macOS.dmg`
- **大小**: 约50-100MB
- **用途**: 最适合分发给最终用户
- **使用**: 用户双击安装，标准macOS体验

#### 2. 分发ZIP包
- **文件名**: `LinkenSphereAppleBrowser-macOS-Distribution.zip`
- **内容**: 
  ```
  macOS_Distribution/
  ├── LinkenSphereAppleBrowser.app    # 主应用
  ├── install.sh                      # 自动安装脚本
  ├── README.txt                      # 用户说明
  ├── app_icon.icns                   # 应用图标
  └── *.json                          # 配置文件
  ```
- **用途**: 包含完整安装工具的分发包

### 📋 技术文件

#### 3. 应用程序文件
- **文件**: `LinkenSphereAppleBrowser.app` 或可执行文件
- **用途**: 开发者测试或直接运行

## 🔄 工作流程详解

### 构建环境
- **系统**: macOS-latest (GitHub提供的最新macOS)
- **Python**: 3.10
- **架构**: Universal Binary (支持Intel + Apple Silicon)
- **工具**: PyInstaller, Xcode命令行工具

### 构建步骤
1. **环境准备** (1-2分钟)
   - 检出代码
   - 设置Python环境
   - 安装系统依赖

2. **依赖安装** (2-3分钟)
   - 安装PyInstaller
   - 安装项目依赖
   - 可选安装Playwright

3. **资源准备** (30秒)
   - 创建应用图标
   - 运行兼容性测试

4. **应用构建** (2-3分钟)
   - PyInstaller打包
   - 创建应用包或可执行文件

5. **分发包创建** (1分钟)
   - 创建DMG安装包
   - 生成分发ZIP
   - 创建用户文档

6. **文件上传** (1分钟)
   - 上传到GitHub Artifacts
   - 可选创建GitHub Release

## 📥 下载方式

### 方式1: 从Artifacts下载 (临时)

构建完成后：
1. 进入Actions页面
2. 点击最新的工作流运行
3. 在页面底部找到Artifacts
4. 下载需要的文件

**注意**: Artifacts保存30天后自动删除

### 方式2: 从Releases下载 (永久)

如果创建了Release：
1. 访问: https://github.com/zhangzhiran/linken-sphere-apple-browser/releases
2. 找到最新版本
3. 下载附件中的文件

**优势**: 永久保存，版本管理清晰

## 🎯 用户使用指南

### 给用户的分发说明

当您要分发应用给用户时，可以这样说明：

---

**LinkenSphere Apple Browser - macOS版本**

**系统要求**: macOS 10.14或更高版本

**安装方法**:

**方法1 (推荐)**: 
1. 下载 `LinkenSphereAppleBrowser-macOS.dmg`
2. 双击DMG文件
3. 将应用拖拽到Applications文件夹
4. 从Launchpad启动

**方法2**:
1. 下载 `LinkenSphereAppleBrowser-macOS-Distribution.zip`
2. 解压ZIP文件
3. 双击 `install.sh` 自动安装

**如果遇到安全提示**:
右键点击应用 → 选择"打开" → 点击"打开"

---

## 🔧 自定义构建

### 修改构建配置

编辑 `.github/workflows/build-macos-only.yml` 文件：

```yaml
# 修改应用名称
- name: Build macOS distribution package
  run: |
    # 在这里可以设置环境变量
    export APP_NAME="您的应用名称"
    python create_macos_distribution.py
```

### 添加代码签名

如果有Apple开发者账户，可以添加代码签名：

```yaml
- name: Code sign application
  run: |
    codesign --force --deep --sign "Developer ID Application: Your Name" \
      dist/LinkenSphereAppleBrowser.app
```

### 自定义DMG外观

可以添加自定义DMG背景和布局：

```yaml
- name: Create custom DMG
  run: |
    # 创建自定义DMG的脚本
    ./create_custom_dmg.sh
```

## 📊 构建监控

### 查看构建状态

在README中添加构建状态徽章：
```markdown
![macOS Build](https://github.com/zhangzhiran/linken-sphere-apple-browser/workflows/Build%20macOS%20Distribution%20Package/badge.svg)
```

### 构建通知

可以配置构建完成通知：
- GitHub通知
- 邮件通知
- Slack通知

## 🚨 故障排除

### 常见问题

1. **构建失败**: 检查Actions日志中的错误信息
2. **文件缺失**: 确保所有必需文件都在仓库中
3. **权限问题**: 检查仓库的Actions权限设置
4. **依赖问题**: 更新requirements.txt或修复依赖冲突

### 调试技巧

1. **本地测试**: 先在本地macOS上测试构建脚本
2. **分步调试**: 在工作流中添加调试输出
3. **缓存清理**: 有时需要清理GitHub Actions缓存

## 💡 最佳实践

1. **版本管理**: 使用语义化版本标签
2. **测试**: 在发布前充分测试
3. **文档**: 保持用户文档更新
4. **备份**: 重要版本创建Release备份
5. **监控**: 定期检查构建状态

## 🎉 总结

通过这个GitHub Actions工作流，您可以：

✅ **零成本**: 使用GitHub免费的macOS构建环境
✅ **零配置**: 用户无需安装任何开发工具
✅ **自动化**: 推送代码即可自动构建
✅ **专业**: 生成标准的macOS应用包
✅ **便捷**: 一键下载，直接分发

现在您可以专注于开发，让GitHub Actions处理所有的构建和分发工作！🚀
