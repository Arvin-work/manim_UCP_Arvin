# Manim UCP Arvin - 项目状态说明

## 项目概述

**Manim UCP Arvin** 是一个基于 Manim 的数学可视化 Web 应用控制面板。该项目旨在为不熟悉 Python 编程的用户提供一个友好的图形界面，用于生成数学动画和可视化内容。

### 技术栈
- **后端**: Flask (Python)
- **前端**: HTML5 + CSS3 + JavaScript (原生)
- **动画引擎**: Manim Community Edition
- **数学计算**: SymPy + NumPy
- **环境管理**: Conda

---

## 项目结构

```
manim_UCP_Arvin/
├── app.py                      # Flask 主应用入口
├── taylor_animator.py          # 泰勒展开动画生成器
├── plot_animator.py            # 显函数绘图动画生成器
├── implicit_animator.py        # 隐函数绘图动画生成器
├── polar_animator.py           # 极坐标绘图动画生成器
├── differentiation_animator.py # 微分展示动画生成器
├── integration_animator.py     # 积分展示动画生成器
├── three_d_animator.py         # 三维场景动画生成器
├── templates/
│   └── index.html              # Web 界面主页面
├── static/
│   ├── js/
│   │   └── script.js           # 前端交互逻辑
│   └── css/
│       └── style.css           # 样式文件
├── need_file/                  # 测试文件和示例媒体
├── setup_manim.bat             # Windows 环境配置脚本
├── setup_manim.sh              # Linux/Mac 环境配置脚本
├── start.bat                   # Windows 启动脚本
├── start.sh                    # Linux/Mac 启动脚本
├── LICENSE                     # Apache License 2.0
└── README.md                   # 项目说明
```

---

## 功能完成状态

### ✅ 已完成功能

| 功能模块 | 文件 | 状态 | 说明 |
|---------|------|------|------|
| **泰勒展开动画** | `taylor_animator.py` | ✅ 完成 | 支持自定义展开点、最高阶数，动画展示逐阶逼近过程 |
| **显函数绘图** | `plot_animator.py` | ✅ 完成 | 支持常见数学函数，可配置颜色、线宽、动画风格 |
| **隐函数绘图** | `implicit_animator.py` | ✅ 完成 | 支持隐函数 F(x,y)=0 绘图，使用 Manim 原生 ImplicitFunction |
| **极坐标绘图** | `polar_animator.py` | ✅ 完成 | 支持极坐标 r(θ) 绘图，二维极坐标和三维球坐标 |
| **二维参数方程** | `plot_animator.py` | ✅ 完成 | 支持二维参数曲线 x(t), y(t) 绘图，参数验证和错误提示 |
| **微分展示动画** | `differentiation_animator.py` | ✅ 完成 | 展示割线逼近切线过程，可视化导数概念 |
| **积分展示动画** | `integration_animator.py` | ✅ 完成 | 黎曼和逼近过程，支持正负函数值区域 |
| **三维黎曼积分** | `three_d_animator.py` | ✅ 完成 | Wave of Boxes 风格，从大box到小box递进效果 |
| **三维相机设置** | `three_d_animator.py` | ✅ 完成 | 支持自定义相机角度、预设视角、保存/加载预设 |
| **三维场景绘制** | `three_d_animator.py` | ✅ 基础完成 | 支持曲面、曲线、平面绘制，自动旋转展示 |
| **Flask Web 服务** | `app.py` | ✅ 完成 | RESTful API 接口，后台任务处理 |
| **前端界面** | `index.html` + `script.js` | ✅ 完成 | 响应式界面，实时日志显示，隐函数/极坐标模式警告 |
| **环境配置脚本** | `setup_manim.bat/sh` | ✅ 完成 | 自动检测并创建 Conda 环境 |
| **启动脚本** | `start.bat/sh` | ✅ 完成 | 一键启动应用 |

### ⚠️ 部分完成/待改进功能

| 功能模块 | 状态 | 说明 |
|---------|------|------|
| **三维场景优化** | ⚠️ 基础完成 | 可考虑添加更多三维对象类型和交互 |
| **任务状态轮询** | ⚠️ 基础实现 | 可考虑使用 WebSocket 实现实时推送 |

### ❌ 未开始功能

| 功能模块 | 说明 |
|---------|------|
| **用户系统** | 无用户登录、权限管理 |
| **历史记录** | 无动画生成历史保存功能 |
| **批量处理** | 不支持批量生成动画 |
| **导出格式选择** | 仅支持 MP4，不支持 GIF/图片序列等 |

---

## 快速开始

### 1. 环境要求
- Anaconda 或 Miniconda
- Python 3.12
- 操作系统: Windows / Linux / macOS

### 2. 安装配置

**Windows:**
```batch
.\setup_manim.bat
```

**Linux/macOS:**
```bash
chmod +x setup_manim.sh
./setup_manim.sh
```

### 3. 启动应用

**Windows:**
```batch
.\start.bat
```

**Linux/macOS:**
```bash
chmod +x start.sh
./start.sh
```

### 4. 访问界面
启动后打开浏览器访问: `http://localhost:5000`

---

## API 接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/` | GET | 主页面 |
| `/api/switch_scene` | POST | 切换场景类型 (2D/3D) |
| `/api/switch_input_type` | POST | 切换输入类型 (显函数/隐函数) |
| `/api/process_visualization` | POST | 处理可视化请求 |
| `/api/task_status/<task_id>` | GET | 查询任务状态 |
| `/api/download_animation/<task_id>` | GET | 下载生成的动画 |

---

## 支持的数学函数

前端输入支持以下数学函数和常量:

- **三角函数**: `sin(x)`, `cos(x)`, `tan(x)`
- **指数对数**: `exp(x)`, `log(x)`
- **其他**: `sqrt(x)`, `x**n` (幂运算)
- **常量**: `pi`, `e`

---

## 开发计划

### 短期目标
1. 实现隐函数输入和绘制功能
2. 添加更多三维对象类型

### 中期目标
1. 添加用户系统和历史记录
2. 支持更多导出格式 (GIF, PNG序列)
3. 优化渲染性能

### 长期目标
1. 支持自定义动画脚本
2. 添加协作功能
3. 部署云端服务

---

## 贡献指南

欢迎提交 Issue 和 Pull Request!

---

## 许可证

本项目采用 Apache License 2.0 许可证。详见 [LICENSE](LICENSE) 文件。

---

*最后更新: 2026-03-31*
