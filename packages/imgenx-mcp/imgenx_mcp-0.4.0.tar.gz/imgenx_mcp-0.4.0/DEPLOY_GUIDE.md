# 🚀 发布步骤指南

## ✅ 当前状态

已完成：
- ✅ Git 仓库已初始化
- ✅ 代码已提交（commit: 5600901）
- ✅ Python 包已构建
  - `dist/imgenx_mcp-0.3.0.tar.gz` (456KB)
  - `dist/imgenx_mcp-0.3.0-py3-none-any.whl` (21KB)
- ✅ 包验证通过

---

## 📋 接下来的步骤

### 步骤 1: 创建 GitHub 仓库

1. **访问 GitHub 创建新仓库**
   - 打开：https://github.com/new
   - 或者访问：https://github.com/helios123?tab=repositories 点击 "New"

2. **填写仓库信息**
   ```
   Repository name: imgenx-mcp
   Description: AI Image/Video Generation MCP Server with OSS Upload - Powered by Doubao API

   选项：
   ✅ Public（公开仓库，才能发布到PyPI）
   ❌ 不要勾选 "Add a README file"
   ❌ 不要勾选 "Add .gitignore"
   ❌ 不要选择 License（我们已经有了）
   ```

3. **创建仓库后，复制仓库 URL**
   - 应该是：`https://github.com/helios123/imgenx-mcp.git`

4. **推送代码到 GitHub**

   在命令行运行：
   ```bash
   cd D:\20251110-jimengmcp\imgenx-main\imgenx-main

   git remote add origin https://github.com/helios123/imgenx-mcp.git
   git branch -M main
   git push -u origin main
   ```

---

### 步骤 2: 注册 PyPI 账号（如果还没有）

1. **访问 PyPI 注册页面**
   - https://pypi.org/account/register/

2. **填写注册信息**
   - Username: helios123（建议与GitHub一致）
   - Email: 你的邮箱
   - Password: 设置密码

3. **验证邮箱**
   - 检查邮件并点击验证链接

---

### 步骤 3: 创建 PyPI API Token

1. **登录 PyPI**
   - https://pypi.org/

2. **进入账户设置**
   - 点击右上角你的用户名
   - 选择 "Account settings"

3. **创建 API Token**
   - 滚动到 "API tokens" 部分
   - 点击 "Add API token"
   - Token name: `imgenx-mcp-upload`
   - Scope: "Entire account" (首次上传必须选这个)
   - 点击 "Add token"

4. **复制 Token**
   - **重要**: Token 只显示一次，立即复制保存！
   - 格式类似：`pypi-AgEIcHlwaS5vcmc...`

---

### 步骤 4: 配置 PyPI 凭证

**方法 A: 使用 .pypirc 文件（推荐）**

创建文件 `~/.pypirc`（Windows: `%USERPROFILE%\.pypirc`）：

```ini
[pypi]
username = __token__
password = pypi-你的token内容
```

**方法 B: 环境变量**

```bash
# Windows PowerShell
$env:TWINE_USERNAME = "__token__"
$env:TWINE_PASSWORD = "pypi-你的token内容"

# Windows CMD
set TWINE_USERNAME=__token__
set TWINE_PASSWORD=pypi-你的token内容

# Linux/Mac
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=pypi-你的token内容
```

---

### 步骤 5: 上传到 Test PyPI（可选，建议测试）

测试环境可以先验证流程：

```bash
cd D:\20251110-jimengmcp\imgenx-main\imgenx-main

# 上传到 Test PyPI
python -m twine upload --repository testpypi dist/*
```

测试安装：
```bash
pip install --index-url https://test.pypi.org/simple/ --no-deps imgenx-mcp
```

---

### 步骤 6: 上传到 PyPI（正式发布）

```bash
cd D:\20251110-jimengmcp\imgenx-main\imgenx-main

# 正式上传
python -m twine upload dist/*
```

