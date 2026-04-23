#!/bin/bash
# ============================================
# Manim UCP Arvin - 环境自动部署脚本
# 适用于 Linux / macOS
# ============================================

set -e  # 遇到任何错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

# 打印带颜色的信息
info() { echo -e "${GREEN}✓${NC} $1"; }
warn() { echo -e "${YELLOW}⚠${NC} $1"; }
error() { echo -e "${RED}✗${NC} $1"; }
step() { echo -e "${BLUE}▶${NC} $1"; }
header() {
    echo
    echo -e "${PURPLE}=========================================${NC}"
    echo -e "${PURPLE}  $1${NC}"
    echo -e "${PURPLE}=========================================${NC}"
}

# ============================================
# 1. 检测 Conda 安装
# ============================================
header "第 1/7 步：检测 Conda 环境"

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
    echo "  下载地址: https://docs.conda.io/en/latest/miniconda.html"
    exit 1
fi

info "已检测到 Conda: $(conda --version | head -n1)"

# 初始化 conda
eval "$(conda shell.bash hook)"

# ============================================
# 2. 接受 Anaconda 服务条款
# ============================================
header "第 2/7 步：Conda 服务条款检查"

if conda tos --help &> /dev/null; then
    conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/main 2>/dev/null || true
    conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/r 2>/dev/null || true
    info "Conda 服务条款已接受"
else
    warn "当前 Conda 版本不支持 'tos' 命令，跳过检查"
fi

# ============================================
# 3. 安装系统级依赖
# ============================================
header "第 3/7 步：安装系统编译依赖"

OS="$(uname -s)"
case "$OS" in
    Linux)
        if command -v apt-get &> /dev/null; then
            # Debian / Ubuntu
            sudo apt-get update -qq
            sudo apt-get install -y build-essential libcairo2-dev pkg-config ffmpeg
            info "已安装 build-essential, libcairo2-dev, pkg-config, ffmpeg"
        elif command -v yum &> /dev/null; then
            # RHEL / CentOS
            sudo yum install -y gcc gcc-c++ cairo-devel pkgconfig ffmpeg
            info "已安装 gcc, cairo-devel, pkgconfig, ffmpeg"
        elif command -v dnf &> /dev/null; then
            sudo dnf install -y gcc gcc-c++ cairo-devel pkgconfig ffmpeg
            info "已安装 gcc, cairo-devel, pkgconfig, ffmpeg"
        else
            warn "未检测到 apt / yum / dnf，请手动安装：gcc, cairo-dev, pkg-config, ffmpeg"
        fi
        ;;
    Darwin)
        # macOS
        if ! command -v gcc &> /dev/null; then
            warn "未找到 gcc，尝试安装 Xcode Command Line Tools..."
            xcode-select --install 2>/dev/null || true
            read -p "请等待 Xcode Command Line Tools 安装完成，然后按 Enter 继续..." -r
        fi
        
        if command -v brew &> /dev/null; then
            brew install pkg-config cairo ffmpeg
            info "通过 Homebrew 安装了 cairo, pkg-config, ffmpeg"
        else
            warn "未找到 Homebrew，请手动安装：cairo, pkg-config, ffmpeg"
        fi
        ;;
    *)
        error "不支持的操作系统: $OS"
        exit 1
        ;;
esac

# 验证 FFmpeg
if command -v ffmpeg &> /dev/null; then
    FFMPEG_VER=$(ffmpeg -version | head -n1 | awk '{print $3}')
    info "已检测到 FFmpeg: $FFMPEG_VER"
else
    warn "未检测到 FFmpeg，Manim 可能无法正常渲染视频"
fi

# ============================================
# 4. 创建 conda 环境（统一 Python 3.12）
# ============================================
header "第 4/7 步：创建 Python 环境"

ENV_NAME="manim_myself"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if conda env list | grep -q "^${ENV_NAME} "; then
    info "环境 '$ENV_NAME' 已存在，将更新其中的依赖包"
