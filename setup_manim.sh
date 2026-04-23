#!/bin/bash

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}检测Conda环境...${NC}"

# 检测是否安装了Conda
if ! command -v conda &> /dev/null; then
    echo -e "${RED}错误: 未找到Conda！请先安装Anaconda或Miniconda。${NC}"
    exit 1
fi

echo -e "${GREEN}✓ 已检测到Conda${NC}"

# 初始化conda（确保conda命令在脚本中可用）
eval "$(conda shell.bash hook)"

echo -e "${YELLOW}检测manim_myself环境...${NC}"

# 检测是否存在manim_myself环境
if conda env list | grep -q "manim_myself"; then
    echo -e "${GREEN}✓ 找到manim_myself环境${NC}"
    echo -e "${YELLOW}激活环境...${NC}"
    conda activate manim_myself
    
    echo -e "${YELLOW}检测manim是否已安装...${NC}"
    if python -c "import manim" &> /dev/null; then
        echo -e "${GREEN}✓ manim已安装${NC}"
        echo -e "${GREEN}环境准备就绪！${NC}"
    else
        echo -e "${YELLOW}✗ manim未安装，正在安装...${NC}"
        pip install manim
        echo -e "${GREEN}✓ manim安装完成${NC}"
    fi
else
    echo -e "${YELLOW}✗ 未找到manim_myself环境，正在创建...${NC}"
    conda create -n manim_myself python=3.12 -y
    echo -e "${GREEN}✓ 环境创建完成${NC}"
    echo -e "${YELLOW}激活环境并安装manim...${NC}"
    conda activate manim_myself
    pip install manim
    echo -e "${GREEN}✓ manim安装完成${NC}"
fi

echo
echo -e "${GREEN}使用以下命令激活环境:${NC}"
echo "conda activate manim_myself"