会看到：
```
Uploading distributions to https://upload.pypi.org/legacy/
Uploading imgenx_mcp-0.3.0-py3-none-any.whl
100% ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 21.5/21.5 kB • 00:01 • ?
Uploading imgenx_mcp-0.3.0.tar.gz
100% ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 456.0/456.0 kB • 00:02 • ?

View at:
https://pypi.org/project/imgenx-mcp/0.3.0/
```

---

### 步骤 7: 验证发布

1. **访问 PyPI 页面**
   - https://pypi.org/project/imgenx-mcp/

2. **测试安装**
   ```bash
   pip install imgenx-mcp
   ```

3. **验证版本**
   ```bash
   pip show imgenx-mcp
   ```

---

### 步骤 8: 创建 GitHub Release

1. **在 GitHub 仓库页面**
   - 访问：https://github.com/helios123/imgenx-mcp
   - 点击右侧 "Releases" -> "Create a new release"

2. **填写 Release 信息**
   ```
   Tag version: v0.3.0
   Release title: v0.3.0 - Add OSS Upload Support

   Description:
   ## 🎉 New Features
   - Add aliyun OSS upload integration
   - Add `upload_to_oss` and `download_and_upload_to_oss` tools
   - Add CDN acceleration support

   ## ⚡ Performance
   - Optimize upload performance (35% faster)
   - Remove unnecessary file verification

   ## 📚 Documentation
   - Add comprehensive OSS usage guide
   - Add quick start guide
   - Add performance optimization docs

   ## 📦 Installation
   ```bash
   pip install imgenx-mcp
   ```

   See [README](https://github.com/helios123/imgenx-mcp/blob/main/README.md) for usage instructions.
   ```

3. **发布 Release**
   - 点击 "Publish release"

---

## 🎯 完整命令速查

```bash
# 1. 推送到 GitHub
cd D:\20251110-jimengmcp\imgenx-main\imgenx-main
git remote add origin https://github.com/helios123/imgenx-mcp.git
git branch -M main
git push -u origin main

# 2. 发布到 PyPI
python -m twine upload dist/*

# 3. 创建 Git tag
git tag -a v0.3.0 -m "Release v0.3.0 - Add OSS upload support"
git push origin v0.3.0
```

---

## ❓ 常见问题

### Q: 包名已存在怎么办？

如果 `imgenx-mcp` 已被占用，需要更改包名：

1. 修改 `pyproject.toml` 中的 `name`
2. 重新构建：`python -m build`
3. 上传新包名

### Q: 上传失败：403 Forbidden

原因：
- Token 权限不足
- 包名已存在且你无权限

解决：
- 检查 Token 是否正确
- 尝试不同的包名

### Q: 如何更新版本？

1. 修改 `pyproject.toml` 中的 `version`
2. 提交代码
3. 重新构建和上传

```bash
# 修改版本号
# version = "0.3.1"

# 清理旧构建
rm -rf dist/

# 重新构建
python -m build

# 上传新版本
python -m twine upload dist/*
```

---

## ✅ 检查清单

发布前确认：

- [ ] GitHub 仓库已创建
- [ ] 代码已推送到 GitHub
- [ ] PyPI 账号已注册
- [ ] API Token 已创建
- [ ] 凭证已配置（.pypirc 或环境变量）
- [ ] 包已构建（dist/ 目录）
- [ ] 包已验证（twine check）
- [ ] 准备好上传

发布后确认：

- [ ] PyPI 页面正常显示
- [ ] 可以通过 pip 安装
- [ ] GitHub Release 已创建
- [ ] Git tag 已推送
- [ ] 文档更新完整

---

## 📞 需要帮助？

如遇到问题，可以：

1. 查看 PyPI 文档：https://packaging.python.org/
2. 查看 Twine 文档：https://twine.readthedocs.io/
3. 检查 GitHub Actions 日志（如果配置了自动发布）

---

**准备好后，按照步骤 1-6 依次执行即可！** 🚀
