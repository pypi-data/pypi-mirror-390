# Cherry Studio 配置说明

## 📋 配置文件

配置文件已创建：`cherry_studio_config.json`

---

## 🚀 使用方法

### 步骤 1: 找到 Cherry Studio 配置文件

Cherry Studio 的 MCP 配置文件位置：
- **Windows**: `%APPDATA%\cherry-studio\mcp_config.json`
- **macOS**: `~/Library/Application Support/cherry-studio/mcp_config.json`
- **Linux**: `~/.config/cherry-studio/mcp_config.json`

### 步骤 2: 复制配置内容

将 `cherry_studio_config.json` 的内容复制到 Cherry Studio 的配置文件中。

**或者直接在 Cherry Studio UI 中添加：**
1. 打开 Cherry Studio
2. 进入设置 → MCP 服务器
3. 点击"添加服务器"
4. 粘贴配置内容

### 步骤 3: 配置 OSS（可选）

如果您需要使用 OSS 上传功能，请将配置中的 OSS 凭证替换为真实的：

```json
"OSS_ACCESS_KEY_ID": "你的真实AccessKeyId",
"OSS_ACCESS_KEY_SECRET": "你的真实AccessKeySecret"
```

如果不使用 OSS，可以删除这些环境变量，或保持占位符。

### 步骤 4: 重启 Cherry Studio

保存配置后，重启 Cherry Studio 使配置生效。

---

## ✅ 验证配置

重启后，在 Cherry Studio 中应该能看到 `imgenx` MCP 服务器，包含以下 14 个工具：

### 🎨 图片生成
1. **text_to_image** - 文字生成图片
2. **image_to_image** - 图片生成图片

### 🎬 视频生成
3. **text_to_video** - 文字生成视频
4. **image_to_video** - 图片生成视频

### 🔍 图片分析
5. **analyze_image** - AI 分析图片内容
6. **get_image_info** - 获取图片信息

### ✂️ 图片编辑
7. **crop_image** - 裁剪图片
8. **resize_image** - 调整大小
9. **convert_image** - 格式转换
10. **adjust_image** - 调整亮度/对比度/饱和度
11. **paste_image** - 图片合成

### ☁️ OSS 上传
12. **upload_to_oss** - 上传本地文件
13. **download_and_upload_to_oss** - 下载并上传

### 📥 下载
14. **download** - 下载文件到本地

---

## 💡 使用示例

配置完成后，您可以在 Cherry Studio 中直接使用：

```
生成一只小猫在天上飞的图片
```

```
把这张图片上传到 OSS
```

```
生成一个日落海滩的视频，5秒，1080p
```

```
分析这张图片的内容
```

---

## 🔧 配置详解

```json
{
  "mcpServers": {
    "imgenx": {
      // 使用 uvx 运行（推荐，无需安装）
      "command": "uvx",
      "args": ["imgenx-mcp"],

      // 环境变量配置
      "env": {
        // 图片生成模型（Doubao）
        "IMGENX_IMAGE_MODEL": "doubao:doubao-seedream-4-0-250828",

        // 视频生成模型
        "IMGENX_VIDEO_MODEL": "doubao-video-generator",

        // 图片分析模型
        "IMGENX_ANALYZER_MODEL": "doubao-image-analyzer",

        // 您的 API Key（已配置）
        "IMGENX_API_KEY": "ebabd2d9-c0c6-44a4-9ec6-0656fc81d496",

        // 阿里云 OSS 配置（需要替换为真实凭证）
        "OSS_ACCESS_KEY_ID": "your_oss_access_key_id_here",
        "OSS_ACCESS_KEY_SECRET": "your_oss_access_key_secret_here",
        "OSS_BUCKET": "dev-res-tishi",
        "OSS_ENDPOINT": "oss-cn-shanghai.aliyuncs.com",
        "OSS_CDN_URL": "https://dev-res.tishiii.com/"
      },

      // 超时时间（秒），视频生成可能需要较长时间
      "timeout": 600
    }
  }
}
```

---

## 📦 其他安装方式

如果您不想使用 `uvx`，也可以先安装包：

### 方式 1: 使用 pip
```bash
pip install imgenx-mcp
```

然后修改配置：
```json
{
  "command": "python",
  "args": ["-m", "imgenx.main"],
  "env": { ... }
}
```

### 方式 2: 从 GitHub 安装
```bash
pip install git+https://github.com/Zluowa/imgenx-mcp.git
```

---

## ⚠️ 注意事项

1. **API Key 安全**
   - 配置文件包含您的真实 API Key
   - 请勿分享或提交到公开仓库

2. **OSS 配置**
   - 如果不使用 OSS 功能，可以忽略 OSS 相关配置
   - 使用 OSS 功能需要替换为真实的 AccessKey 和 Secret

3. **网络要求**
   - 需要能够访问 Doubao API 和阿里云 OSS
   - 首次运行会自动安装依赖（使用 uvx 时）

---

## 🆘 故障排查

### 问题 1: Cherry Studio 中看不到服务器

**解决方法：**
1. 检查配置文件路径是否正确
2. 检查 JSON 格式是否正确（使用 JSON 验证工具）
3. 查看 Cherry Studio 日志

### 问题 2: 工具调用失败

**解决方法：**
1. 检查 API Key 是否正确
2. 检查网络连接
3. 查看错误信息

### 问题 3: OSS 上传失败

**解决方法：**
1. 确认已配置真实的 OSS 凭证
2. 检查 OSS Bucket 权限
3. 验证网络连接

---

## 🔗 相关链接

- **GitHub**: https://github.com/Zluowa/imgenx-mcp
- **PyPI**: https://pypi.org/project/imgenx-mcp/
- **文档**: https://github.com/Zluowa/imgenx-mcp/blob/main/README.md

---

## 📞 获取帮助

如有问题，请：
1. 查看项目 README
2. 在 GitHub 提交 Issue
3. 查看 Cherry Studio 官方文档

---

**🎉 配置完成后，您就可以在 Cherry Studio 中使用所有 14 个 imgenx 工具了！**
