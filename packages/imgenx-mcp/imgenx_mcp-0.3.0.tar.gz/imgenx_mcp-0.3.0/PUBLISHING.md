# 发布到 PyPI 指南

## 准备工作

### 1. 安装构建工具

```bash
pip install build twine
```

### 2. 注册 PyPI 账号

如果还没有 PyPI 账号，访问 https://pypi.org/account/register/ 注册。

### 3. 配置 PyPI Token

创建 `~/.pypirc` 文件：

```ini
[pypi]
  username = __token__
  password = pypi-your-token-here
```

或使用 keyring:
```bash
pip install keyring
keyring set https://upload.pypi.org/legacy/ __token__
```

## 发布步骤

### 1. 更新版本号

编辑 `pyproject.toml`，更新 `version` 字段：

```toml
version = "0.3.0"
```

### 2. 清理旧构建

```bash
rm -rf dist/ build/ *.egg-info
```

### 3. 构建分发包

```bash
python -m build
```

这将在 `dist/` 目录生成：
- `imgenx_mcp-0.3.0.tar.gz` (源码包)
- `imgenx_mcp-0.3.0-py3-none-any.whl` (wheel包)

### 4. 检查包

```bash
twine check dist/*
```

### 5. 上传到 Test PyPI（测试）

```bash
twine upload --repository testpypi dist/*
```

测试安装：
```bash
pip install --index-url https://test.pypi.org/simple/ imgenx-mcp
```

### 6. 上传到 PyPI（正式发布）

```bash
twine upload dist/*
```

### 7. 验证发布

访问 https://pypi.org/project/imgenx-mcp/ 确认包已发布。

测试安装：
```bash
pip install imgenx-mcp
```

## 发布检查清单

在发布前确认：

- [ ] 所有测试通过
- [ ] 更新了版本号
- [ ] 更新了 CHANGELOG
- [ ] 更新了 README
- [ ] 清理了临时文件
- [ ] 创建了 git tag

```bash
git tag -a v0.3.0 -m "Release version 0.3.0"
git push origin v0.3.0
```

## 自动化发布（可选）

### 使用 GitHub Actions

创建 `.github/workflows/publish.yml`:

```yaml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install build twine
    - name: Build package
      run: python -m build
    - name: Publish to PyPI
      env:
        TWINE_USERNAME: __token__
        TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
      run: twine upload dist/*
```

在 GitHub 仓库设置中添加 Secret: `PYPI_API_TOKEN`

## 发布后

1. 在 GitHub 创建 Release
2. 更新文档链接
3. 通知用户更新

```bash
pip install --upgrade imgenx-mcp
```

## 常见问题

### Q: 包名已存在

如果包名 `imgenx-mcp` 已被占用，需要更改包名，或联系原作者转移。

### Q: 上传失败

检查：
- PyPI Token 是否正确
- 网络连接是否正常
- 版本号是否已存在

### Q: 如何删除已发布的版本

PyPI 不允许删除或覆盖已发布的版本，只能发布新版本。

## 参考资料

- [Python Packaging 用户指南](https://packaging.python.org/)
- [Twine 文档](https://twine.readthedocs.io/)
- [PyPI 文档](https://pypi.org/help/)
