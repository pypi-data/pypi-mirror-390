# 快速开始指南

## 🚀 5 分钟开始使用 imgenx-mcp

### 步骤 1: 获取 API Key

访问 [火山引擎控制台](https://console.volcengine.com/) 获取豆包 API Key。

### 步骤 2: 配置 Claude Desktop

**找到配置文件：**
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Linux: `~/.config/Claude/claude_desktop_config.json`

**添加配置：**

```json
{
  "mcpServers": {
    "imgenx": {
      "command": "uvx",
      "args": ["imgenx-mcp"],
      "env": {
        "IMGENX_IMAGE_MODEL": "doubao:doubao-seedream-4-0-250828",
        "IMGENX_API_KEY": "你的API_KEY"
      },
      "timeout": 600
    }
  }
}
```

### 步骤 3: 重启 Claude Desktop

关闭并重新打开 Claude Desktop。

### 步骤 4: 开始使用！

在 Claude 中输入：

```
生成一只小猫在天上飞的图片
```

Claude 将自动调用 imgenx MCP 服务生成图片并返回 URL！

---

## 📸 添加 OSS 上传（可选）

如果你想把生成的图片自动上传到阿里云 OSS：

### 步骤 1: 获取 OSS 凭证

访问 [阿里云 RAM 控制台](https://ram.console.aliyun.com/) 创建 AccessKey。

### 步骤 2: 更新配置

在 Claude Desktop 配置中添加 OSS 环境变量：

```json
{
  "mcpServers": {
    "imgenx": {
      "command": "uvx",
      "args": ["imgenx-mcp"],
      "env": {
        "IMGENX_IMAGE_MODEL": "doubao:doubao-seedream-4-0-250828",
        "IMGENX_API_KEY": "你的API_KEY",
        "OSS_ACCESS_KEY_ID": "你的OSS_KEY",
        "OSS_ACCESS_KEY_SECRET": "你的OSS_SECRET",
        "OSS_BUCKET": "你的bucket名称",
        "OSS_ENDPOINT": "oss-cn-shanghai.aliyuncs.com",
        "OSS_CDN_URL": "https://your-cdn.com/"
      },
      "timeout": 600
    }
  }
}
```

### 步骤 3: 使用上传功能

```
生成一只小猫的图片，然后上传到OSS
```

Claude 会生成图片并上传，返回 CDN 地址！

---

## 🎯 常用命令示例

### 图片生成

```
生成一个日落时的海滩，2K分辨率
```

```
根据这张图片生成一个类似风格的图片（上传图片）
```

### 视频生成

```
生成一个5秒的日落视频，1080p
```

### 图片编辑

```
把这张图片调整为1920x1080
```

```
把图片转换为webp格式
```

### OSS 上传

```
把刚才生成的图片上传到OSS
```

---

## ❓ 常见问题

### Q1: MCP 服务无法启动？

**检查：**
1. Claude Desktop 是否最新版本
2. 配置文件 JSON 格式是否正确
3. API Key 是否有效

**查看日志：**
- Windows: `%APPDATA%\Claude\logs\`
- macOS: `~/Library/Logs/Claude/`

### Q2: 图片生成失败？

**可能原因：**
- API Key 无效或过期
- 模型名称错误
- 网络连接问题

**解决：**
检查配置中的 `IMGENX_API_KEY` 和 `IMGENX_IMAGE_MODEL`

### Q3: OSS 上传失败？

**可能原因：**
- OSS 凭证错误
- Bucket 不存在
- 无上传权限

**解决：**
验证 OSS 配置是否正确，检查 RAM 权限

### Q4: 如何只使用图片生成，不用OSS？

**答：**
只配置图片生成相关的环境变量即可，OSS 配置是可选的：

```json
{
  "env": {
    "IMGENX_IMAGE_MODEL": "doubao:doubao-seedream-4-0-250828",
    "IMGENX_API_KEY": "你的API_KEY"
  }
}
```

---

## 📚 更多资源

- [完整 README](./README.md)
- [OSS 上传详细说明](./OSS_USAGE.md)
- [性能优化指南](./PERFORMANCE_OPTIMIZATION.md)
- [发布指南](./PUBLISHING.md)

---

## 💬 获取帮助

遇到问题？

1. 查看 [GitHub Issues](https://github.com/helios123/imgenx-mcp/issues)
2. 提交新的 Issue
3. 查看 MCP 官方文档

---

**现在开始使用 imgenx-mcp，让 AI 为你创作精彩图片和视频！** 🎨✨
