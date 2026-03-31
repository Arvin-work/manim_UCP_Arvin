#!/bin/bash

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}   Manim Visualization App Launcher${NC}"
echo -e "${BLUE}========================================${NC}"
echo

# 检测是否安装了Conda
if ! command -v conda &> /dev/null; then
    echo -e "${RED}错误: 未找到Conda！请先安装Anaconda或Miniconda。${NC}"
    echo -e "${YELLOW}请运行 setup_manim.sh 进行环境配置。${NC}"
    exit 1
fi

echo -e "${GREEN}[1/3] 检测到Conda${NC}"

# 初始化conda（确保conda命令在脚本中可用）
eval "$(conda shell.bash hook)"

# 检测是否存在manim_myself环境
if ! conda env list | grep -q "manim_myself"; then
    echo -e "${RED}错误: 未找到manim_myself环境！${NC}"
    echo -e "${YELLOW}请先运行 setup_manim.sh 进行环境配置。${NC}"
    exit 1
fi

echo -e "${GREEN}[2/3] 找到manim_myself环境${NC}"

# 激活环境
echo -e "${YELLOW}[3/3] 激活环境并启动应用...${NC}"
conda activate manim_myself

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 启动Flask应用
echo
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}   启动 Manim Visualization App${NC}"
echo -e "${BLUE}========================================${NC}"
echo

python app.py

# 如果应用退出，显示状态
if [ $? -ne 0 ]; then
    echo
    echo -e "${RED}应用异常退出，错误代码: $?${NC}"
fi
