#!/bin/bash
# ============================================
# Manim 环境自动部署脚本 (Linux / macOS)
# 创建 conda 环境 manim_myself 并安装 manim
# ============================================

set -e  # 遇到任何错误立即退出，避免产生错误提示误导

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的信息
info() { echo -e "${GREEN}✓${NC} $1"; }
warn() { echo -e "${YELLOW}⚠${NC} $1"; }
error() { echo -e "${RED}✗${NC} $1"; }
step() { echo -e "${BLUE}▶${NC} $1"; }

# ============================================
# 1. 检测 Conda 安装
# ============================================
step "检测 Conda 环境..."
if ! command -v conda &> /dev/null; then
    # 常见安装路径
    for conda_path in "$HOME/miniconda3/bin/conda" "$HOME/anaconda3/bin/conda" "/opt/conda/bin/conda"; do
        if [ -f "$conda_path" ]; then
            export PATH="$(dirname "$conda_path"):$PATH"
            break
        fi
    done
fi

if ! command -v conda &> /dev/null; then
    error "未找到 Conda！请先安装 Miniconda 或 Anaconda。"
    exit 1
fi
info "已检测到 Conda: $(conda --version | head -n1)"

# 初始化 conda 以便后续使用 conda activate
eval "$(conda shell.bash hook)"

# ============================================
# 2. 接受 Anaconda 服务条款（非交互）
# ============================================
step "检查并接受 Conda 服务条款..."
if conda tos --help &> /dev/null; then
    # 新版本 conda 需要接受 tos
    conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/main 2>/dev/null || true
    conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/r 2>/dev/null || true
    info "Conda 服务条款已接受"
else
    warn "当前 Conda 版本不支持 'tos' 命令，跳过服务条款检查"
fi

# ============================================
# 3. 安装系统级依赖（gcc / cairo 等）
# ============================================
step "检查并安装系统编译依赖..."
OS="$(uname -s)"
case "$OS" in
    Linux)
        if command -v apt-get &> /dev/null; then
            # Debian / Ubuntu
            sudo apt-get update -qq
            sudo apt-get install -y build-essential libcairo2-dev pkg-config
            info "已安装 build-essential, libcairo2-dev, pkg-config"
        elif command -v yum &> /dev/null; then
            # RHEL / CentOS
            sudo yum install -y gcc gcc-c++ cairo-devel pkgconfig
            info "已安装 gcc, cairo-devel, pkgconfig"
        elif command -v dnf &> /dev/null; then
            sudo dnf install -y gcc gcc-c++ cairo-devel pkgconfig
            info "已安装 gcc, cairo-devel, pkgconfig"
        else
            warn "未检测到 apt / yum / dnf，请手动安装 gcc 和 cairo 开发库"
        fi
        ;;
    Darwin)
        # macOS
        if ! command -v gcc &> /dev/null; then
            warn "未找到 gcc，尝试安装 Xcode Command Line Tools..."
            xcode-select --install 2>/dev/null || true
            # 等待用户安装
            read -p "请等待 Xcode Command Line Tools 安装完成，然后按 Enter 继续..." -r
        fi
        if ! command -v pkg-config &> /dev/null; then
            if command -v brew &> /dev/null; then
                brew install pkg-config cairo
                info "通过 Homebrew 安装了 cairo 和 pkg-config"
            else
                warn "未找到 Homebrew，请手动安装 cairo 和 pkg-config"
            fi
        fi
        ;;
    *)
        error "不支持的操作系统: $OS"
        exit 1
        ;;
esac
info "系统依赖准备就绪"

# ============================================
# 4. 创建 conda 环境（使用 Python 3.11）
# ============================================
ENV_NAME="manim_myself"
step "检查环境 '$ENV_NAME'..."

if conda env list | grep -q "^${ENV_NAME} "; then
    warn "环境 '$ENV_NAME' 已存在，将更新其中的 manim"
else
    step "创建新环境 $ENV_NAME (Python 3.11)..."
    conda create -n "$ENV_NAME" python=3.11 -y
    info "环境创建完成"
fi

# 激活环境
source "$(conda info --base)/etc/profile.d/conda.sh"  # 确保 conda 可用
conda activate "$ENV_NAME"
info "已激活环境 $ENV_NAME"

# ============================================
# 5. 安装 manim
# ============================================
step "安装 / 更新 manim..."
pip install --upgrade pip setuptools wheel
pip install manim

# 验证安装
if python -c "import manim" &> /dev/null; then
    MANIM_VER=$(python -c "import manim; print(manim.__version__)" 2>/dev/null || echo "unknown")
    info "manim 安装成功 (版本: $MANIM_VER)"
else
    error "manim 安装失败，请检查错误日志"
    exit 1
fi

# ============================================
# 完成提示
# ============================================
echo
info "========================================="
info "环境部署完成！"
info "使用以下命令激活环境："
echo -e "    ${GREEN}conda activate $ENV_NAME${NC}"
info "========================================="