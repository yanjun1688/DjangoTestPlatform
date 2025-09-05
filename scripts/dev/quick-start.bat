@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul
echo Django Development Server - Quick Start
echo =======================================

:: 快速检查是否在正确目录
if not exist "backend\manage.py" (
    echo Error: Please run from project root directory
    echo Current: %CD%
    pause
    exit /b 1
)

cd backend

:: 检查虚拟环境
if defined VIRTUAL_ENV (
    echo Using active virtual environment
    set PYTHON_CMD=python
) else if exist ".venv\Scripts\activate.bat" (
    echo Activating .venv...
    call .venv\Scripts\activate.bat
    set PYTHON_CMD=python
) else if exist "venv\Scripts\activate.bat" (
    echo Activating venv...
    call venv\Scripts\activate.bat
    set PYTHON_CMD=python
) else (
    echo Warning: No virtual environment found, using system Python
    set PYTHON_CMD=python
)

:: 智能依赖检查（仅检查关键模块）
echo Checking key dependencies...
%PYTHON_CMD% -c "import django, rest_framework, reversion" >nul 2>&1
if !ERRORLEVEL! NEQ 0 (
    echo Installing missing dependencies...
    %PYTHON_CMD% -m pip install -r requirements.txt
) else (
    echo Dependencies OK, skipping installation
)

:: 快速数据库检查和迁移
echo Checking database...
%PYTHON_CMD% manage.py migrate --check >nul 2>&1
if !ERRORLEVEL! NEQ 0 (
    echo Running pending migrations...
    %PYTHON_CMD% manage.py migrate
) else (
    echo Database is up to date
)

:: 启动服务器
echo.
echo Starting Django server at http://localhost:8000
echo Admin: http://localhost:8000/admin (admin/admin123)
echo Press Ctrl+C to stop
echo =======================================
%PYTHON_CMD% manage.py runserver 8000