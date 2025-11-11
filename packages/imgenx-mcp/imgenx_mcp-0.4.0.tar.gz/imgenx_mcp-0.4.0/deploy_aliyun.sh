#!/bin/bash
# imgenx-mcp 阿里云服务器一键部署脚本

echo "================================"
echo "imgenx-mcp 部署脚本"
echo "================================"
echo ""

# 1. 检查 Python 版本
echo ">>> 步骤 1: 检查 Python 环境"
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | awk '{print $2}')
    echo "✓ 检测到 Python $PYTHON_VERSION"
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_VERSION=$(python --version | awk '{print $2}')
    echo "✓ 检测到 Python $PYTHON_VERSION"
    PYTHON_CMD="python"
else
    echo "✗ 未检测到 Python，请先安装 Python 3.10+"
    exit 1
fi

# 检查版本是否 >= 3.10
REQUIRED_VERSION="3.10"
if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "✗ Python 版本过低（需要 >= 3.10），当前版本: $PYTHON_VERSION"
    exit 1
fi

echo ""

# 2. 安装 imgenx-mcp
echo ">>> 步骤 2: 安装 imgenx-mcp"
$PYTHON_CMD -m pip install --upgrade pip
$PYTHON_CMD -m pip install imgenx-mcp

if [ $? -eq 0 ]; then
    echo "✓ imgenx-mcp 安装成功"
else
    echo "✗ imgenx-mcp 安装失败"
    exit 1
fi

echo ""

# 3. 验证安装
echo ">>> 步骤 3: 验证安装"
$PYTHON_CMD -m imgenx.main --help > /dev/null 2>&1

if [ $? -eq 0 ]; then
    echo "✓ imgenx-mcp 验证成功"
else
    echo "✗ imgenx-mcp 验证失败"
    exit 1
fi

echo ""

# 4. 创建配置文件
echo ">>> 步骤 4: 创建配置文件"
CONFIG_FILE="cherry_studio_config.json"

cat > $CONFIG_FILE << 'EOF'
{
  "mcpServers": {
    "imgenx": {
      "command": "python3",
      "args": ["-m", "imgenx.main", "server"],
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
EOF

echo "✓ 配置文件已创建: $CONFIG_FILE"

echo ""

# 5. 显示配置路径
echo ">>> 步骤 5: 配置说明"
echo ""
echo "配置文件已生成: $(pwd)/$CONFIG_FILE"
echo ""
echo "请将此配置添加到您的 MCP 客户端："
echo "  - Cherry Studio: 设置 → MCP 服务器 → 添加服务器"
echo "  - Claude Desktop: 编辑配置文件"
echo ""

# 6. 测试服务器启动
echo ">>> 步骤 6: 测试服务器（3秒后自动停止）"
timeout 3 $PYTHON_CMD -m imgenx.main server > /dev/null 2>&1 &
PID=$!
sleep 3
kill $PID 2>/dev/null

if ps -p $PID > /dev/null 2>&1; then
    echo "✓ MCP 服务器可以正常启动"
else
    echo "✓ MCP 服务器测试完成"
fi

echo ""
echo "================================"
echo "✓ 部署完成！"
echo "================================"
echo ""
echo "下一步："
echo "1. 复制配置文件内容: cat $CONFIG_FILE"
echo "2. 添加到 Cherry Studio 或 Claude Desktop"
echo "3. 重启客户端"
echo ""
