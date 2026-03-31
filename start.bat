@echo off
setlocal enabledelayedexpansion

echo ========================================
echo    Manim Visualization App Launcher
echo ========================================
echo.

:: 检测是否安装了Conda
where conda >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: 未找到Conda！请先安装Anaconda或Miniconda。
    echo 请运行 setup_manim.bat 进行环境配置。
    pause
    exit /b 1
)

echo [1/3] 检测到Conda

:: 检测是否存在manim_myself环境
conda env list | findstr "manim_myself" >nul
if %errorlevel% neq 0 (
    echo 错误: 未找到manim_myself环境！
    echo 请先运行 setup_manim.bat 进行环境配置。
    pause
    exit /b 1
)

echo [2/3] 找到manim_myself环境

:: 激活环境
echo [3/3] 激活环境并启动应用...
call conda activate manim_myself

:: 获取脚本所在目录
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

:: 启动Flask应用
echo.
echo ========================================
echo    启动 Manim Visualization App
echo ========================================
echo.
python app.py

:: 如果应用退出，暂停以查看错误信息
if %errorlevel% neq 0 (
    echo.
    echo 应用异常退出，错误代码: %errorlevel%
    pause
)
