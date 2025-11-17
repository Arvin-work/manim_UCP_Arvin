@echo off
setlocal enabledelayedexpansion

echo 检测Conda环境...

:: 检测是否安装了Conda
where conda >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: 未找到Conda！请先安装Anaconda或Miniconda。
    pause
    exit /b 1
)

echo ✓ 已检测到Conda

:: 检测是否存在manim_myself环境
echo 检测manim_myself环境...
conda env list | findstr "manim_myself" >nul
if %errorlevel% equ 0 (
    echo ✓ 找到manim_myself环境
    echo 激活环境...
    call conda activate manim_myself
    
    echo 检测manim是否已安装...
    python -c "import manim" 2>nul
    if %errorlevel% equ 0 (
        echo ✓ manim已安装
        echo 环境准备就绪！
    ) else (
        echo ✗ manim未安装，正在安装...
        pip install manim
        echo ✓ manim安装完成
    )
) else (
    echo ✗ 未找到manim_myself环境，正在创建...
    conda create -n manim_myself python=3.12 -y
    echo ✓ 环境创建完成
    echo 激活环境并安装manim...
    call conda activate manim_myself
    pip install manim
    echo ✓ manim安装完成
)

echo.
echo 使用以下命令激活环境:
echo conda activate manim_myself
pause