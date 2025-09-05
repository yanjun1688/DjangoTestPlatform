@echo off
chcp 65001 >nul
echo 🔍 Django项目环境检查
echo ==========================

:: 检查Python
echo 📍 检查Python环境...

set PYTHON_CMD=
where python3 >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    set PYTHON_CMD=python3
    goto :run_check
)

where python >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    set PYTHON_CMD=python
    goto :run_check
)

echo ❌ 错误: 未找到Python，请先安装Python
pause
exit /b 1

:run_check
echo 🚀 运行环境检查脚本...
%PYTHON_CMD% check_environment.py
if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✅ 环境检查完成
) else (
    echo.
    echo ❌ 环境检查发现问题
)

echo.
echo 按任意键关闭...
pause >nul