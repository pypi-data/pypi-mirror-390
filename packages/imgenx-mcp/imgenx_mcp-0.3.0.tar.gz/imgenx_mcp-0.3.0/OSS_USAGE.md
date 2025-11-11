# 阿里云 OSS 上传功能使用说明

## 📦 已完成的工作

1. ✅ 安装了 `oss2` SDK（Python 阿里云 OSS SDK）
2. ✅ 配置了阿里云 OSS（使用 Huadan 项目的配置）
3. ✅ 实现了直接上传到 OSS 的功能
4. ✅ 添加了两个 MCP 工具函数
5. ✅ 完成测试并验证功能正常

---

## 🔧 配置信息

### 环境变量（.env 文件）

```bash
# 图片视频生成模型配置
IMGENX_IMAGE_MODEL=doubao:doubao-seedream-4-0-250828
IMGENX_VIDEO_MODEL=doubao-video-generator
IMGENX_ANALYZER_MODEL=doubao-image-analyzer
IMGENX_API_KEY=ebabd2d9-c0c6-44a4-9ec6-0656fc81d496

# 阿里云 OSS 配置（来自 Huadan 项目）
OSS_ACCESS_KEY_ID=LTAI5t8WoXY2sYaMt9NUk2YM
OSS_ACCESS_KEY_SECRET=HUKE4Bu0WYtT2hJixNlwj69pbi0ZXf
OSS_BUCKET=dev-res-tishi
OSS_ENDPOINT=oss-cn-shanghai.aliyuncs.com
OSS_CDN_URL=https://dev-res.tishiii.com/
```

---

## 🚀 核心功能

### 1. OSSService 类

位置: `imgenx/oss_service.py`

**主要方法：**

```python
from imgenx.oss_service import get_oss_service

# 获取 OSS 服务实例
oss_service = get_oss_service()

# 上传本地文件
result = oss_service.upload_file(
    file_path='./image.jpg',
    business_dir='images'  # 可选：images, videos, data 等
)

# 上传字节数据
result = oss_service.upload_bytes(
    data=image_bytes,
    filename='photo.jpg',
    business_dir='images'
)

# 删除文件
success = oss_service.delete_file('images/202511/xxx.jpg')

# 检查文件是否存在
exists = oss_service.file_exists('images/202511/xxx.jpg')

# 获取文件 URL
url = oss_service.get_file_url('images/202511/xxx.jpg', use_cdn=True)
```

**返回结果格式：**

```python
{
    'object_key': 'images/202511/1762774964687_07d21332.jpg',
    'oss_url': 'https://dev-res-tishi.oss-cn-shanghai.aliyuncs.com/images/202511/xxx.jpg',
    'cdn_url': 'https://dev-res.tishiii.com/images/202511/xxx.jpg',
    'status': 200
}
```

---

### 2. MCP 工具函数

位置: `imgenx/server.py`

#### 工具 1: `upload_to_oss`

上传本地文件到 OSS

```python
@mcp.tool
def upload_to_oss(file_path: str, business_dir: str = 'images') -> Dict[str, str]:
    '''上传文件到阿里云 OSS，生成图片或视频后建议调用此工具上传文件。

    Args:
        file_path (str): 本地文件路径
        business_dir (str): 业务目录，默认 'images'，可选 'videos', 'data' 等

    Returns:
        Dict[str, str]: 包含 object_key、oss_url、cdn_url
    '''
```

**使用示例：**
```bash
# 在 MCP 客户端中调用
upload_to_oss(file_path="/path/to/image.jpg", business_dir="images")
```

#### 工具 2: `download_and_upload_to_oss`

下载图片/视频并直接上传到 OSS

```python
@mcp.tool
def download_and_upload_to_oss(url: str, business_dir: str = 'images') -> Dict[str, str]:
    '''下载图片或视频并直接上传到 OSS，无需先保存到本地。
    生成图片或视频后可以直接调用此工具完成下载和上传。

    Args:
        url (str): 图片或视频的下载 URL
        business_dir (str): 业务目录，默认 'images'，可选 'videos', 'data' 等

    Returns:
        Dict[str, str]: 包含 object_key、oss_url、cdn_url
    '''
```

