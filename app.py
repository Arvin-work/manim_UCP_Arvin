from flask import Flask, render_template, request, jsonify, send_file
import json
import logging
import os
import tempfile
import threading
import traceback
from datetime import datetime

# 配置日志 - 更详细的配置
logging.basicConfig(
    level=logging.DEBUG,  # 改为 DEBUG 级别以获取更多信息
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('visualization.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# 在导入其他模块之前先记录日志
logger.info("开始导入模块...")

try:
    from taylor_animator import TaylorExpansionAnimator
    from plot_animator import FunctionPlotAnimator
    from differentiation_animator import DifferentiationAnimator
    from integration_animator import IntegrationAnimator
    from three_d_animator import ThreeDAnimator
    from implicit_animator import ImplicitFunctionAnimator
    from polar_animator import PolarAnimator
    logger.info("✅ 模块导入成功")
except ImportError as e:
    logger.error(f"❌ 模块导入失败: {e}")
    logger.error(traceback.format_exc())
    # 如果导入失败，创建空类防止应用崩溃
    class TaylorExpansionAnimator:
        def create_taylor_animation(self, *args, **kwargs):
            raise Exception("TaylorExpansionAnimator 未正确导入")
    
    class FunctionPlotAnimator:
        def create_function_plot(self, *args, **kwargs):
            raise Exception("FunctionPlotAnimator 未正确导入")
        
    class ThreeDAnimator:  # 添加空类
        def create_3d_animation(self, *args, **kwargs):
            raise Exception("ThreeDAnimator 未正确导入")
    
    class ImplicitFunctionAnimator:
        def create_implicit_plot(self, *args, **kwargs):
            raise Exception("ImplicitFunctionAnimator 未正确导入")
        def create_implicit_differentiation_animation(self, *args, **kwargs):
            raise Exception("ImplicitFunctionAnimator 未正确导入")
    
    class PolarAnimator:
        def create_polar_plot(self, *args, **kwargs):
            raise Exception("PolarAnimator 未正确导入")
        def create_spherical_plot(self, *args, **kwargs):
            raise Exception("PolarAnimator 未正确导入")

app = Flask(__name__)

# 全局动画生成器
try:
    animator = TaylorExpansionAnimator()
    plot_animator = FunctionPlotAnimator()
    differentiation_animator = DifferentiationAnimator()
    integration_animator = IntegrationAnimator()
    three_d_animator = ThreeDAnimator()
    implicit_animator = ImplicitFunctionAnimator()
    polar_animator = PolarAnimator()
    logger.info("✅ 动画生成器初始化成功")
except Exception as e:
    logger.error(f"❌ 动画生成器初始化失败: {e}")
    logger.error(traceback.format_exc())
    # 创建空的动画生成器实例
    animator = TaylorExpansionAnimator()
    plot_animator = FunctionPlotAnimator()
    integration_animator = IntegrationAnimator()
    three_d_animator = ThreeDAnimator()
    implicit_animator = ImplicitFunctionAnimator()
    polar_animator = PolarAnimator()

class VisualizationController:
    """可视化项目核心控制器"""
    
    def __init__(self):
        self.current_scene = "2D"
        self.current_input_type = "explicit"
        self.selected_functions = []
        self.animation_tasks = {}
        logger.info("✅ VisualizationController 初始化成功")
        
    def process_visualization_request(self, scene_data):
        """处理可视化请求"""
        try:
            logger.info(f"接收到可视化请求: {scene_data}")
            
            # 解析场景数据
            scene_type = scene_data.get('scene_type', '2D')
            input_type = scene_data.get('input_type', 'explicit')
            functions = scene_data.get('functions', [])
            parameters = scene_data.get('parameters', {})
            
            # 更新当前状态
            self.current_scene = scene_type
            self.current_input_type = input_type
            self.selected_functions = functions

            # 隐函数输入模式下的功能支持检查
            if input_type == 'implicit':
                unsupported_functions = []
                for func in functions:
                    if func in ['taylor', 'integration']:
                        unsupported_functions.append(func)
                
                if unsupported_functions:
                    func_names = {
                        'taylor': '泰勒展开',
                        'integration': '积分展示'
                    }
                    unsupported_names = [func_names.get(f, f) for f in unsupported_functions]
                    return {
                        "status": "error",
                        "message": f"隐函数输入模式下不支持以下功能: {', '.join(unsupported_names)}。隐函数模式仅支持: 单纯画图、微分展示",
                        "timestamp": datetime.now().isoformat()
                    }

            # 极坐标输入模式下的功能支持检查
            if input_type == 'polar':
                unsupported_functions = []
                for func in functions:
                    if func in ['taylor', 'integration', 'differentiation']:
                        unsupported_functions.append(func)
                
                if unsupported_functions:
                    func_names = {
                        'taylor': '泰勒展开',
                        'integration': '积分展示',
                        'differentiation': '微分展示'
                    }
                    unsupported_names = [func_names.get(f, f) for f in unsupported_functions]
                    return {
                        "status": "error",
                        "message": f"极坐标输入模式下不支持以下功能: {', '.join(unsupported_names)}。极坐标模式仅支持: 单纯画图",
                        "timestamp": datetime.now().isoformat()
                    }
            
            # 参数方程输入模式下的功能支持检查
            if input_type == 'parametric':
                unsupported_functions = []
                for func in functions:
                    if func in ['taylor', 'integration', 'differentiation']:
                        unsupported_functions.append(func)
                
                if unsupported_functions:
                    func_names = {
                        'taylor': '泰勒展开',
                        'integration': '积分展示',
                        'differentiation': '微分展示'
                    }
                    unsupported_names = [func_names.get(f, f) for f in unsupported_functions]
                    return {
                        "status": "error",
                        "message": f"参数方程输入模式下不支持以下功能: {', '.join(unsupported_names)}。参数方程模式仅支持: 单纯画图",
                        "timestamp": datetime.now().isoformat()
                    }

            # 处理参数方程绘制（仅三维模式）
            if scene_type == '3D' and input_type == 'parametric' and 'plot' in functions:
                task_id = self._start_parametric_plot(parameters)
                return {
                    "status": "processing",
                    "message": "参数方程图像生成中...",
                    "task_id": task_id,
                    "timestamp": datetime.now().isoformat()
                }

            # 处理三维场景绘制
            if scene_type == '3D' and 'plot' in functions:
                task_id = self._start_3d_plot(parameters)
                return {
                    "status": "processing",
                    "message": "三维场景绘制中...",
                    "task_id": task_id,
                    "timestamp": datetime.now().isoformat()
                }
            
            # 特别处理泰勒展开
            if 'taylor' in functions:
                task_id = self._start_taylor_animation(parameters)
                return {
                    "status": "processing",
                    "message": "泰勒展开动画生成中...",
                    "task_id": task_id,
                    "timestamp": datetime.now().isoformat()
                }
            
            # 处理绘图 - 区分显函数、隐函数、极坐标和参数方程
            if 'plot' in functions:
                if input_type == 'implicit':
                    task_id = self._start_implicit_plot(parameters)
                    return {
                        "status": "processing",
                        "message": "隐函数图像生成中...",
                        "task_id": task_id,
                        "timestamp": datetime.now().isoformat()
                    }
                elif input_type == 'polar':
                    task_id = self._start_polar_plot(parameters, scene_type)
                    return {
                        "status": "processing",
                        "message": "极坐标图像生成中...",
                        "task_id": task_id,
                        "timestamp": datetime.now().isoformat()
                    }
                elif input_type == 'parametric':
                    task_id = self._start_2d_parametric_plot(parameters)
                    return {
                        "status": "processing",
                        "message": "参数曲线图像生成中...",
                        "task_id": task_id,
                        "timestamp": datetime.now().isoformat()
                    }
                else:
                    task_id = self._start_function_plot(parameters)
                    return {
                        "status": "processing",
                        "message": "函数图像生成中...",
                        "task_id": task_id,
                        "timestamp": datetime.now().isoformat()
                    }
            
            # 处理微分展示 - 区分显函数和隐函数
            if 'differentiation' in functions:
                if input_type == 'implicit':
                    task_id = self._start_implicit_differentiation_animation(parameters)
                    return {
                        "status": "processing",
                        "message": "隐函数微分展示动画生成中...",
                        "task_id": task_id,
                        "timestamp": datetime.now().isoformat()
                    }
                else:
                    task_id = self._start_differentiation_animation(parameters)
                    return {
                        "status": "processing",
                        "message": "微分展示动画生成中...",
                        "task_id": task_id,
                        "timestamp": datetime.now().isoformat()
                    }
            
            # 处理积分展示
            if 'integration' in functions:
                if scene_type == '3D':
                    task_id = self._start_3d_integration_animation(parameters)
                else:
                    task_id = self._start_integration_animation(parameters)
                return {
                    "status": "processing",
                    "message": "积分展示动画生成中...",
                    "task_id": task_id,
                    "timestamp": datetime.now().isoformat()
                }
            
            # 打印场景信息
            self._log_scene_info(scene_type, input_type, functions, parameters)
            
            return {
                "status": "success",
                "message": f"{scene_type}场景处理完成",
                "timestamp": datetime.now().isoformat(),
                "data_received": scene_data
            }
            
        except Exception as e:
            logger.error(f"处理可视化请求时出错: {str(e)}")
            logger.error(traceback.format_exc())
            return {
                "status": "error",
                "message": str(e)
            }

    def _start_2d_parametric_plot(self, parameters):
        """启动二维参数曲线绘制任务"""
        try:
            parametric_config = parameters.get('parametric', {})
            
            x_expr = parametric_config.get('x_expr', '')
            y_expr = parametric_config.get('y_expr', '')
            
            t_range_str = parametric_config.get('t_range', '0,6.28')
            try:
                t_range = [float(t.strip()) for t in t_range_str.split(',')]
            except:
                t_range = [0, 2 * 3.14159]
            
            color_scheme = parameters.get('color_scheme', 'blue')
            stroke_width = parameters.get('stroke_width', '4')
            
            logger.info(f"二维参数曲线参数 - x(t)={x_expr}, y(t)={y_expr}")
            logger.info(f"参数范围 - t: {t_range}")
            
            task_id = f"parametric_2d_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            def generate_plot():
                try:
                    logger.info(f"开始生成二维参数曲线图像")
                    
                    output_dir = os.path.join(tempfile.gettempdir(), "manim_parametric_2d")
                    os.makedirs(output_dir, exist_ok=True)
                    output_file = os.path.join(output_dir, f"{task_id}.mp4")
                    
                    video_path = plot_animator.create_2d_parametric_curve(
                        x_expr, y_expr,
                        t_range=tuple(t_range),
                        color_scheme=color_scheme,
                        stroke_width=int(stroke_width) if stroke_width.isdigit() else 4,
                        output_file=output_file
                    )
                    
                    self.animation_tasks[task_id] = {
                        'status': 'completed',
                        'video_path': video_path,
                        'created_at': datetime.now().isoformat()
                    }
                    
                    logger.info(f"二维参数曲线图像生成完成: {video_path}")
                    plot_animator.play_animation(video_path)
                    
                except Exception as e:
                    logger.error(f"生成二维参数曲线图像失败: {str(e)}")
                    logger.error(traceback.format_exc())
                    self.animation_tasks[task_id] = {
                        'status': 'error',
                        'error': str(e),
                        'created_at': datetime.now().isoformat()
                    }
            
            thread = threading.Thread(target=generate_plot)
            thread.daemon = True
            thread.start()
            
            return task_id
            
        except Exception as e:
            logger.error(f"启动二维参数曲线任务失败: {str(e)}")
            raise

    def _start_function_plot(self, parameters):
        """启动显函数绘制任务"""
        try:
            # 提取参数
            func_expression = parameters.get('function_expression', '')
            x_range_str = parameters.get('x_range', '-10,10')
            y_range_str = parameters.get('y_range', '-10,10')
            resolution = parameters.get('resolution', '100')
            color_scheme = parameters.get('color_scheme', 'yellow')
            stroke_width = parameters.get('stroke_width', '4')
            animation_style = parameters.get('animation_style', 'none')
            
            # 解析范围参数
            try:
                x_range = [float(x.strip()) for x in x_range_str.split(',')]
                y_range = [float(y.strip()) for y in y_range_str.split(',')]
            except:
                x_range = [-10, 10]
                y_range = [-10, 10]
            
            # 解析其他参数
            try:
                resolution = int(resolution)
                stroke_width = int(stroke_width)
            except:
                resolution = 100
                stroke_width = 4
            
            # 生成任务ID
            task_id = f"plot_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # 在后台线程中生成图像
            def generate_plot():
                try:
                    logger.info(f"开始生成函数图像: {func_expression}")
                    
                    # 创建输出目录
                    output_dir = os.path.join(tempfile.gettempdir(), "manim_plots")
                    os.makedirs(output_dir, exist_ok=True)
                    output_file = os.path.join(output_dir, f"{task_id}.mp4")
                    
                    # 生成函数图像
                    video_path = plot_animator.create_function_plot(
                        func_expression,
                        tuple(x_range),
                        tuple(y_range),
                        resolution,
                        color_scheme,
                        stroke_width,
                        animation_style,
                        output_file
                    )
                    
                    self.animation_tasks[task_id] = {
                        'status': 'completed',
                        'video_path': video_path,
                        'created_at': datetime.now().isoformat()
                    }
                    
                    logger.info(f"函数图像生成完成: {video_path}")
                    
                    # 自动播放动画
                    plot_animator.play_animation(video_path)
                    
                except Exception as e:
                    logger.error(f"生成函数图像失败: {str(e)}")
                    logger.error(traceback.format_exc())
                    self.animation_tasks[task_id] = {
                        'status': 'error',
                        'error': str(e),
                        'created_at': datetime.now().isoformat()
                    }
            
            # 启动后台任务
            thread = threading.Thread(target=generate_plot)
            thread.daemon = True
            thread.start()
            
            # 记录任务信息
            self.animation_tasks[task_id] = {
                'status': 'processing',
                'created_at': datetime.now().isoformat()
            }
            
            return task_id
            
        except Exception as e:
            logger.error(f"启动函数绘制任务失败: {str(e)}")
            logger.error(traceback.format_exc())
            raise

    def _start_taylor_animation(self, parameters):
        """启动泰勒展开动画生成任务"""
        try:
            # 提取参数
            func_expression = parameters.get('function_expression', '')
            taylor_config = parameters.get('taylor_expansion', {})
            expansion_point = taylor_config.get('expansion_point', 0)
            max_order = taylor_config.get('max_order', 10)
            
            # 解析范围参数
            x_range_str = parameters.get('x_range', '-3,3')
            y_range_str = parameters.get('y_range', '-2,2')
            
            try:
                x_range = [float(x.strip()) for x in x_range_str.split(',')]
                y_range = [float(y.strip()) for y in y_range_str.split(',')]
            except:
                x_range = [-3, 3]
                y_range = [-2, 2]
            
            # 生成任务ID
            task_id = f"taylor_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # 在后台线程中生成动画
            def generate_animation():
                try:
                    logger.info(f"开始生成泰勒展开动画: {func_expression} 在 x={expansion_point}")
                    
                    # 创建输出目录
                    output_dir = os.path.join(tempfile.gettempdir(), "manim_animations")
                    os.makedirs(output_dir, exist_ok=True)
                    output_file = os.path.join(output_dir, f"{task_id}.mp4")
                    
                    # 生成动画
                    video_path = animator.create_taylor_animation(
                        func_expression,
                        expansion_point,
                        max_order,
                        tuple(x_range),
                        tuple(y_range),
                        output_file
                    )
                    
                    self.animation_tasks[task_id] = {
                        'status': 'completed',
                        'video_path': video_path,
                        'created_at': datetime.now().isoformat()
                    }
                    
                    logger.info(f"泰勒展开动画生成完成: {video_path}")
                    
                    # 自动播放动画
                    animator.play_animation(video_path)
                    
                except Exception as e:
                    logger.error(f"生成泰勒展开动画失败: {str(e)}")
                    logger.error(traceback.format_exc())
                    self.animation_tasks[task_id] = {
                        'status': 'error',
                        'error': str(e),
                        'created_at': datetime.now().isoformat()
                    }
            
            # 启动后台任务
            thread = threading.Thread(target=generate_animation)
            thread.daemon = True
            thread.start()
            
            # 记录任务信息
            self.animation_tasks[task_id] = {
                'status': 'processing',
                'created_at': datetime.now().isoformat()
            }
            
            return task_id
            
        except Exception as e:
            logger.error(f"启动泰勒动画任务失败: {str(e)}")
            logger.error(traceback.format_exc())
            raise
    
    def _start_differentiation_animation(self, parameters):
        """启动微分展示动画生成任务"""
        try:
            differentiation_config = parameters.get('differentiation', {})
            
            if differentiation_config.get('is_3d'):
                return self._start_3d_differentiation_animation(parameters)
            
            func_expression = parameters.get('function_expression', '')
            
            fit_point = differentiation_config.get('fit_point', 0)
            radius = differentiation_config.get('radius', 1)
            
            fit_point = float(fit_point)
            radius = float(radius)
                
            logger.info(f"微分展示参数 - 函数: {func_expression}, 拟合点: {fit_point}, 半径: {radius}")

            logger.info(f"微分展示参数 - 函数: {func_expression}")
            logger.info(f"微分展示参数 - 拟合点: {fit_point}, 半径: {radius}")
            logger.info(f"微分展示参数 - differentiation_config: {differentiation_config}")
            
            try:
                fit_point = float(fit_point)
                radius = float(radius)
            except (ValueError, TypeError) as e:
                logger.error(f"参数类型转换错误: {e}")
                raise ValueError("拟合点和半径必须是数字")
            
            x_range_str = parameters.get('x_range', '-10,10')
            y_range_str = parameters.get('y_range', '-10,10')
            
            try:
                x_range = [float(x.strip()) for x in x_range_str.split(',')]
                y_range = [float(y.strip()) for y in y_range_str.split(',')]
            except:
                x_range = [-10, 10]
                y_range = [-10, 10]
            
            task_id = f"diff_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            def generate_animation():
                try:
                    logger.info(f"开始生成微分展示动画: {func_expression} 在 x={fit_point}")
                    
                    output_dir = os.path.join(tempfile.gettempdir(), "manim_differentiation")
                    os.makedirs(output_dir, exist_ok=True)
                    output_file = os.path.join(output_dir, f"{task_id}.mp4")
                    
                    video_path = differentiation_animator.create_differentiation_animation(
                        func_expression,
                        fit_point,
                        radius,
                        tuple(x_range),
                        tuple(y_range),
                        output_file
                    )
                    
                    self.animation_tasks[task_id] = {
                        'status': 'completed',
                        'video_path': video_path,
                        'created_at': datetime.now().isoformat()
                    }
                    
                    logger.info(f"微分展示动画生成完成: {video_path}")
                    
                    differentiation_animator.play_animation(video_path)
                    
                except Exception as e:
                    logger.error(f"生成微分展示动画失败: {str(e)}")
                    logger.error(traceback.format_exc())
                    self.animation_tasks[task_id] = {
                        'status': 'error',
                        'error': str(e),
                        'created_at': datetime.now().isoformat()
                    }
            
            thread = threading.Thread(target=generate_animation)
            thread.daemon = True
            thread.start()
            
            self.animation_tasks[task_id] = {
                'status': 'processing',
                'created_at': datetime.now().isoformat()
            }
            
            return task_id
            
        except Exception as e:
            logger.error(f"启动微分展示动画任务失败: {str(e)}")
            raise
    
    def _start_3d_differentiation_animation(self, parameters):
        """启动三维微分展示动画生成任务"""
        try:
            differentiation_config = parameters.get('differentiation', {})
            parametric = differentiation_config.get('parametric', {})
            
            x_expr = parametric.get('x_expr', '')
            y_expr = parametric.get('y_expr', '')
            z_expr = parametric.get('z_expr', '')
            
            t_range_str = parametric.get('t_range', '0,6.28')
            try:
                t_range = [float(t.strip()) for t in t_range_str.split(',')]
            except:
                t_range = [0, 2 * 3.14159]
            
            animation_duration = differentiation_config.get('animation_duration', 5)
            tangent_scale = differentiation_config.get('tangent_scale', 1)
            
            camera_config = parameters.get('camera', {})
            camera_phi = camera_config.get('phi', 45)
            camera_theta = camera_config.get('theta', -45)
            
            logger.info(f"三维微分展示参数 - x(t)={x_expr}, y(t)={y_expr}, z(t)={z_expr}")
            logger.info(f"参数范围 - t: {t_range}, 动画时长: {animation_duration}秒")
            logger.info(f"相机参数 - φ: {camera_phi}°, θ: {camera_theta}°")
            
            task_id = f"3d_diff_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            def generate_animation():
                try:
                    logger.info(f"开始生成三维微分展示动画")
                    
                    output_dir = os.path.join(tempfile.gettempdir(), "manim_3d_differentiation")
                    os.makedirs(output_dir, exist_ok=True)
                    output_file = os.path.join(output_dir, f"{task_id}.mp4")
                    
                    video_path = three_d_animator.create_3d_differentiation_animation(
                        x_expr, y_expr, z_expr,
                        t_range=tuple(t_range),
                        animation_duration=animation_duration,
                        tangent_scale=tangent_scale,
                        camera_phi=camera_phi,
                        camera_theta=camera_theta,
                        output_file=output_file
                    )
                    
                    self.animation_tasks[task_id] = {
                        'status': 'completed',
                        'video_path': video_path,
                        'created_at': datetime.now().isoformat()
                    }
                    
                    logger.info(f"三维微分展示动画生成完成: {video_path}")
                    three_d_animator.play_animation(video_path)
                    
                except Exception as e:
                    logger.error(f"生成三维微分展示动画失败: {str(e)}")
                    logger.error(traceback.format_exc())
                    self.animation_tasks[task_id] = {
                        'status': 'error',
                        'error': str(e),
                        'created_at': datetime.now().isoformat()
                    }
            
            thread = threading.Thread(target=generate_animation)
            thread.daemon = True
            thread.start()
            
            self.animation_tasks[task_id] = {
                'status': 'processing',
                'created_at': datetime.now().isoformat()
            }
            
            return task_id
            
        except Exception as e:
            logger.error(f"启动三维微分展示动画任务失败: {str(e)}")
            raise

    def _start_integration_animation(self, parameters):
        """启动积分展示动画生成任务"""
        try:
            # 提取参数
            func_expression = parameters.get('function_expression', '')
            
            # 从 integration 配置中获取参数
            integration_config = parameters.get('integration', {})
            lower_bound = integration_config.get('lower_bound', 0)
            upper_bound = integration_config.get('upper_bound', 1)
            
            # 确保参数类型正确
            lower_bound = float(lower_bound)
            upper_bound = float(upper_bound)
            
            # 解析范围参数
            x_range_str = parameters.get('x_range', '-10,10')
            y_range_str = parameters.get('y_range', '-10,10')
            
            try:
                x_range = [float(x.strip()) for x in x_range_str.split(',')]
                y_range = [float(y.strip()) for y in y_range_str.split(',')]
            except:
                x_range = [-10, 10]
                y_range = [-10, 10]
            
            # 生成任务ID
            task_id = f"integ_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # 在后台线程中生成动画
            def generate_animation():
                try:
                    logger.info(f"开始生成积分展示动画: {func_expression} 区间 [{lower_bound}, {upper_bound}]")
                    
                    # 创建输出目录
                    output_dir = os.path.join(tempfile.gettempdir(), "manim_integration")
                    os.makedirs(output_dir, exist_ok=True)
                    output_file = os.path.join(output_dir, f"{task_id}.mp4")
                    
                    # 生成动画
                    video_path = integration_animator.create_integration_animation(
                        func_expression,
                        lower_bound,
                        upper_bound,
                        tuple(x_range),
                        tuple(y_range),
                        output_file
                    )
                    
                    self.animation_tasks[task_id] = {
                        'status': 'completed',
                        'video_path': video_path,
                        'created_at': datetime.now().isoformat()
                    }
                    
                    logger.info(f"积分展示动画生成完成: {video_path}")
                    
                    # 自动播放动画
                    integration_animator.play_animation(video_path)
                    
                except Exception as e:
                    logger.error(f"生成积分展示动画失败: {str(e)}")
                    logger.error(traceback.format_exc())
                    self.animation_tasks[task_id] = {
                        'status': 'error',
                        'error': str(e),
                        'created_at': datetime.now().isoformat()
                    }
            
            # 启动后台任务
            thread = threading.Thread(target=generate_animation)
            thread.daemon = True
            thread.start()
            
            # 记录任务信息
            self.animation_tasks[task_id] = {
                'status': 'processing',
                'created_at': datetime.now().isoformat()
            }
            
            return task_id
            
        except Exception as e:
            logger.error(f"启动积分展示动画任务失败: {str(e)}")
            raise

    def _start_integration_animation(self, parameters):
        """启动积分展示动画生成任务"""
        try:
            # 提取参数
            func_expression = parameters.get('function_expression', '')
            
            # 从 integration 配置中获取参数
            integration_config = parameters.get('integration', {})
            lower_bound = integration_config.get('lower_bound', 0)
            upper_bound = integration_config.get('upper_bound', 1)
            
            # 确保参数类型正确
            lower_bound = float(lower_bound)
            upper_bound = float(upper_bound)
            
            # 解析范围参数
            x_range_str = parameters.get('x_range', '-10,10')
            y_range_str = parameters.get('y_range', '-10,10')
            
            try:
                x_range = [float(x.strip()) for x in x_range_str.split(',')]
                y_range = [float(y.strip()) for y in y_range_str.split(',')]
            except:
                x_range = [-10, 10]
                y_range = [-10, 10]
            
            # 生成任务ID
            task_id = f"integ_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # 在后台线程中生成动画
            def generate_animation():
                try:
                    logger.info(f"开始生成积分展示动画: {func_expression} 区间 [{lower_bound}, {upper_bound}]")
                    
                    # 创建输出目录
                    output_dir = os.path.join(tempfile.gettempdir(), "manim_integration")
                    os.makedirs(output_dir, exist_ok=True)
                    output_file = os.path.join(output_dir, f"{task_id}.mp4")
                    
                    # 生成动画
                    video_path = integration_animator.create_integration_animation(
                        func_expression,
                        lower_bound,
                        upper_bound,
                        tuple(x_range),
                        tuple(y_range),
                        output_file
                    )
                    
                    self.animation_tasks[task_id] = {
                        'status': 'completed',
                        'video_path': video_path,
                        'created_at': datetime.now().isoformat()
                    }
                    
                    logger.info(f"积分展示动画生成完成: {video_path}")
                    
                    # 自动播放动画
                    integration_animator.play_animation(video_path)
                    
                except Exception as e:
                    logger.error(f"生成积分展示动画失败: {str(e)}")
                    logger.error(traceback.format_exc())
                    self.animation_tasks[task_id] = {
                        'status': 'error',
                        'error': str(e),
                        'created_at': datetime.now().isoformat()
                    }
            
            # 启动后台任务
            thread = threading.Thread(target=generate_animation)
            thread.daemon = True
            thread.start()
            
            # 记录任务信息
            self.animation_tasks[task_id] = {
                'status': 'processing',
                'created_at': datetime.now().isoformat()
            }
            
            return task_id
            
        except Exception as e:
            logger.error(f"启动积分展示动画任务失败: {str(e)}")
            raise
    
    def _start_3d_integration_animation(self, parameters):
        """启动三维黎曼积分展示动画生成任务"""
        try:
            integration_config = parameters.get('integration', {})
            
            func_expression = parameters.get('function_expression', '')
            
            x_range_str = parameters.get('x_range', '-3,3')
            y_range_str = parameters.get('y_range', '-3,3')
            
            try:
                x_range = [float(x.strip()) for x in x_range_str.split(',')]
                y_range = [float(y.strip()) for y in y_range_str.split(',')]
            except:
                x_range = [-3, 3]
                y_range = [-3, 3]
            
            subdivisions = integration_config.get('subdivisions', 10)
            animation_duration = integration_config.get('animation_duration', 5)
            show_progression = integration_config.get('show_progression', True)
            
            camera_config = parameters.get('camera', {})
            camera_phi = camera_config.get('phi', 45)
            camera_theta = camera_config.get('theta', -45)
            
            logger.info(f"三维黎曼积分参数 - 函数: {func_expression}")
            logger.info(f"坐标范围 - X: {x_range}, Y: {y_range}")
            logger.info(f"细分数量: {subdivisions}, 动画时长: {animation_duration}秒")
            logger.info(f"相机参数 - φ: {camera_phi}°, θ: {camera_theta}°")
            
            task_id = f"3d_integ_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            def generate_animation():
                try:
                    logger.info(f"开始生成三维黎曼积分动画")
                    
                    output_dir = os.path.join(tempfile.gettempdir(), "manim_3d_integration")
                    os.makedirs(output_dir, exist_ok=True)
                    output_file = os.path.join(output_dir, f"{task_id}.mp4")
                    
                    video_path = three_d_animator.create_3d_riemann_integration(
                        func_expression,
                        x_range=tuple(x_range),
                        y_range=tuple(y_range),
                        subdivisions=subdivisions,
                        animation_duration=animation_duration,
                        show_progression=show_progression,
                        camera_phi=camera_phi,
                        camera_theta=camera_theta,
                        output_file=output_file
                    )
                    
                    self.animation_tasks[task_id] = {
                        'status': 'completed',
                        'video_path': video_path,
                        'created_at': datetime.now().isoformat()
                    }
                    
                    logger.info(f"三维黎曼积分动画生成完成: {video_path}")
                    three_d_animator.play_animation(video_path)
                    
                except Exception as e:
                    logger.error(f"生成三维黎曼积分动画失败: {str(e)}")
                    logger.error(traceback.format_exc())
                    self.animation_tasks[task_id] = {
                        'status': 'error',
                        'error': str(e),
                        'created_at': datetime.now().isoformat()
                    }
            
            thread = threading.Thread(target=generate_animation)
            thread.daemon = True
            thread.start()
            
            self.animation_tasks[task_id] = {
                'status': 'processing',
                'created_at': datetime.now().isoformat()
            }
            
            return task_id
            
        except Exception as e:
            logger.error(f"启动三维黎曼积分动画任务失败: {str(e)}")
            raise

    def _start_3d_plot(self, parameters):
        """启动三维场景绘制任务"""
        try:
            # 提取参数
            func_expression = parameters.get('function_expression', '')
            
            # 获取绘制类型
            plot_type = parameters.get('plot_type', 'auto')
            
            # 解析范围参数
            x_range_str = parameters.get('x_range', '-5,5')
            y_range_str = parameters.get('y_range', '-5,5')
            z_range_str = parameters.get('z_range', '-5,5')
            
            try:
                x_range = [float(x.strip()) for x in x_range_str.split(',')]
                y_range = [float(y.strip()) for y in y_range_str.split(',')]
                z_range = [float(z.strip()) for z in z_range_str.split(',')]
            except:
                x_range = [-5, 5]
                y_range = [-5, 5]
                z_range = [-5, 5]
            
            camera_config = parameters.get('camera', {})
            camera_phi = camera_config.get('phi', 45)
            camera_theta = camera_config.get('theta', -45)
            
            logger.info(f"相机参数 - φ: {camera_phi}°, θ: {camera_theta}°")
            
            # 生成任务ID
            task_id = f"3d_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # 在后台线程中生成动画
            def generate_animation():
                try:
                    logger.info(f"开始生成三维场景动画: {func_expression}, 绘制类型: {plot_type}")
                    
                    # 创建输出目录
                    output_dir = os.path.join(tempfile.gettempdir(), "manim_3d")
                    os.makedirs(output_dir, exist_ok=True)
                    output_file = os.path.join(output_dir, f"{task_id}.mp4")
                    
                    # 生成动画
                    video_path = three_d_animator.create_3d_animation(
                        func_expression,
                        plot_type,
                        tuple(x_range),
                        tuple(y_range),
                        tuple(z_range),
                        camera_phi=camera_phi,
                        camera_theta=camera_theta,
                        output_file=output_file
                    )
                    
                    self.animation_tasks[task_id] = {
                        'status': 'completed',
                        'video_path': video_path,
                        'created_at': datetime.now().isoformat()
                    }
                    
                    logger.info(f"三维场景动画生成完成: {video_path}")
                    
                    # 自动播放动画
                    three_d_animator.play_animation(video_path)
                    
                except Exception as e:
                    logger.error(f"生成三维场景动画失败: {str(e)}")
                    logger.error(traceback.format_exc())
                    self.animation_tasks[task_id] = {
                        'status': 'error',
                        'error': str(e),
                        'created_at': datetime.now().isoformat()
                    }
            
            # 启动后台任务
            thread = threading.Thread(target=generate_animation)
            thread.daemon = True
            thread.start()
            
            # 记录任务信息
            self.animation_tasks[task_id] = {
                'status': 'processing',
                'created_at': datetime.now().isoformat()
            }
            
            return task_id
            
        except Exception as e:
            logger.error(f"启动三维场景动画任务失败: {str(e)}")
            raise
    
    def _start_implicit_plot(self, parameters):
        """启动隐函数绘图任务"""
        try:
            func_expression = parameters.get('function_expression', '')
            x_range_str = parameters.get('x_range', '-10,10')
            y_range_str = parameters.get('y_range', '-10,10')
            resolution = parameters.get('resolution', '200')
            color_scheme = parameters.get('color_scheme', 'yellow')
            stroke_width = parameters.get('stroke_width', '4')
            animation_style = parameters.get('animation_style', 'none')
            
            try:
                x_range = [float(x.strip()) for x in x_range_str.split(',')]
                y_range = [float(y.strip()) for y in y_range_str.split(',')]
            except:
                x_range = [-10, 10]
                y_range = [-10, 10]
            
            try:
                resolution = int(resolution)
                stroke_width = int(stroke_width)
            except:
                resolution = 200
                stroke_width = 4
            
            task_id = f"implicit_plot_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            def generate_plot():
                try:
                    logger.info(f"开始生成隐函数图像: {func_expression}")
                    
                    output_dir = os.path.join(tempfile.gettempdir(), "manim_implicit")
                    os.makedirs(output_dir, exist_ok=True)
                    output_file = os.path.join(output_dir, f"{task_id}.mp4")
                    
                    video_path = implicit_animator.create_implicit_plot(
                        func_expression,
                        tuple(x_range),
                        tuple(y_range),
                        resolution,
                        color_scheme,
                        stroke_width,
                        animation_style,
                        output_file
                    )
                    
                    self.animation_tasks[task_id] = {
                        'status': 'completed',
                        'video_path': video_path,
                        'created_at': datetime.now().isoformat()
                    }
                    
                    logger.info(f"隐函数图像生成完成: {video_path}")
                    implicit_animator.play_animation(video_path)
                    
                except Exception as e:
                    logger.error(f"生成隐函数图像失败: {str(e)}")
                    logger.error(traceback.format_exc())
                    self.animation_tasks[task_id] = {
                        'status': 'error',
                        'error': str(e),
                        'created_at': datetime.now().isoformat()
                    }
            
            thread = threading.Thread(target=generate_plot)
            thread.daemon = True
            thread.start()
            
            self.animation_tasks[task_id] = {
                'status': 'processing',
                'created_at': datetime.now().isoformat()
            }
            
            return task_id
            
        except Exception as e:
            logger.error(f"启动隐函数绘图任务失败: {str(e)}")
            logger.error(traceback.format_exc())
            raise
    
    def _start_implicit_differentiation_animation(self, parameters):
        """启动隐函数微分展示动画任务"""
        try:
            func_expression = parameters.get('function_expression', '')
            
            differentiation_config = parameters.get('differentiation', {})
            fit_point_x = differentiation_config.get('fit_point', 0)
            
            try:
                fit_point_x = float(fit_point_x)
            except (ValueError, TypeError) as e:
                logger.error(f"参数类型转换错误: {e}")
                raise ValueError("拟合点必须是数字")
            
            x_range_str = parameters.get('x_range', '-10,10')
            y_range_str = parameters.get('y_range', '-10,10')
            
            try:
                x_range = [float(x.strip()) for x in x_range_str.split(',')]
                y_range = [float(y.strip()) for y in y_range_str.split(',')]
            except:
                x_range = [-10, 10]
                y_range = [-10, 10]
            
            task_id = f"implicit_diff_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            def generate_animation():
                try:
                    logger.info(f"开始生成隐函数微分展示动画: {func_expression} 在 x={fit_point_x}")
                    
                    output_dir = os.path.join(tempfile.gettempdir(), "manim_implicit_diff")
                    os.makedirs(output_dir, exist_ok=True)
                    output_file = os.path.join(output_dir, f"{task_id}.mp4")
                    
                    video_path = implicit_animator.create_implicit_differentiation_animation(
                        func_expression,
                        fit_point_x,
                        tuple(x_range),
                        tuple(y_range),
                        200,
                        output_file
                    )
                    
                    self.animation_tasks[task_id] = {
                        'status': 'completed',
                        'video_path': video_path,
                        'created_at': datetime.now().isoformat()
                    }
                    
                    logger.info(f"隐函数微分展示动画生成完成: {video_path}")
                    implicit_animator.play_animation(video_path)
                    
                except Exception as e:
                    logger.error(f"生成隐函数微分展示动画失败: {str(e)}")
                    logger.error(traceback.format_exc())
                    self.animation_tasks[task_id] = {
                        'status': 'error',
                        'error': str(e),
                        'created_at': datetime.now().isoformat()
                    }
            
            thread = threading.Thread(target=generate_animation)
            thread.daemon = True
            thread.start()
            
            self.animation_tasks[task_id] = {
                'status': 'processing',
                'created_at': datetime.now().isoformat()
            }
            
            return task_id
            
        except Exception as e:
            logger.error(f"启动隐函数微分展示动画任务失败: {str(e)}")
            raise
    
    def _start_polar_plot(self, parameters, scene_type='2D'):
        """启动极坐标绘图任务"""
        try:
            polar_config = parameters.get('polar', {})
            r_expression = polar_config.get('r_expression', '')
            phi_expression = polar_config.get('phi_expression', '')
            radius_max = polar_config.get('radius_max', 4)
            azimuth_step = polar_config.get('azimuth_step', 30)
            radius_step = polar_config.get('radius_step', 1)
            theta_range_str = polar_config.get('theta_range', '0,6.28')
            
            color_scheme = parameters.get('color_scheme', 'red')
            stroke_width = parameters.get('stroke_width', '3')
            animation_style = parameters.get('animation_style', 'draw')
            
            try:
                radius_max = float(radius_max)
                azimuth_step = float(azimuth_step)
                radius_step = float(radius_step)
                stroke_width = int(stroke_width)
            except:
                radius_max = 4
                azimuth_step = 30
                radius_step = 1
                stroke_width = 3
            
            try:
                theta_range = [float(t.strip()) for t in theta_range_str.split(',')]
            except:
                theta_range = [0, 2 * 3.14159]
            
            task_id = f"polar_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            def generate_plot():
                try:
                    logger.info(f"开始生成极坐标图像: r = {r_expression}")
                    
                    output_dir = os.path.join(tempfile.gettempdir(), "manim_polar")
                    os.makedirs(output_dir, exist_ok=True)
                    output_file = os.path.join(output_dir, f"{task_id}.mp4")
                    
                    if scene_type == '3D' and phi_expression:
                        video_path = polar_animator.create_spherical_plot(
                            r_expression,
                            phi_expression,
                            theta_range=tuple(theta_range),
                            color_scheme=color_scheme,
                            animation_style=animation_style,
                            output_file=output_file
                        )
                    else:
                        video_path = polar_animator.create_polar_plot(
                            r_expression,
                            radius_max=radius_max,
                            azimuth_step=azimuth_step,
                            radius_step=radius_step,
                            theta_range=tuple(theta_range),
                            color_scheme=color_scheme,
                            stroke_width=stroke_width,
                            animation_style=animation_style,
                            output_file=output_file
                        )
                    
                    self.animation_tasks[task_id] = {
                        'status': 'completed',
                        'video_path': video_path,
                        'created_at': datetime.now().isoformat()
                    }
                    
                    logger.info(f"极坐标图像生成完成: {video_path}")
                    polar_animator.play_animation(video_path)
                    
                except Exception as e:
                    logger.error(f"生成极坐标图像失败: {str(e)}")
                    logger.error(traceback.format_exc())
                    self.animation_tasks[task_id] = {
                        'status': 'error',
                        'error': str(e),
                        'created_at': datetime.now().isoformat()
                    }
            
            thread = threading.Thread(target=generate_plot)
            thread.daemon = True
            thread.start()
            
            self.animation_tasks[task_id] = {
                'status': 'processing',
                'created_at': datetime.now().isoformat()
            }
            
            return task_id
            
        except Exception as e:
            logger.error(f"启动极坐标绘图任务失败: {str(e)}")
            raise
    
    def _start_parametric_plot(self, parameters):
        """启动参数方程绘图任务"""
        try:
            parametric_config = parameters.get('parametric', {})
            mode = parametric_config.get('mode', 'curve')
            
            x_expr = parametric_config.get('x_expr', '')
            y_expr = parametric_config.get('y_expr', '')
            z_expr = parametric_config.get('z_expr', '')
            
            color_scheme = parameters.get('color_scheme', 'blue')
            
            camera_config = parameters.get('camera', {})
            camera_phi = camera_config.get('phi', 45)
            camera_theta = camera_config.get('theta', -45)
            
            logger.info(f"相机参数 - φ: {camera_phi}°, θ: {camera_theta}°")
            
            task_id = f"parametric_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            def generate_plot():
                try:
                    logger.info(f"开始生成参数方程图像: mode={mode}")
                    
                    output_dir = os.path.join(tempfile.gettempdir(), "manim_parametric")
                    os.makedirs(output_dir, exist_ok=True)
                    output_file = os.path.join(output_dir, f"{task_id}.mp4")
                    
                    if mode == 'curve':
                        t_range_str = parametric_config.get('t_range', '0,6.28')
                        try:
                            t_range = [float(t.strip()) for t in t_range_str.split(',')]
                        except:
                            t_range = [0, 2 * 3.14159]
                        
                        video_path = three_d_animator.create_parametric_curve(
                            x_expr, y_expr, z_expr,
                            t_range=tuple(t_range),
                            color_scheme=color_scheme,
                            camera_phi=camera_phi,
                            camera_theta=camera_theta,
                            output_file=output_file
                        )
                    else:
                        u_range_str = parametric_config.get('u_range', '0,6.28')
                        v_range_str = parametric_config.get('v_range', '0,3.14')
                        
                        try:
                            u_range = [float(u.strip()) for u in u_range_str.split(',')]
                            v_range = [float(v.strip()) for v in v_range_str.split(',')]
                        except:
                            u_range = [0, 2 * 3.14159]
                            v_range = [0, 3.14159]
                        
                        video_path = three_d_animator.create_parametric_surface(
                            x_expr, y_expr, z_expr,
                            u_range=tuple(u_range),
                            v_range=tuple(v_range),
                            color_scheme=color_scheme,
                            camera_phi=camera_phi,
                            camera_theta=camera_theta,
                            output_file=output_file
                        )
                    
                    self.animation_tasks[task_id] = {
                        'status': 'completed',
                        'video_path': video_path,
                        'created_at': datetime.now().isoformat()
                    }
                    
                    logger.info(f"参数方程图像生成完成: {video_path}")
                    three_d_animator.play_animation(video_path)
                    
                except Exception as e:
                    logger.error(f"生成参数方程图像失败: {str(e)}")
                    logger.error(traceback.format_exc())
                    self.animation_tasks[task_id] = {
                        'status': 'error',
                        'error': str(e),
                        'created_at': datetime.now().isoformat()
                    }
            
            thread = threading.Thread(target=generate_plot)
            thread.daemon = True
            thread.start()
            
            self.animation_tasks[task_id] = {
                'status': 'processing',
                'created_at': datetime.now().isoformat()
            }
            
            return task_id
            
        except Exception as e:
            logger.error(f"启动参数方程绘图任务失败: {str(e)}")
            raise
    
    def get_task_status(self, task_id):
        """获取任务状态"""
        return self.animation_tasks.get(task_id, {'status': 'not_found'})
    
    def _log_scene_info(self, scene_type, input_type, functions, parameters):
        """记录场景信息"""
        logger.info("=" * 50)
        logger.info("场景配置信息")
        logger.info("=" * 50)
        logger.info(f"场景类型: {scene_type}")
        logger.info(f"输入类型: {input_type}")
        logger.info(f"功能选项: {', '.join(functions)}")
        
        # 特别显示泰勒展开参数
        if 'taylor' in functions and 'taylor_expansion' in parameters:
            taylor_config = parameters['taylor_expansion']
            logger.info(f"泰勒展开点: {taylor_config.get('expansion_point', '未设置')}")
            logger.info(f"最高阶数: {taylor_config.get('max_order', '未设置')}")
        
        logger.info(f"参数配置: {json.dumps(parameters, indent=2, ensure_ascii=False)}")
        logger.info("=" * 50)

# 初始化控制器
try:
    controller = VisualizationController()
    logger.info("✅ 控制器初始化成功")
except Exception as e:
    logger.error(f"❌ 控制器初始化失败: {e}")
    logger.error(traceback.format_exc())
    controller = None

@app.route('/')
def index():
    """主页面"""
    logger.info("访问主页")
    return render_template('index.html')

@app.route('/api/switch_scene', methods=['POST'])
def switch_scene():
    """切换2D/3D场景"""
    data = request.json
    scene_type = data.get('scene_type', '2D')
    logger.info(f"切换场景到: {scene_type}")
    
    return jsonify({
        "status": "success",
        "current_scene": scene_type,
        "message": f"已切换到{scene_type}场景"
    })

@app.route('/api/switch_input_type', methods=['POST'])
def switch_input_type():
    """切换输入类型"""
    data = request.json
    input_type = data.get('input_type', 'explicit')
    logger.info(f"切换输入类型到: {input_type}")
    
    return jsonify({
        "status": "success",
        "current_input_type": input_type,
        "message": f"已切换到{input_type}输入"
    })

@app.route('/api/start_creation', methods=['POST'])
def start_creation():
    """开始创作 - 处理用户配置"""
    try:
        data = request.json
        logger.info("接收到开始创作请求")
        
        # 处理可视化请求
        if controller:
            result = controller.process_visualization_request(data)
            return jsonify(result)
        else:
            return jsonify({
                "status": "error",
                "message": "控制器未正确初始化"
            }), 500
        
    except Exception as e:
        logger.error(f"开始创作处理失败: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            "status": "error",
            "message": f"处理失败: {str(e)}"
        }), 500

@app.route('/api/task_status/<task_id>')
def get_task_status(task_id):
    """获取任务状态"""
    if controller:
        status = controller.get_task_status(task_id)
        return jsonify(status)
    else:
        return jsonify({"status": "error", "message": "控制器未正确初始化"}), 500

@app.route('/api/download_animation/<task_id>')
def download_animation(task_id):
    """下载生成的动画"""
    if controller:
        task_info = controller.get_task_status(task_id)
        if task_info.get('status') == 'completed' and 'video_path' in task_info:
            return send_file(
                task_info['video_path'],
                as_attachment=True,
                download_name=f"taylor_expansion_{task_id}.mp4"
            )
        else:
            return jsonify({"status": "error", "message": "动画未就绪或不存在"}), 404
    else:
        return jsonify({"status": "error", "message": "控制器未正确初始化"}), 500

@app.route('/api/status')
def get_status():
    """获取系统状态"""
    if controller:
        return jsonify({
            "status": "running",
            "current_scene": controller.current_scene,
            "current_input_type": controller.current_input_type,
            "selected_functions": controller.selected_functions,
            "timestamp": datetime.now().isoformat()
        })
    else:
        return jsonify({"status": "error", "message": "控制器未正确初始化"}), 500

@app.route('/api/validate_3d_point', methods=['POST'])
def validate_3d_point():
    """验证三维点是否在参数曲线上"""
    try:
        data = request.get_json()
        point = data.get('point', [])
        parametric = data.get('parametric', {})
        
        if len(point) != 3:
            return jsonify({"valid": False, "message": "点坐标格式错误"})
        
        if parametric.get('mode') != 'curve':
            return jsonify({"valid": False, "message": "仅支持参数曲线验证"})
        
        x_expr = parametric.get('x_expr', '')
        y_expr = parametric.get('y_expr', '')
        z_expr = parametric.get('z_expr', '')
        
        import numpy as np
        
        def create_param_func(expr_str):
            return lambda t: eval(
                expr_str,
                {
                    "t": t, "sin": np.sin, "cos": np.cos, "tan": np.tan,
                    "exp": np.exp, "sqrt": np.sqrt, "log": np.log,
                    "pi": np.pi, "e": np.e
                }
            )
        
        x_func = create_param_func(x_expr)
        y_func = create_param_func(y_expr)
        z_func = create_param_func(z_expr)
        
        t_range_str = parametric.get('t_range', '0,6.28')
        try:
            t_range = [float(t.strip()) for t in t_range_str.split(',')]
        except:
            t_range = [0, 2 * np.pi]
        
        tolerance = 0.1
        t_values = np.linspace(t_range[0], t_range[1], 1000)
        
        for t in t_values:
            try:
                curve_point = [x_func(t), y_func(t), z_func(t)]
                distance = np.sqrt(sum((a - b)**2 for a, b in zip(point, curve_point)))
                
                if distance < tolerance:
                    dt = 0.001
                    tangent = [
                        (x_func(t + dt) - x_func(t - dt)) / (2 * dt),
                        (y_func(t + dt) - y_func(t - dt)) / (2 * dt),
                        (z_func(t + dt) - z_func(t - dt)) / (2 * dt)
                    ]
                    
                    return jsonify({
                        "valid": True,
                        "t_value": float(t),
                        "curve_point": curve_point,
                        "tangent": tangent
                    })
            except:
                continue
        
        return jsonify({"valid": False, "message": "点不在曲线上"})
        
    except Exception as e:
        logger.error(f"验证三维点失败: {str(e)}")
        return jsonify({"valid": False, "message": str(e)})

@app.route('/api/get_curve_point', methods=['POST'])
def get_curve_point():
    """获取参数曲线在指定参数t处的点和切线向量"""
    try:
        data = request.get_json()
        t = data.get('t', 0)
        parametric = data.get('parametric', {})
        
        if parametric.get('mode') != 'curve':
            return jsonify({"error": "仅支持参数曲线"})
        
        x_expr = parametric.get('x_expr', '')
        y_expr = parametric.get('y_expr', '')
        z_expr = parametric.get('z_expr', '')
        
        import numpy as np
        
        def create_param_func(expr_str):
            return lambda t: eval(
                expr_str,
                {
                    "t": t, "sin": np.sin, "cos": np.cos, "tan": np.tan,
                    "exp": np.exp, "sqrt": np.sqrt, "log": np.log,
                    "pi": np.pi, "e": np.e
                }
            )
        
        x_func = create_param_func(x_expr)
        y_func = create_param_func(y_expr)
        z_func = create_param_func(z_expr)
        
        point = [x_func(t), y_func(t), z_func(t)]
        
        dt = 0.001
        tangent = [
            (x_func(t + dt) - x_func(t - dt)) / (2 * dt),
            (y_func(t + dt) - y_func(t - dt)) / (2 * dt),
            (z_func(t + dt) - z_func(t - dt)) / (2 * dt)
        ]
        
        return jsonify({
            "point": point,
            "tangent": tangent
        })
        
    except Exception as e:
        logger.error(f"获取曲线点失败: {str(e)}")
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    logger.info("=" * 50)
    logger.info("启动Manim简化可视化工具...")
    logger.info("=" * 50)
    
    try:
        app.run(debug=True, host='127.0.0.1', port=5000, use_reloader=False)
    except Exception as e:
        logger.error(f"Flask应用启动失败: {e}")
        logger.error(traceback.format_exc())