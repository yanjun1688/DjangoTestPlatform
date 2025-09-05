@echo off
chcp 65001 >nul
echo 🚀 启动Django后端服务器
echo ==========================

echo 📍 检查Python环境...

:: 智能检测Python命令（优先使用虚拟环境中的Python）
set PYTHON_CMD=

:: 检查是否已在虚拟环境中
if defined VIRTUAL_ENV (
    echo 🔍 检测到已在虚拟环境中: %VIRTUAL_ENV%
    where python >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        set PYTHON_CMD=python
        goto :python_found
    )
)

:: 如果不在虚拟环境中，按优先级检测
where python3.11 >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    set PYTHON_CMD=python3.11
    goto :python_found
)

where python3 >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    set PYTHON_CMD=python3
    goto :python_found
)

where python >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    for /f "tokens=2" %%i in ('python --version 2^>^&1') do (
        set VERSION=%%i
        if "!VERSION:~0,2!"=="3." (
            set PYTHON_CMD=python
            goto :python_found
        )
    )
)

echo ❌ 错误: 未找到Python 3.x，请先安装Python 3.x
pause
exit /b 1

:python_found
echo 📍 使用Python命令: %PYTHON_CMD%
%PYTHON_CMD% --version

echo 📁 当前目录: %CD%

:: 切换到backend目录
if not exist "blackend" (
    echo ❌ 错误: 未找到blackend目录，请确保在项目根目录下运行
    pause
    exit /b 1
)

cd blackend

:: 检查manage.py是否存在
if not exist "manage.py" (
    echo ❌ 错误: 未找到manage.py文件
    pause
    exit /b 1
)

:: 检查并激活虚拟环境
echo 🔧 检查虚拟环境...
if defined VIRTUAL_ENV (
    echo ✅ 已在虚拟环境中: %VIRTUAL_ENV%
    goto :venv_ready
)

if exist ".venv\Scripts\activate.bat" (
    echo 激活虚拟环境: .venv
    call .venv\Scripts\activate.bat
    :: 激活后重新设置Python命令
    where python >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        set PYTHON_CMD=python
    )
    echo ✅ 虚拟环境已激活
) else if exist "venv\Scripts\activate.bat" (
    echo 激活虚拟环境: venv
    call venv\Scripts\activate.bat
    :: 激活后重新设置Python命令
    where python >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        set PYTHON_CMD=python
    )
    echo ✅ 虚拟环境已激活
) else (
    echo ⚠️  未找到虚拟环境，建议创建虚拟环境
    echo    可运行: %PYTHON_CMD% -m venv .venv
    echo    然后激活: .venv\Scripts\activate.bat
)

:venv_ready

:: 安装依赖
echo 📦 检查并安装依赖...
if exist "requirements.txt" (
    echo 正在安装Python依赖...
    %PYTHON_CMD% -m pip install --upgrade pip
    %PYTHON_CMD% -m pip install -r requirements.txt
    if %ERRORLEVEL% NEQ 0 (
        echo ❌ 依赖安装失败，请检查requirements.txt文件
        pause
        exit /b 1
    )
    echo ✅ 依赖安装成功
) else (
    echo ⚠️  未找到requirements.txt文件
)

:: 运行数据库迁移
echo 🗄️  运行数据库迁移...
%PYTHON_CMD% manage.py makemigrations
%PYTHON_CMD% manage.py migrate
if %ERRORLEVEL% NEQ 0 (
    echo ❌ 数据库迁移失败
    pause
    exit /b 1
)

:: 创建超级用户
echo 👤 检查超级用户...
echo from django.contrib.auth import get_user_model; User = get_user_model(); created = not User.objects.filter(is_superuser=True).exists(); User.objects.create_superuser('admin', 'admin@test.com', 'admin123') if created else None; print('超级用户已创建' if created else '超级用户已存在') | %PYTHON_CMD% manage.py shell

:: 收集静态文件
echo 📂 收集静态文件...
%PYTHON_CMD% manage.py collectstatic --noinput

echo ✅ 准备启动Django开发服务器...
echo 🌐 服务器地址: http://localhost:8000
echo 🔧 Admin地址: http://localhost:8000/admin
echo 📝 Admin账号: admin / admin123
echo 🔄 按Ctrl+C停止服务器
echo ==========================

:: 启动服务器
%PYTHON_CMD% manage.py runserver 0.0.0.0:8000

echo.
echo 服务器已停止
pause 