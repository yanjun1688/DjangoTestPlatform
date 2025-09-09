@echo off
REM Windows批处理脚本 - 便捷测试执行
REM 使用方法: 双击运行或在命令行中执行

echo ==========================================
echo Django测试平台 - 集中化测试执行器
echo ==========================================
echo.

cd /d "%~dp0"

REM 检查Python是否可用
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: Python未安装或不在PATH环境变量中
    pause
    exit /b 1
)

echo 选择要执行的测试类型:
echo.
echo 1. 执行所有测试
echo 2. 单元测试 (Unit Tests)
echo 3. API测试 (API Tests)  
echo 4. 功能测试 (Functional Tests)
echo 5. 集成测试 (Integration Tests)
echo 6. E2E测试 (End-to-End Tests)
echo 7. 性能测试 (Performance Tests)
echo 8. 检查环境
echo 9. 退出
echo.

set /p choice="请输入选择 (1-9): "

if "%choice%"=="1" (
    echo 执行所有测试...
    python run_all_tests.py --verbose
) else if "%choice%"=="2" (
    echo 执行单元测试...
    python run_all_tests.py --unit --verbose
) else if "%choice%"=="3" (
    echo 执行API测试...
    python run_all_tests.py --api --verbose
) else if "%choice%"=="4" (
    echo 执行功能测试...
    python run_all_tests.py --functional --verbose
) else if "%choice%"=="5" (
    echo 执行集成测试...
    python run_all_tests.py --integration --verbose
) else if "%choice%"=="6" (
    echo 执行E2E测试...
    python run_all_tests.py --e2e --verbose
) else if "%choice%"=="7" (
    echo 执行性能测试...
    python run_all_tests.py --performance --verbose
) else if "%choice%"=="8" (
    echo 检查测试环境...
    python run_all_tests.py --check
) else if "%choice%"=="9" (
    echo 退出
    exit /b 0
) else (
    echo 无效选择，请重新运行脚本
)

echo.
echo 测试执行完成！
pause