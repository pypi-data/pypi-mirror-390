@echo off
chcp 65001 >nul
echo ================================
echo imgenx-mcp 部署脚本 (Windows)
echo ================================
echo.

REM 1. 检查 Python
echo ^>^>^> 步骤 1: 检查 Python 环境
python --version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✓ 检测到 Python
    set PYTHON_CMD=python
) else (
    python3 --version >nul 2>&1
    if %errorlevel% equ 0 (
        echo ✓ 检测到 Python3
        set PYTHON_CMD=python3
    ) else (
        echo ✗ 未检测到 Python，请先安装 Python 3.10+
        pause
        exit /b 1
    )
)
echo.

REM 2. 安装 imgenx-mcp
echo ^>^>^> 步骤 2: 安装 imgenx-mcp
%PYTHON_CMD% -m pip install --upgrade pip
%PYTHON_CMD% -m pip install imgenx-mcp

if %errorlevel% equ 0 (
    echo ✓ imgenx-mcp 安装成功
) else (
    echo ✗ imgenx-mcp 安装失败
    pause
    exit /b 1
)
echo.

REM 3. 验证安装
echo ^>^>^> 步骤 3: 验证安装
%PYTHON_CMD% -m imgenx.main --help >nul 2>&1

if %errorlevel% equ 0 (
    echo ✓ imgenx-mcp 验证成功
) else (
    echo ✗ imgenx-mcp 验证失败
    pause
    exit /b 1
)
echo.

REM 4. 创建配置文件
echo ^>^>^> 步骤 4: 创建配置文件
set CONFIG_FILE=cherry_studio_config.json

(
echo {
echo   "mcpServers": {
echo     "imgenx": {
echo       "command": "python",
echo       "args": ["-m", "imgenx.main", "server"],
echo       "env": {
echo         "IMGENX_IMAGE_MODEL": "doubao:doubao-seedream-4-0-250828",
echo         "IMGENX_VIDEO_MODEL": "doubao:doubao-seedance-1-0-pro-fast-251015",
echo         "IMGENX_ANALYZER_MODEL": "doubao:doubao-seed-1-6-vision-250815",
echo         "IMGENX_API_KEY": "ebabd2d9-c0c6-44a4-9ec6-0656fc81d496",
echo         "OSS_ACCESS_KEY_ID": "LTAI5t8WoXY2sYaMt9NUk2YM",
echo         "OSS_ACCESS_KEY_SECRET": "HUKE4Bu0WYtT2hJixNlwj69pbi0ZXf",
echo         "OSS_BUCKET": "dev-res-tishi",
echo         "OSS_ENDPOINT": "oss-cn-shanghai.aliyuncs.com",
echo         "OSS_CDN_URL": "https://dev-res.tishiii.com/"
echo       },
echo       "timeout": 600
echo     }
echo   }
echo }
) > %CONFIG_FILE%

echo ✓ 配置文件已创建: %CONFIG_FILE%
echo.

REM 5. 显示说明
echo ^>^>^> 步骤 5: 配置说明
echo.
echo 配置文件已生成: %cd%\%CONFIG_FILE%
echo.
echo 请将此配置添加到您的 MCP 客户端：
echo   - Cherry Studio: 设置 → MCP 服务器 → 添加服务器
echo   - Claude Desktop: 编辑配置文件
echo.

echo ================================
echo ✓ 部署完成！
echo ================================
echo.
echo 下一步：
echo 1. 查看配置文件: type %CONFIG_FILE%
echo 2. 添加到 Cherry Studio 或 Claude Desktop
echo 3. 重启客户端
echo.
pause
