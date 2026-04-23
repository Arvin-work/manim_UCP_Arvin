@echo off
setlocal enabledelayedexpansion

:: ============================================
:: Manim UCP Arvin - 环境自动部署脚本
:: 适用于 Windows
:: ============================================

echo ==========================================
echo   Manim UCP Arvin 环境自动部署
echo ==========================================
echo.

:: ============================================
:: 1. 检测 Conda 安装
:: ==========================================
echo [1/6] 检测 Conda 环境...

where conda >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo 错误: 未找到 Conda！请先安装 Anaconda 或 Miniconda。
    echo   下载地址: https://docs.conda.io/en/latest/miniconda.html
    echo.
    pause
    exit /b 1
)

echo   已检测到 Conda
call conda --version

call conda init cmd.exe >nul 2>&1

:: ============================================
:: 2. 检测 FFmpeg
:: ==========================================
echo.
echo [2/6] 检测 FFmpeg...

where ffmpeg >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=3 delims= " %%v in ('ffmpeg -version 2^>nul ^| findstr "ffmpeg version"') do (
        echo   已检测到 FFmpeg: %%v
    )
) else (
    echo   警告: 未检测到 FFmpeg，Manim 可能无法正常渲染视频
)

:: ============================================
:: 3. 创建/检查 conda 环境
:: ==========================================
echo.
echo [3/6] 创建 Python 环境...

set ENV_NAME=manim_myself
set SCRIPT_DIR=%~dp0

conda env list | findstr "manim_myself" >nul
if %errorlevel% equ 0 (
    echo   环境 '%ENV_NAME%' 已存在，将更新其中的依赖包
) else (
    echo   创建新环境 %ENV_NAME% (Python 3.12)...
    call conda create -n %ENV_NAME% python=3.12 -y
    echo   Python 3.12 环境创建完成
)

echo   激活环境...
call conda activate %ENV_NAME%

for /f "tokens=2" %%v in ('python --version 2^>^&1') do set PY_VER=%%v
echo   当前 Python 版本: %PY_VER%

:: ============================================
:: 4. 安装项目依赖
:: ==========================================
echo.
echo [4/6] 安装项目依赖包...

cd /d "%SCRIPT_DIR%"

echo   安装依赖包...
python -m pip install --upgrade pip setuptools wheel

if exist requirements.txt (
    echo   -----------------------------------------
    type requirements.txt
    echo   -----------------------------------------
    pip install -r requirements.txt
    echo   依赖安装完成
) else (
    pip install Flask Werkzeug manim sympy numpy
    echo   依赖安装完成
)

:: ============================================
:: 5. 验证安装
:: ==========================================
echo.
echo [5/6] 验证安装结果...
echo.

set ALL_OK=1

python -c "import manim" 2>nul
if %errorlevel% equ 0 (
    for /f "delims=" %%v in ('python -c "import manim; print(manim.__version__)" 2^>nul') do (
        echo   manim: %%v [OK]
    )
) else (
    echo   manim 导入失败！
    set ALL_OK=0
)

for %%p in (flask sympy numpy) do (
    python -c "import %%p" 2>nul
    if %errorlevel% equ 0 (
        for /f "delims=" %%v in ('python -c "import %%p; print(%%p.__version__)" 2^>nul') do (
            echo   %%p: %%v [OK]
        )
    ) else (
        echo   %%p 导入失败！
        set ALL_OK=0
    )
)

echo.
echo   验证项目模块完整性...
set MODULES=taylor_animator plot_animator differentiation_animator integration_animator three_d_animator implicit_animator polar_animator
for %%m in (%MODULES%) do (
    python -c "import %%m" 2>nul
    if %errorlevel% equ 0 (
        echo   %%m [OK]
    ) else (
        echo   %%m [警告: 运行时会自动重试]
    )
)

python -c "import app" 2>nul
if %errorlevel% equ 0 (
    echo   app.py [OK]
) else (
    echo   app.py [警告: 运行时会自动重试]
)

:: ============================================
:: 6. 完成提示
:: ==========================================
echo.
echo ==========================================
echo [6/6] 部署完成！
echo ==========================================
echo.

if %ALL_OK% == 1 (
    echo   所有依赖验证通过！
) else (
    echo   部分警告不影响运行，启动应用时会自动重试
)

echo.
echo ==========================================
echo   Manim UCP Arvin 环境部署成功！
echo ==========================================
echo.
echo 执行以下命令启动项目：
echo.
echo   ① 激活环境：
echo      conda activate %ENV_NAME%
echo.
echo   ② 启动应用：
echo      cd /d "%SCRIPT_DIR%"
echo      python app.py
echo.
echo   ③ 访问地址：
echo      http://localhost:5000
echo.
echo 说明：
echo   - Python 3.12 自动安装兼容版本 manim 0.18+
echo   - 渲染视频默认输出到 temp_render\ 目录
echo   - 运行日志保存在 visualization.log
echo.

pause