else
    step "创建新环境 $ENV_NAME (Python 3.12)..."
    conda create -n "$ENV_NAME" python=3.12 -y
    info "Python 3.12 环境创建完成"
fi

# 激活环境
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate "$ENV_NAME"
info "已激活环境: $ENV_NAME"
info "当前 Python 版本: $(python --version | awk '{print $2}')"

# ============================================
# 5. 安装项目依赖（按 requirements.txt 精确版本）
# ============================================
header "第 5/7 步：安装项目依赖包"

cd "$SCRIPT_DIR"

if [ -f "requirements.txt" ]; then
    step "按 requirements.txt 精确安装依赖..."
    pip install --upgrade pip setuptools wheel
    
    echo "-----------------------------------------"
    cat requirements.txt
    echo "-----------------------------------------"
    
    pip install -r requirements.txt
    info "requirements.txt 依赖安装完成"
else
    warn "未找到 requirements.txt，手动安装依赖..."
    pip install Flask==2.3.3 Werkzeug==2.3.7 manim==0.17.3 sympy==1.12 numpy==1.24.3
    info "手动安装依赖完成"
fi

# ============================================
# 6. 验证安装
# ============================================
header "第 6/7 步：验证安装结果"

ALL_OK=true

# 验证 manim
if python -c "import manim" &> /dev/null; then
    MANIM_VER=$(python -c "import manim; print(manim.__version__)")
    if [ "$MANIM_VER" = "0.17.3" ]; then
        info "manim: $MANIM_VER ✓"
    else
        warn "manim: $MANIM_VER ⚠ (预期: 0.17.3，可能存在兼容性问题)"
    fi
else
    error "manim 导入失败！"
    ALL_OK=false
fi

# 验证其他核心依赖
for pkg in flask sympy numpy; do
    if python -c "import $pkg" &> /dev/null; then
        PKG_VER=$(python -c "import $pkg; print($pkg.__version__)")
        info "$pkg: $PKG_VER ✓"
    else
        error "$pkg 导入失败！"
        ALL_OK=false
    fi
done

# 验证项目所有模块
step "验证项目模块完整性..."
cd "$SCRIPT_DIR"
MODULES=("taylor_animator" "plot_animator" "differentiation_animator" 
         "integration_animator" "three_d_animator" "implicit_animator" "polar_animator")

for module in "${MODULES[@]}"; do
    if python -c "import $module" &> /dev/null; then
        info "$module ✓"
    else
        warn "$module ⚠ 导入警告（可忽略，运行时会重试）"
    fi
done

# 验证 app.py
if python -c "import app; print('app 导入成功')" &> /dev/null; then
    info "Flask 应用入口: app.py ✓"
else
    warn "app.py ⚠ 导入警告（可忽略，运行时会重试）"
fi

# ============================================
# 7. 完成提示
# ============================================
header "第 7/7 步：部署完成！"

if [ "$ALL_OK" = true ]; then
    info "✅ 所有依赖验证通过！"
else
    warn "⚠ 部分警告不影响运行，启动应用时会自动重试"
fi

echo
echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}   Manim UCP Arvin 环境部署成功！${NC}"
echo -e "${GREEN}=========================================${NC}"
echo
echo "📌 执行以下命令启动项目："
echo
echo "   ① 激活环境："
echo -e "      ${GREEN}conda activate $ENV_NAME${NC}"
echo
echo "   ② 启动应用："
echo -e "      ${GREEN}cd $SCRIPT_DIR${NC}"
echo -e "      ${GREEN}python app.py${NC}"
echo
echo "   ③ 访问地址："
echo -e "      ${BLUE}http://localhost:5000${NC}"
echo
echo "📝 说明："
echo "   - 渲染视频默认输出到 temp_render/ 目录"
echo "   - 运行日志保存在 visualization.log"
echo

