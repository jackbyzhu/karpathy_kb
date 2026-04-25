@echo off
echo ========================================
echo Karpathy Knowledge Base - 快速部署脚本
echo ========================================
echo.

REM 检查 Python 是否安装
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未检测到 Python，请先安装 Python 3.8+
    echo 下载地址：https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [1/6] Python 已安装
python --version
echo.

REM 创建虚拟环境
echo [2/6] 创建虚拟环境...
python -m venv venv
if %errorlevel% neq 0 (
    echo [错误] 创建虚拟环境失败
    pause
    exit /b 1
)
echo 虚拟环境创建成功
echo.

REM 激活虚拟环境
echo [3/6] 激活虚拟环境...
call venv\Scripts\activate.bat
echo 虚拟环境已激活
echo.

REM 升级 pip
echo [4/6] 升级 pip...
python -m pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple
echo.

REM 安装依赖
echo [5/6] 安装依赖包（这可能需要几分钟）...
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
if %errorlevel% neq 0 (
    echo [警告] 部分依赖安装失败，请检查错误信息
    echo 可以尝试手动安装：pip install -r requirements.txt
)
echo.

REM 检查配置文件
echo [6/6] 检查配置文件...
if not exist "src\config.py" (
    echo [错误] 未找到 src\config.py
    echo 请复制 src\config.py.example 为 src\config.py 并配置 API Key
    pause
    exit /b 1
)

echo.
echo ========================================
echo 部署完成！
echo ========================================
echo.
echo 下一步：
echo 1. 编辑 src\config.py 配置你的 API Key
echo 2. 将资料放入 raw\ 目录
echo 3. 运行 python app.py 开始使用
echo.
echo 如需上传到 GitHub，请查看 GITHUB_UPLOAD_GUIDE.md
echo.
pause