**使用示例：**
```bash
# 在 MCP 客户端中调用
download_and_upload_to_oss(
    url="https://example.com/generated_image.jpg",
    business_dir="images"
)
```

---

## 📂 文件存储路径规则

**路径格式：** `{business_dir}/{YYYYMM}/{timestamp}_{uuid}.{ext}`

**示例：**
```
images/202511/1762774964687_07d21332.jpg
videos/202511/1762774966071_8027ecc3.mp4
data/202511/1762774968234_abc12345.txt
```

**说明：**
- `business_dir`: 业务目录（images, videos, data 等）
- `YYYYMM`: 年月（例如：202511）
- `timestamp`: 毫秒级时间戳
- `uuid`: 8位随机 UUID
- `ext`: 文件扩展名

---

## 🧪 测试

运行测试脚本验证功能：

```bash
cd imgenx-main/imgenx-main
.venv/Scripts/python test_oss.py
```

**测试内容：**
1. ✅ OSS 配置检查
2. ✅ 文件上传测试
3. ✅ 字节数据上传测试
4. ✅ 文件删除测试

---

## 🔗 访问 URL

上传成功后会返回两个 URL：

1. **OSS URL（直接访问）：**
   ```
   https://dev-res-tishi.oss-cn-shanghai.aliyuncs.com/images/202511/xxx.jpg
   ```

2. **CDN URL（推荐使用，加速访问）：**
   ```
   https://dev-res.tishiii.com/images/202511/xxx.jpg
   ```

---

## 📋 使用流程示例

### 场景 1: 生成图片并上传

```python
# 1. 生成图片
result = text_to_image(prompt="一只可爱的猫", size="2K")
image_url = result[0]['url']

# 2. 下载并上传到 OSS
oss_result = download_and_upload_to_oss(url=image_url, business_dir="images")

# 3. 获取 CDN URL
cdn_url = oss_result['cdn_url']
print(f"图片已上传: {cdn_url}")
```

### 场景 2: 本地文件上传

```python
# 1. 下载图片到本地
download(url="https://example.com/image.jpg", path="/tmp/image.jpg")

# 2. 上传到 OSS
oss_result = upload_to_oss(file_path="/tmp/image.jpg", business_dir="images")

# 3. 获取 CDN URL
cdn_url = oss_result['cdn_url']
print(f"图片已上传: {cdn_url}")
```

---

## 🔒 安全说明

- ⚠️ `.env` 文件包含敏感信息（AccessKey、Secret），**请勿提交到 Git**
- ⚠️ 生产环境建议使用 STS 临时凭证或 RAM 角色
- ⚠️ 建议为 OSS Bucket 配置访问控制和防盗链

---

## 📚 相关文档

- [阿里云 OSS Python SDK 文档](https://help.aliyun.com/document_detail/32026.html)
- [oss2 PyPI 页面](https://pypi.org/project/oss2/)
- [Huadan 项目 OSS 配置](../huadan-backend-feature/src/main/resources/application-dev.yml)

---

## ✨ 功能特性

- ✅ 自动生成唯一文件名（时间戳 + UUID）
- ✅ 按年月目录自动分类
- ✅ 支持 CDN 加速访问
- ✅ 支持本地文件和字节数据上传
- ✅ 支持直接下载 URL 并上传
- ✅ 完整的错误处理
- ✅ 文件存在性检查
- ✅ 文件删除功能

---

## 🆘 常见问题

### Q1: 上传失败怎么办？

**检查项：**
1. 确认 `.env` 文件配置正确
2. 确认网络连接正常
3. 确认 OSS AccessKey 权限
4. 查看错误日志

### Q2: 如何更改存储路径？

修改 `business_dir` 参数即可：
```python
upload_to_oss(file_path="xxx.jpg", business_dir="custom_dir")
```

### Q3: 如何使用其他 OSS Bucket？

修改 `.env` 文件中的 OSS 配置：
```bash
OSS_BUCKET=your-bucket-name
OSS_ENDPOINT=oss-cn-beijing.aliyuncs.com
```

---

## 📞 联系方式

如有问题，请联系开发团队或查看 Huadan 项目文档。
