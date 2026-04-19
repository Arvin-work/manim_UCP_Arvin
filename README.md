# Manim UCP Arvin

<div align="center">

![Python Version](https://img.shields.io/badge/python-3.12-blue.svg)
![Flask](https://img.shields.io/badge/flask-2.3.3-green.svg)
![Manim](https://img.shields.io/badge/manim-0.17.3-orange.svg)
![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)

**一个基于 Manim 的数学可视化 Web 应用控制面板**

[English](#english-version) | [中文文档](#中文文档)

</div>

---

## 中文文档

### 📖 项目简介

**Manim UCP Arvin** (User Control Panel) 是一个基于 Manim Community Edition 的数学可视化 Web 应用。该项目旨在为不熟悉 Python 编程的用户提供一个友好、直观的图形界面，用于生成高质量的数学动画和可视化内容。

#### 🎯 核心目标

- **降低使用门槛**: 让不熟悉编程的用户也能轻松创建数学动画
- **可视化数学概念**: 通过动画直观展示微积分、函数图像等数学概念
- **教育辅助工具**: 为教师和学生提供数学教学辅助工具
- **开源免费**: 完全开源，免费使用，鼓励社区贡献

#### 🌟 背景意义

Manim 是著名的数学动画引擎，由 3Blue1Brown 创建，能够生成高质量的数学教学视频。然而，Manim 的使用需要一定的 Python 编程基础，这对许多教育工作者和学生来说是一个障碍。本项目通过 Web 界面封装 Manim 的核心功能，让用户无需编写代码即可生成数学动画，极大地降低了使用门槛。

---

### ✨ 功能特性

#### 🎨 主要功能模块

| 功能模块 | 描述 | 状态 |
|---------|------|------|
| **显函数绘图** | 支持 y = f(x) 格式的函数绘图，可配置颜色、线宽、动画风格 | ✅ 已完成 |
| **隐函数绘图** | 支持 F(x,y) = 0 格式的隐函数绘图，如圆、椭圆等 | ✅ 已完成 |
| **极坐标绘图** | 支持 r = r(θ) 格式的极坐标方程绘图，包括二维和三维球坐标 | ✅ 已完成 |
| **参数方程** | 支持二维参数曲线 x(t), y(t) 和三维参数曲线/曲面 | ✅ 已完成 |
| **泰勒展开** | 动画展示泰勒级数逐阶逼近函数的过程 | ✅ 已完成 |
| **微分展示** | 可视化导数概念，展示割线逼近切线的过程 | ✅ 已完成 |
| **积分展示** | 黎曼和逼近过程可视化，支持正负函数值区域 | ✅ 已完成 |
| **三维场景** | 支持三维曲面、曲线、平面绘制，可自定义相机视角 | ✅ 已完成 |
| **三维黎曼积分** | 三维曲面下体积积分可视化 | ❌ 已禁用 |

#### 🛠️ 辅助功能

- **多种输入方式**: 显函数、隐函数、极坐标、参数方程
- **实时日志显示**: 动画生成过程实时反馈
- **参数验证**: 智能检测输入错误并提供友好提示
- **相机控制**: 三维场景支持自定义相机角度和预设视角
- **环境自动配置**: 一键安装和配置运行环境
- **跨平台支持**: 支持 Windows、Linux、macOS

#### 📊 功能支持矩阵

| 功能 | 显函数 | 隐函数 | 极坐标 | 参数方程(3D) |
|------|--------|--------|--------|--------------|
| 单纯画图 | ✅ | ✅ | ✅ | ✅ |
| 微分展示 | ✅ | ✅ | ❌ | ✅ (曲线) |
| 泰勒展开 | ✅ | ❌ | ❌ | ❌ |
| 积分展示 | ✅ | ❌ | ❌ | ❌ |

---

### 🏗️ 技术架构

#### 系统架构图

```
┌─────────────────────────────────────────────────────────┐
│                    用户界面层 (Frontend)                  │
│  ┌──────────────────────────────────────────────────┐   │
│  │  HTML5 + CSS3 + JavaScript (原生)                 │   │
│  │  - 响应式界面设计                                  │   │
│  │  - 实时日志显示                                    │   │
│  │  - 参数输入与验证                                  │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
                            ↓ HTTP/REST API
┌─────────────────────────────────────────────────────────┐
│                    应用层 (Backend)                       │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Flask Web Framework                              │   │
│  │  - RESTful API 接口                               │   │
│  │  - 后台任务处理                                    │   │
│  │  - 参数验证与解析                                  │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                    业务逻辑层                             │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐       │
│  │ Taylor     │  │ Plot       │  │ Implicit   │       │
│  │ Animator   │  │ Animator   │  │ Animator   │       │
│  └────────────┘  └────────────┘  └────────────┘       │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐       │
│  │ Polar      │  │ Diff       │  │ Integration│       │
│  │ Animator   │  │ Animator   │  │ Animator   │       │
│  └────────────┘  └────────────┘  └────────────┘       │
│  ┌────────────┐                                          │
│  │ 3D        │                                          │
│  │ Animator  │                                          │
│  └────────────┘                                          │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                    核心引擎层                             │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Manim Community Edition                          │   │
│  │  - 动画渲染引擎                                    │   │
│  │  - 数学对象生成                                    │   │
│  │  - 视频编码输出                                    │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                    数学计算层                             │
│  ┌──────────────────┐  ┌──────────────────┐            │
│  │  SymPy           │  │  NumPy           │            │
│  │  - 符号计算       │  │  - 数值计算       │            │
│  │  - 表达式解析     │  │  - 数组运算       │            │
│  └──────────────────┘  └──────────────────┘            │
└─────────────────────────────────────────────────────────┘
```

#### 技术栈详情

**前端技术**
- **HTML5**: 语义化标签，结构清晰
- **CSS3**: 响应式设计，现代化UI
- **JavaScript (原生)**: 无框架依赖，轻量高效
- **Fetch API**: 异步HTTP请求

**后端技术**
- **Flask 2.3.3**: 轻量级Web框架
- **Werkzeug 2.3.7**: WSGI工具库
- **Threading**: 后台任务处理

**核心引擎**
- **Manim 0.17.3**: 动画渲染引擎
- **FFmpeg**: 视频编码

**数学计算**
- **SymPy 1.12**: 符号数学计算
- **NumPy 1.24.3**: 数值计算

**环境管理**
- **Conda**: Python环境管理
- **pip**: 包管理器

---

### 📁 项目结构

```
manim_UCP_Arvin/
├── 📄 app.py                      # Flask 主应用入口
├── 📄 taylor_animator.py          # 泰勒展开动画生成器
├── 📄 plot_animator.py            # 显函数绘图动画生成器
├── 📄 implicit_animator.py        # 隐函数绘图动画生成器
├── 📄 polar_animator.py           # 极坐标绘图动画生成器
├── 📄 differentiation_animator.py # 微分展示动画生成器
├── 📄 integration_animator.py     # 积分展示动画生成器
├── 📄 three_d_animator.py         # 三维场景动画生成器
│
├── 📂 templates/
│   └── 📄 index.html              # Web 界面主页面
│
├── 📂 static/
│   ├── 📂 js/
│   │   └── 📄 script.js           # 前端交互逻辑
│   └── 📂 css/
│       └── 📄 style.css           # 样式文件
│
├── 📂 need_file/                  # 测试文件和示例媒体
│   ├── 📄 test_comprehensive.py   # 综合测试套件
│   └── 📂 media/                  # 生成的视频文件
│
├── 📄 setup_manim.bat             # Windows 环境配置脚本
├── 📄 setup_manim.sh              # Linux/Mac 环境配置脚本
├── 📄 start.bat                   # Windows 启动脚本
├── 📄 start.sh                    # Linux/Mac 启动脚本
│
├── 📄 requirements.txt            # Python 依赖列表
├── 📄 USER_MANUAL.txt             # 用户使用手册
├── 📄 PROJECT_STATUS.md           # 项目状态说明
├── 📄 LICENSE                     # Apache License 2.0
└── 📄 README.md                   # 项目说明文档
```

#### 核心文件说明

| 文件 | 说明 |
|------|------|
| `app.py` | Flask应用主入口，处理HTTP请求和路由 |
| `*_animator.py` | 各类动画生成器，封装Manim动画逻辑 |
| `templates/index.html` | Web界面HTML模板 |
| `static/js/script.js` | 前端交互逻辑和API调用 |
| `static/css/style.css` | 界面样式定义 |
| `requirements.txt` | Python依赖包列表 |

---

### 🚀 快速开始

#### 环境要求

- **操作系统**: Windows 10/11, Linux, macOS
- **Python**: 3.12
- **Conda**: Anaconda 或 Miniconda
- **FFmpeg**: 自动安装（Manim依赖）

#### 安装步骤

##### Windows 系统

1. **克隆项目**
```batch
git clone https://github.com/Arvin-work/manim_UCP_Arvin/tree/new_project
cd manim_UCP_Arvin
```

2. **运行环境配置脚本**
```batch
.\setup_manim.bat
```

脚本会自动：
- 检测 Conda 是否安装
- 创建名为 `manim_myself` 的 Conda 环境
- 安装所有依赖包
- 配置 Manim

3. **启动应用**
```batch
.\start.bat
```

4. **访问应用**
打开浏览器，访问 `http://localhost:5000`

##### Linux/macOS 系统

1. **克隆项目**
```bash
git clone https://github.com/Arvin-work/manim_UCP_Arvin/tree/new_project
cd manim_UCP_Arvin
```

2. **添加执行权限**
```bash
chmod +x setup_manim.sh start.sh
```

3. **运行环境配置脚本**
```bash
./setup_manim.sh
```

4. **启动应用**
```bash
./start.sh
```

5. **访问应用**
打开浏览器，访问 `http://localhost:5000`

#### 手动安装（可选）

如果自动脚本失败，可以手动安装：

```bash
# 创建 Conda 环境
conda create -n manim_myself python=3.12 -y
conda activate manim_myself

# 安装依赖
pip install -r requirements.txt

# 启动应用
python app.py
```

---

### 📚 使用指南

#### 基本操作流程

1. **选择场景类型**
   - 二维场景：用于平面函数图像
   - 三维场景：用于空间曲面和曲线

2. **选择输入方式**
   - 显函数：y = f(x) 格式
   - 隐函数：F(x,y) = 0 格式
   - 极坐标：r = r(θ) 格式
   - 参数方程：x(t), y(t), z(t) 格式

3. **输入函数表达式**
   - 支持常见数学函数：sin, cos, tan, exp, log, sqrt
   - 使用 `**` 表示幂运算
   - 使用 `pi` 和 `e` 常量

4. **选择功能模块**
   - 单纯画图：仅绘制函数图像
   - 微分展示：展示导数概念
   - 泰勒展开：展示泰勒级数逼近
   - 积分展示：展示黎曼和逼近

5. **调整参数**（可选）
   - 坐标范围
   - 动画时长
   - 颜色设置
   - 相机角度（三维场景）

6. **生成动画**
   - 点击"开始创作"按钮
   - 等待动画生成
   - 下载或在线观看

#### 使用示例

##### 示例 1：绘制二次函数

```
场景：二维场景
输入方式：显函数
函数表达式：x**2
功能：单纯画图
X轴范围：-5 到 5
```

##### 示例 2：泰勒展开展示

```
场景：二维场景
输入方式：显函数
函数表达式：sin(x)
功能：泰勒展开
展开点：0
最高阶数：7
```

##### 示例 3：隐函数绘图

```
场景：二维场景
输入方式：隐函数
函数表达式：x**2 + y**2 - 4
功能：单纯画图
```

##### 示例 4：三维曲面

```
场景：三维场景
输入方式：显函数
函数表达式：x**2 + y**2
功能：单纯画图
X轴范围：-3 到 3
Y轴范围：-3 到 3
相机角度：φ=45°, θ=-45°
```

##### 示例 5：极坐标绘图

```
场景：二维场景
输入方式：极坐标
函数表达式：2 + 2*sin(theta)
功能：单纯画图
θ范围：0 到 2*pi
```

##### 示例 6：参数方程曲线

```
场景：三维场景
输入方式：参数方程
模式：曲线
x(t)：cos(t)
y(t)：sin(t)
z(t)：t/(2*pi)
t范围：0 到 4*pi
```

#### 支持的数学函数

| 函数 | 说明 | 示例 |
|------|------|------|
| `sin(x)` | 正弦函数 | sin(x) |
| `cos(x)` | 余弦函数 | cos(x) |
| `tan(x)` | 正切函数 | tan(x) |
| `exp(x)` | 指数函数 | exp(x) |
| `log(x)` | 自然对数 | log(x) |
| `sqrt(x)` | 平方根 | sqrt(x) |
| `abs(x)` | 绝对值 | abs(x) |
| `asin(x)` | 反正弦 | asin(x) |
| `acos(x)` | 反余弦 | acos(x) |
| `atan(x)` | 反正切 | atan(x) |

#### 常量

- `pi`: 圆周率 π ≈ 3.14159
- `e`: 自然常数 e ≈ 2.71828

---

### ❓ 常见问题解答

#### Q1: 安装时提示"Conda未找到"

**A**: 请确保已安装 Anaconda 或 Miniconda，并将其添加到系统环境变量中。

**解决方法**:
- Windows: 安装时勾选"Add Anaconda to my PATH environment variable"
- Linux/macOS: 在 `~/.bashrc` 或 `~/.zshrc` 中添加 Conda 路径

#### Q2: 动画生成速度很慢

**A**: 动画生成时间取决于复杂度和时长，通常需要几秒到几分钟。

**优化建议**:
- 减少动画时长
- 降低坐标范围
- 减少细分程度（积分展示）

#### Q3: 提示"函数解析错误"

**A**: 请检查函数表达式格式是否正确。

**常见错误**:
- 使用 `^` 代替 `**` 表示幂运算
- 忘记乘号：`2x` 应写成 `2*x`
- 括号不匹配

#### Q4: 三维场景显示不正常

**A**: 尝试调整相机角度参数。

**推荐设置**:
- φ (俯仰角): 45°
- θ (方位角): -45°

#### Q5: 生成的视频在哪里？

**A**: 视频文件保存在 `need_file/media/videos/` 目录下，也可以通过浏览器直接下载。

#### Q6: 支持哪些浏览器？

**A**: 推荐使用现代浏览器：
- Google Chrome (推荐)
- Mozilla Firefox
- Microsoft Edge
- Safari

#### Q7: 可以导出其他格式吗？

**A**: 目前仅支持 MP4 格式。如需其他格式，可使用视频转换工具。

#### Q8: 隐函数模式下某些功能不可用？

**A**: 这是正常限制。隐函数模式仅支持：
- 单纯画图
- 微分展示

不支持泰勒展开和积分展示。

#### Q9: 极坐标模式支持哪些功能？

**A**: 极坐标模式仅支持单纯画图功能。

#### Q10: 如何贡献代码？

**A**: 请参阅下方的"贡献指南"部分。

---

### 🤝 贡献指南

我们欢迎所有形式的贡献！

#### 如何贡献

1. **Fork 项目**
   - 点击右上角的 "Fork" 按钮

2. **克隆你的 Fork**
```bash
git clone https://github.com/Arvin-work/manim_UCP_Arvin/tree/new_project
```

3. **创建分支**
```bash
git checkout -b feature/your-feature-name
```

4. **进行修改**
   - 遵循现有代码风格
   - 添加必要的注释
   - 更新相关文档

5. **提交更改**
```bash
git add .
git commit -m "描述你的更改"
```

6. **推送到 Fork**
```bash
git push origin feature/your-feature-name
```

7. **创建 Pull Request**
   - 在 GitHub 上创建 Pull Request
   - 详细描述你的更改

#### 贡献类型

- 🐛 Bug 修复
- ✨ 新功能开发
- 📝 文档改进
- 🎨 UI/UX 改进
- ⚡ 性能优化
- 🌐 国际化支持

#### 代码规范

- **Python**: 遵循 PEP 8 规范
- **JavaScript**: 使用 ES6+ 语法
- **注释**: 使用中文注释
- **文档**: 更新相关文档

#### 测试

在提交 PR 前，请确保：

1. 运行测试套件
```bash
cd need_file
python test_comprehensive.py
```

2. 手动测试新功能

3. 检查文档是否需要更新

---

### 📄 许可证

本项目采用 Apache License 2.0 许可证。详见 [LICENSE](LICENSE) 文件。

```
Copyright 2024 Manim UCP Arvin Contributors

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
```

---

### 📞 联系方式

- **问题反馈**: 请在 GitHub Issues 中提交
- **功能建议**: 欢迎在 Issues 中讨论
- **代码贡献**: 请参考贡献指南

---

### 🙏 致谢

- [Manim Community](https://www.manim.community/) - 优秀的数学动画引擎
- [3Blue1Brown](https://www.3blue1brown.com/) - Manim 的创建者
- 所有贡献者和用户

---

<div align="center">

**如果这个项目对你有帮助，请给一个 ⭐ Star！**

Made with ❤️ by Manim UCP Arvin Team

</div>

---

## English Version

### 📖 Project Overview

**Manim UCP Arvin** (User Control Panel) is a web-based mathematical visualization application built on Manim Community Edition. The project aims to provide a user-friendly graphical interface for users unfamiliar with Python programming to generate high-quality mathematical animations and visualizations.

#### 🎯 Core Objectives

- **Lower the barrier**: Enable users without programming knowledge to create mathematical animations
- **Visualize mathematical concepts**: Intuitively demonstrate calculus, function graphs, and other mathematical concepts
- **Educational tool**: Provide teaching aids for educators and students
- **Open source & free**: Completely open source and free to use

### ✨ Features

- **Multiple input methods**: Explicit functions, implicit functions, polar coordinates, parametric equations
- **2D & 3D visualization**: Support for both 2D and 3D mathematical objects
- **Educational animations**: Taylor series, differentiation, integration visualization
- **Real-time feedback**: Live logging during animation generation
- **Camera control**: Customizable camera angles for 3D scenes
- **Cross-platform**: Windows, Linux, macOS support

### 🚀 Quick Start

#### Requirements

- Python 3.12
- Anaconda or Miniconda
- FFmpeg (auto-installed with Manim)

#### Installation

**Windows:**
```batch
.\setup_manim.bat
.\start.bat
```

**Linux/macOS:**
```bash
chmod +x setup_manim.sh start.sh
./setup_manim.sh
./start.sh
```

Access the application at `http://localhost:5000`

### 📚 Usage Examples

**Example 1: Quadratic Function**
```
Scene: 2D Scene
Input: Explicit Function
Expression: x**2
Function: Simple Plot
```

**Example 2: Taylor Series**
```
Scene: 2D Scene
Input: Explicit Function
Expression: sin(x)
Function: Taylor Expansion
Expansion Point: 0
Max Order: 7
```

**Example 3: 3D Surface**
```
Scene: 3D Scene
Input: Explicit Function
Expression: x**2 + y**2
Function: Simple Plot
Camera: φ=45°, θ=-45°
```

### 🤝 Contributing

We welcome all contributions! Please see the Chinese section above for detailed contribution guidelines.

### 📄 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

---

<div align="center">

**If this project helps you, please give it a ⭐ Star!**

</div>
