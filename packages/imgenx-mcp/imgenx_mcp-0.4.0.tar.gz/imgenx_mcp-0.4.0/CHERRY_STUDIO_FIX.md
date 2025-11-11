# 🔧 Cherry Studio 配置修复指南

## ❌ 问题分析

错误信息：`Error invoking remote method 'mcp:list-tools': McpError: MCP error -32000: Connection closed`

**原因：** 之前的配置使用了错误的命令 `imgenx-mcp`，但实际的可执行文件名是 `imgenx`。

---

## ✅ 解决方案

我为您提供了两个解决方案，推荐使用方案 2（更稳定）。

---

### 方案 1: 使用 uvx（无需安装）

**配置文件：cherry_studio_config_fixed.json**

```json
{
  "mcpServers": {
    "imgenx": {
      "command": "uvx",
      "args": ["--from", "imgenx-mcp", "imgenx", "server"],
      "env": {
        "IMGENX_IMAGE_MODEL": "doubao:doubao-seedream-4-0-250828",
        "IMGENX_VIDEO_MODEL": "doubao:doubao-seedance-1-0-pro-fast-251015",
        "IMGENX_ANALYZER_MODEL": "doubao:doubao-seed-1-6-vision-250815",
        "IMGENX_API_KEY": "ebabd2d9-c0c6-44a4-9ec6-0656fc81d496",
        "OSS_ACCESS_KEY_ID": "LTAI5t8WoXY2sYaMt9NUk2YM",
        "OSS_ACCESS_KEY_SECRET": "HUKE4Bu0WYtT2hJixNlwj69pbi0ZXf",
        "OSS_BUCKET": "dev-res-tishi",
        "OSS_ENDPOINT": "oss-cn-shanghai.aliyuncs.com",
        "OSS_CDN_URL": "https://dev-res.tishiii.com/"
      },
      "timeout": 600
    }
  }
}
```

**优点：**
- 无需手动安装
- uvx 会自动管理虚拟环境

**缺点：**
- 首次运行需要下载依赖（约 3 秒）
- 可能在某些网络环境下较慢

---

### 方案 2: 使用 pip 安装（推荐）⭐

**步骤 1：安装包**

```bash
pip install imgenx-mcp
```

**步骤 2：使用配置文件**

**配置文件：cherry_studio_config_pip.json**

```json
{
  "mcpServers": {
    "imgenx": {
      "command": "python",
      "args": ["-m", "imgenx.main"],
      "env": {
        "IMGENX_IMAGE_MODEL": "doubao:doubao-seedream-4-0-250828",
        "IMGENX_VIDEO_MODEL": "doubao:doubao-seedance-1-0-pro-fast-251015",
        "IMGENX_ANALYZER_MODEL": "doubao:doubao-seed-1-6-vision-250815",
        "IMGENX_API_KEY": "ebabd2d9-c0c6-44a4-9ec6-0656fc81d496",
        "OSS_ACCESS_KEY_ID": "LTAI5t8WoXY2sYaMt9NUk2YM",
        "OSS_ACCESS_KEY_SECRET": "HUKE4Bu0WYtT2hJixNlwj69pbi0ZXf",
        "OSS_BUCKET": "dev-res-tishi",
        "OSS_ENDPOINT": "oss-cn-shanghai.aliyuncs.com",
        "OSS_CDN_URL": "https://dev-res.tishiii.com/"
      },
      "timeout": 600
    }
  }
}
```

**优点：**
- ✅ 启动速度快
- ✅ 更稳定
- ✅ 离线可用
- ✅ 推荐使用

**缺点：**
- 需要手动安装包
- 需要手动更新版本

---

## 🚀 详细步骤（方案 2 - 推荐）

### 1. 安装 imgenx-mcp

打开命令行，运行：

```bash
pip install imgenx-mcp
```

等待安装完成（约 10-20 秒）。

### 2. 验证安装

```bash
python -c "import imgenx; print('安装成功！')"
```

如果看到 "安装成功！"，说明安装正确。

### 3. 配置 Cherry Studio

打开 Cherry Studio → 设置 → MCP 服务器 → 添加服务器

复制 `cherry_studio_config_pip.json` 的内容，粘贴到配置中。

### 4. 保存并重启 Cherry Studio

点击保存，然后重启 Cherry Studio。

### 5. 验证连接

重启后，在 Cherry Studio 中应该能看到 `imgenx` MCP 服务器，包含 14 个工具。

---

## 🧪 测试命令

### 测试方案 1（uvx）

```bash
uvx --from imgenx-mcp imgenx --help
```

### 测试方案 2（pip）

```bash
python -m imgenx.main --help
```

---

## 🔍 常见问题

### Q1: 仍然报错 "Connection closed"

**解决方法：**

1. **检查 Python 版本**（需要 >= 3.10）
   ```bash
   python --version
   ```

2. **检查包是否安装**
   ```bash
   pip show imgenx-mcp
   ```

3. **查看 Cherry Studio 日志**
   - Windows: `%APPDATA%\cherry-studio\logs`
   - macOS: `~/Library/Logs/cherry-studio`
   - Linux: `~/.local/share/cherry-studio/logs`

4. **尝试手动运行**
   ```bash
   python -m imgenx.main server
   ```

   如果能运行，说明安装正确，问题可能在 Cherry Studio 配置。

### Q2: 提示找不到 python 命令

**Windows 用户：**

如果提示找不到 `python`，可能需要使用 `python3`：

```json
{
  "command": "python3",
  "args": ["-m", "imgenx.main"]
}
```

或者使用完整路径：

```json
{
  "command": "C:\\Python310\\python.exe",
  "args": ["-m", "imgenx.main"]
}
```

### Q3: OSS 上传失败

**检查项：**
1. 确认 OSS 凭证正确
2. 确认网络连接正常
3. 确认 Bucket 权限

---

## 📊 配置对比

| 特性 | 方案 1 (uvx) | 方案 2 (pip) |
|------|-------------|--------------|
| 安装 | 无需安装 | 需要安装 |
| 启动速度 | 慢（首次） | 快 |
| 稳定性 | 中等 | 高 |
| 离线使用 | ❌ | ✅ |
| 推荐度 | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

---

## 🎯 推荐使用方案 2

**步骤总结：**

1. 运行：`pip install imgenx-mcp`
2. 使用配置：`cherry_studio_config_pip.json`
3. 重启 Cherry Studio
4. 开始使用

---

## 📞 获取更多帮助

如果问题仍未解决：

1. 检查 Cherry Studio 官方文档
2. 查看项目 GitHub Issues: https://github.com/Zluowa/imgenx-mcp/issues
3. 提供以下信息：
   - Python 版本
   - Cherry Studio 版本
   - 完整错误日志
   - 操作系统版本

---

**🎉 修复完成后，您就可以在 Cherry Studio 中使用所有 14 个 imgenx 工具了！**
