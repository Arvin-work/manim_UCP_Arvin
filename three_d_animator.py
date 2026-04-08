import os
import sys
import tempfile
import subprocess
from manim import *
import sympy as sp
import numpy as np
from sympy import symbols, lambdify

class ThreeDAnimator:
    """三维场景绘制动画生成器 - 修复版本"""
    
    def __init__(self):
        self.config = {
            'surface_color': BLUE,
            'line_color': RED,
            'axes_color': WHITE
        }
    
    def parse_function(self, func_str):
        """解析函数字符串为sympy表达式"""
        try:
            allowed_locals = {
                'sin': sp.sin, 'cos': sp.cos, 'tan': sp.tan,
                'exp': sp.exp, 'log': sp.log, 'sqrt': sp.sqrt,
                'pi': sp.pi, 'e': sp.E
            }
            
            expr = sp.sympify(func_str, locals=allowed_locals)
            return expr
        except Exception as e:
            raise ValueError(f"函数解析错误: {str(e)}")
    
    def create_3d_animation(self, func_str, plot_type="auto", x_range=(-5, 5), y_range=(-5, 5), z_range=(-5, 5),
                          camera_phi=45, camera_theta=-45, output_file=None):
        """创建三维场景绘制动画
        
        Args:
            func_str: 函数表达式
            plot_type: 绘制类型，可以是 "auto", "surface", "curve", "plane"
            x_range, y_range, z_range: 坐标轴范围
            camera_phi: 相机俯仰角（与z轴夹角，单位：度）
            camera_theta: 相机方位角（绕z轴旋转角度，单位：度）
            output_file: 输出文件路径
        """
        
        print(f"三维场景绘制参数 - 函数: {func_str}, 绘制类型: {plot_type}")
        print(f"坐标范围 - X: {x_range}, Y: {y_range}, Z: {z_range}")
        print(f"相机参数 - φ: {camera_phi}°, θ: {camera_theta}°")

        # 解析函数
        x, y, z = symbols('x y z')
        func = self.parse_function(func_str)
        
        # 创建动画场景
        class ThreeDPlot(ThreeDScene):
            def construct(self):
                # 创建三维坐标系
                axes = ThreeDAxes(
                    x_range=[x_range[0], x_range[1], 1],
                    y_range=[y_range[0], y_range[1], 1],
                    z_range=[z_range[0], z_range[1], 1],
                )
                
                # 添加坐标轴标签
                axes_labels = axes.get_axis_labels(
                    x_label="x", y_label="y", z_label="z"
                )
                
                self.set_camera_orientation(phi=camera_phi * DEGREES, theta=camera_theta * DEGREES)
                
                # 显示坐标系
                self.play(Create(axes), Write(axes_labels))
                self.wait(1)
                
                # 根据绘制类型创建三维对象
                if plot_type == "surface" or (plot_type == "auto" and self._is_surface_function(func)):
                    # 创建曲面
                    surface = self.create_surface(axes, func, x_range, y_range)
                    self.play(Create(surface), run_time=3)
                    obj = surface
                elif plot_type == "curve" or (plot_type == "auto" and self._is_curve_function(func)):
                    # 创建曲线
                    curve = self.create_curve(axes, func, x_range)
                    self.play(Create(curve), run_time=3)
                    obj = curve
                elif plot_type == "plane":
                    # 创建平面
                    plane = self.create_plane(axes, func, x_range, y_range)
                    self.play(Create(plane), run_time=3)
                    obj = plane
                else:
                    # 默认创建曲面
                    surface = self.create_surface(axes, func, x_range, y_range)
                    self.play(Create(surface), run_time=3)
                    obj = surface
                
                # 旋转相机视角展示三维效果
                self.begin_ambient_camera_rotation(rate=0.2)
                self.wait(4)
                self.stop_ambient_camera_rotation()
                
                # 最终停留
                self.wait(2)
            
            def _is_surface_function(self, func):
                """检测是否为曲面函数（包含x和y变量）"""
                func_symbols = func.free_symbols
                symbols_names = {str(s) for s in func_symbols}
                return 'x' in symbols_names and 'y' in symbols_names
            
            def _is_curve_function(self, func):
                """检测是否为曲线函数（只包含x变量）"""
                func_symbols = func.free_symbols
                symbols_names = {str(s) for s in func_symbols}
                return 'x' in symbols_names and 'y' not in symbols_names
            
            def create_surface(self, axes, func, x_range, y_range):
                """创建三维曲面 z = f(x, y)"""
                try:
                    # 将函数转换为数值函数
                    x_sym, y_sym = symbols('x y')
                    func_lambda = lambdify((x_sym, y_sym), func, 'numpy')
                    
                    # 创建曲面 - 使用fill_opacity而不是opacity
                    surface = Surface(
                        lambda u, v: axes.c2p(
                            u, v, float(func_lambda(u, v))
                        ),
                        u_range=[x_range[0], x_range[1]],
                        v_range=[y_range[0], y_range[1]],
                        resolution=(15, 15),  # 降低分辨率以提高性能
                        color=BLUE
                    )
                    surface.set_fill(BLUE, opacity=0.8)  # 使用set_fill设置透明度
                    surface.set_stroke(WHITE, width=0.5)
                    
                    return surface
                except Exception as e:
                    print(f"创建曲面失败: {e}")
                    # 如果曲面创建失败，创建默认平面
                    return self.create_plane(axes, func, x_range, y_range)
            
            def create_curve(self, axes, func, x_range):
                """创建三维曲线 y = f(x), z = 0"""
                try:
                    # 将函数转换为数值函数
                    x_sym = symbols('x')
                    func_lambda = lambdify(x_sym, func, 'numpy')
                    
                    # 创建参数曲线 (x, f(x), 0)
                    curve = ParametricFunction(
                        lambda t: axes.c2p(
                            float(t), float(func_lambda(t)), 0
                        ),
                        t_range=[x_range[0], x_range[1]],
                        color=RED,
                        stroke_width=4
                    )
                    
                    return curve
                except Exception as e:
                    print(f"创建曲线失败: {e}")
                    # 如果曲线创建失败，创建默认平面
                    return self.create_plane(axes, func, x_range, y_range)
            
            def create_plane(self, axes, func, x_range, y_range):
                """创建平面"""
                try:
                    # 尝试解析常数平面
                    z_value = float(func)
                    plane = Square(
                        side_length=min(x_range[1]-x_range[0], y_range[1]-y_range[0]) * 0.8,
                        color=GREEN,
                        fill_opacity=0.5,
                        stroke_width=2
                    )
                    plane.move_to(axes.c2p(0, 0, z_value))
                    return plane
                except:
                    # 如果无法解析为常数，创建默认平面 z = 0
                    plane = Square(
                        side_length=min(x_range[1]-x_range[0], y_range[1]-y_range[0]) * 0.8,
                        color=GREEN,
                        fill_opacity=0.5,
                        stroke_width=2
                    )
                    plane.move_to(axes.c2p(0, 0, 0))
                    return plane
        
        # 渲染动画
        if output_file is None:
            output_dir = tempfile.mkdtemp()
            output_file = os.path.join(output_dir, "3d_demo.mp4")
        
        original_media_dir = config.media_dir
        
        try:
            output_dir = os.path.join(os.getcwd(), "temp_render")
            os.makedirs(output_dir, exist_ok=True)
            config.media_dir = output_dir
            
            # 三维渲染设置
            config.quality = "medium_quality"
            config.frame_rate = 30
            config.pixel_height = 720
            config.pixel_width = 1280
            config.disable_caching = True
            
            # 渲染场景
            scene = ThreeDPlot()
            scene.render()
            
            # 查找生成的视频文件
            video_files = []
            for root, dirs, files in os.walk(output_dir):
                for file in files:
                    if file.endswith(".mp4") and "ThreeDPlot" in file:
                        video_files.append(os.path.join(root, file))
            
            if video_files:
                generated_video = video_files[0]
                
                if output_file:
                    os.makedirs(os.path.dirname(output_file), exist_ok=True)
                    
                    if os.path.exists(generated_video) and os.path.getsize(generated_video) > 1000:
                        import shutil
                        shutil.copy2(generated_video, output_file)
                        return output_file
                    else:
                        raise FileNotFoundError(f"生成的视频文件无效: {generated_video}")
                else:
                    return generated_video
            else:
                raise FileNotFoundError("未找到生成的视频文件")
                
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"生成三维场景动画时出错: {str(e)}")
            print(f"错误详情: {error_details}")
            raise
        finally:
            config.media_dir = original_media_dir

    def create_parametric_curve(self, x_expr, y_expr, z_expr, t_range=(0, 2*np.pi), 
                               color_scheme='red', stroke_width=3, 
                               camera_phi=45, camera_theta=-45, output_file=None):
        """创建参数曲线动画
        
        Args:
            x_expr: x(t) 表达式字符串
            y_expr: y(t) 表达式字符串
            z_expr: z(t) 表达式字符串
            t_range: 参数t的范围
            color_scheme: 曲线颜色
            stroke_width: 曲线宽度
            camera_phi: 相机俯仰角（与z轴夹角，单位：度）
            camera_theta: 相机方位角（绕z轴旋转角度，单位：度）
            output_file: 输出文件路径
        """
        print(f"参数曲线绘制参数 - x(t)={x_expr}, y(t)={y_expr}, z(t)={z_expr}")
        print(f"参数范围 - t: {t_range}")
        print(f"相机参数 - φ: {camera_phi}°, θ: {camera_theta}°")
        
        color_map = {
            'red': RED, 'blue': BLUE, 'green': GREEN,
            'yellow': YELLOW, 'purple': PURPLE
        }
        curve_color = color_map.get(color_scheme, RED)
        
        def create_param_func(expr_str):
            """创建参数函数"""
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
        
        try:
            x_func(0)
            y_func(0)
            z_func(0)
        except Exception as e:
            raise ValueError(f"参数方程解析错误: {str(e)}")
        
        class ParametricCurveScene(ThreeDScene):
            def construct(self):
                axes = ThreeDAxes(
                    x_range=[-5, 5, 1],
                    y_range=[-5, 5, 1],
                    z_range=[-5, 5, 1],
                )
                
                axes_labels = axes.get_axis_labels(x_label="x", y_label="y", z_label="z")
                
                self.set_camera_orientation(phi=camera_phi * DEGREES, theta=camera_theta * DEGREES)
                
                self.play(Create(axes), Write(axes_labels))
                self.wait(0.5)
                
                curve = ParametricFunction(
                    lambda t: np.array([
                        x_func(t), y_func(t), z_func(t)
                    ]),
                    t_range=t_range,
                    color=curve_color,
                    stroke_width=stroke_width
                )
                
                self.play(Create(curve), run_time=3)
                
                self.begin_ambient_camera_rotation(rate=0.2)
                self.wait(4)
                self.stop_ambient_camera_rotation()
                
                self.wait(1)
        
        if output_file is None:
            output_dir = tempfile.mkdtemp()
            output_file = os.path.join(output_dir, "parametric_curve.mp4")
        
        original_media_dir = config.media_dir
        
        try:
            output_dir = os.path.join(os.getcwd(), "temp_render")
            os.makedirs(output_dir, exist_ok=True)
            config.media_dir = output_dir
            
            config.quality = "medium_quality"
            config.frame_rate = 30
            config.pixel_height = 720
            config.pixel_width = 1280
            config.disable_caching = True
            
            scene = ParametricCurveScene()
            scene.render()
            
            video_files = []
            for root, dirs, files in os.walk(output_dir):
                for file in files:
                    if file.endswith(".mp4") and "ParametricCurveScene" in file:
                        video_files.append(os.path.join(root, file))
            
            if video_files:
                generated_video = video_files[0]
                
                if output_file:
                    os.makedirs(os.path.dirname(output_file), exist_ok=True)
                    
                    if os.path.exists(generated_video) and os.path.getsize(generated_video) > 1000:
                        import shutil
                        shutil.copy2(generated_video, output_file)
                        return output_file
                
            raise FileNotFoundError("未找到生成的视频文件")
                
        except Exception as e:
            import traceback
            print(f"生成参数曲线动画时出错: {str(e)}")
            print(traceback.format_exc())
            raise
        finally:
            config.media_dir = original_media_dir

    def create_parametric_surface(self, x_expr, y_expr, z_expr, 
                                 u_range=(0, 2*np.pi), v_range=(0, np.pi),
                                 color_scheme='blue', resolution=(30, 30),
                                 camera_phi=45, camera_theta=-45, output_file=None):
        """创建参数曲面动画
        
        Args:
            x_expr: x(u,v) 表达式字符串
            y_expr: y(u,v) 表达式字符串
            z_expr: z(u,v) 表达式字符串
            u_range: 参数u的范围
            v_range: 参数v的范围
            color_scheme: 曲面颜色
            resolution: 曲面分辨率
            camera_phi: 相机俯仰角（与z轴夹角，单位：度）
            camera_theta: 相机方位角（绕z轴旋转角度，单位：度）
            output_file: 输出文件路径
        """
        print(f"参数曲面绘制参数 - x(u,v)={x_expr}, y(u,v)={y_expr}, z(u,v)={z_expr}")
        print(f"参数范围 - u: {u_range}, v: {v_range}")
        print(f"相机参数 - φ: {camera_phi}°, θ: {camera_theta}°")
        
        color_map = {
            'red': RED, 'blue': BLUE, 'green': GREEN,
            'yellow': YELLOW, 'purple': PURPLE
        }
        surface_color = color_map.get(color_scheme, BLUE)
        
        def create_param_func(expr_str):
            """创建参数函数"""
            return lambda u, v: eval(
                expr_str,
                {
                    "u": u, "v": v, "sin": np.sin, "cos": np.cos, "tan": np.tan,
                    "exp": np.exp, "sqrt": np.sqrt, "log": np.log,
                    "pi": np.pi, "e": np.e
                }
            )
        
        x_func = create_param_func(x_expr)
        y_func = create_param_func(y_expr)
        z_func = create_param_func(z_expr)
        
        try:
            x_func(0, 0)
            y_func(0, 0)
            z_func(0, 0)
        except Exception as e:
            raise ValueError(f"参数方程解析错误: {str(e)}")
        
        class ParametricSurfaceScene(ThreeDScene):
            def construct(self):
                axes = ThreeDAxes(
                    x_range=[-5, 5, 1],
                    y_range=[-5, 5, 1],
                    z_range=[-5, 5, 1],
                )
                
                axes_labels = axes.get_axis_labels(x_label="x", y_label="y", z_label="z")
                
                self.set_camera_orientation(phi=camera_phi * DEGREES, theta=camera_theta * DEGREES)
                
                self.play(Create(axes), Write(axes_labels))
                self.wait(0.5)
                
                surface = Surface(
                    lambda u, v: np.array([
                        x_func(u, v), y_func(u, v), z_func(u, v)
                    ]),
                    u_range=u_range,
                    v_range=v_range,
                    resolution=resolution,
                    color=surface_color
                )
                surface.set_fill(surface_color, opacity=0.8)
                surface.set_stroke(WHITE, width=0.5)
                
                self.play(Create(surface), run_time=3)
                
                self.begin_ambient_camera_rotation(rate=0.2)
                self.wait(4)
                self.stop_ambient_camera_rotation()
                
                self.wait(1)
        
        if output_file is None:
            output_dir = tempfile.mkdtemp()
            output_file = os.path.join(output_dir, "parametric_surface.mp4")
        
        original_media_dir = config.media_dir
        
        try:
            output_dir = os.path.join(os.getcwd(), "temp_render")
            os.makedirs(output_dir, exist_ok=True)
            config.media_dir = output_dir
            
            config.quality = "medium_quality"
            config.frame_rate = 30
            config.pixel_height = 720
            config.pixel_width = 1280
            config.disable_caching = True
            
            scene = ParametricSurfaceScene()
            scene.render()
            
            video_files = []
            for root, dirs, files in os.walk(output_dir):
                for file in files:
                    if file.endswith(".mp4") and "ParametricSurfaceScene" in file:
                        video_files.append(os.path.join(root, file))
            
            if video_files:
                generated_video = video_files[0]
                
                if output_file:
                    os.makedirs(os.path.dirname(output_file), exist_ok=True)
                    
                    if os.path.exists(generated_video) and os.path.getsize(generated_video) > 1000:
                        import shutil
                        shutil.copy2(generated_video, output_file)
                        return output_file
                
            raise FileNotFoundError("未找到生成的视频文件")
                
        except Exception as e:
            import traceback
            print(f"生成参数曲面动画时出错: {str(e)}")
            print(traceback.format_exc())
            raise
        finally:
            config.media_dir = original_media_dir

    def create_3d_differentiation_animation(self, x_expr, y_expr, z_expr, 
                                           t_range=(0, 2*np.pi),
                                           animation_duration=5,
                                           tangent_scale=1,
                                           camera_phi=45,
                                           camera_theta=-45,
                                           output_file=None):
        """创建三维微分展示动画
        
        Args:
            x_expr: x(t) 表达式字符串
            y_expr: y(t) 表达式字符串
            z_expr: z(t) 表达式字符串
            t_range: 参数t的范围
            animation_duration: 动画时长(秒)
            tangent_scale: 切线向量长度缩放因子
            camera_phi: 相机俯仰角（与z轴夹角，单位：度）
            camera_theta: 相机方位角（绕z轴旋转角度，单位：度）
            output_file: 输出文件路径
        """
        print(f"三维微分展示参数 - x(t)={x_expr}, y(t)={y_expr}, z(t)={z_expr}")
        print(f"参数范围 - t: {t_range}, 动画时长: {animation_duration}秒")
        print(f"相机参数 - φ: {camera_phi}°, θ: {camera_theta}°")
        
        def create_param_func(expr_str):
            """创建参数函数"""
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
        
        try:
            x_func(0)
            y_func(0)
            z_func(0)
        except Exception as e:
            raise ValueError(f"参数方程解析错误: {str(e)}")
        
        def compute_tangent(t, dt=0.001):
            """计算切线向量"""
            return np.array([
                (x_func(t + dt) - x_func(t - dt)) / (2 * dt),
                (y_func(t + dt) - y_func(t - dt)) / (2 * dt),
                (z_func(t + dt) - z_func(t - dt)) / (2 * dt)
            ])
        
        class ThreeDDifferentiationScene(ThreeDScene):
            def construct(self):
                axes = ThreeDAxes(
                    x_range=[-5, 5, 1],
                    y_range=[-5, 5, 1],
                    z_range=[-5, 5, 1],
                )
                
                axes_labels = axes.get_axis_labels(x_label="x", y_label="y", z_label="z")
                
                self.set_camera_orientation(phi=camera_phi * DEGREES, theta=camera_theta * DEGREES)
                
                self.play(Create(axes), Write(axes_labels))
                self.wait(0.5)
                
                curve = ParametricFunction(
                    lambda t: np.array([
                        x_func(t), y_func(t), z_func(t)
                    ]),
                    t_range=t_range,
                    color=BLUE,
                    stroke_width=4
                )
                
                self.play(Create(curve), run_time=2)
                self.wait(0.5)
                
                t_start, t_end = t_range
                t_mid = (t_start + t_end) / 2
                
                point1_pos = np.array([x_func(t_start), y_func(t_start), z_func(t_start)])
                point2_pos = np.array([x_func(t_end), y_func(t_end), z_func(t_end)])
                
                moving_point1 = Dot3D(point=point1_pos, color=RED, radius=0.1)
                moving_point2 = Dot3D(point=point2_pos, color=GREEN, radius=0.1)
                
                self.play(Create(moving_point1), Create(moving_point2))
                self.wait(0.3)
                
                tangent1 = compute_tangent(t_start)
                tangent1 = tangent1 / np.linalg.norm(tangent1) * tangent_scale
                tangent2 = compute_tangent(t_end)
                tangent2 = tangent2 / np.linalg.norm(tangent2) * tangent_scale
                
                arrow1 = Arrow3D(
                    start=point1_pos,
                    end=point1_pos + tangent1,
                    color=YELLOW,
                    thickness=0.02
                )
                arrow2 = Arrow3D(
                    start=point2_pos,
                    end=point2_pos + tangent2,
                    color=ORANGE,
                    thickness=0.02
                )
                
                self.play(Create(arrow1), Create(arrow2))
                self.wait(0.5)
                
                num_frames = int(animation_duration * 30)
                t_values1 = np.linspace(t_start, t_end, num_frames)
                t_values2 = np.linspace(t_end, t_start, num_frames)
                
                for i in range(num_frames):
                    t1 = t_values1[i]
                    t2 = t_values2[i]
                    
                    new_pos1 = np.array([x_func(t1), y_func(t1), z_func(t1)])
                    new_pos2 = np.array([x_func(t2), y_func(t2), z_func(t2)])
                    
                    new_tangent1 = compute_tangent(t1)
                    new_tangent1 = new_tangent1 / np.linalg.norm(new_tangent1) * tangent_scale
                    new_tangent2 = compute_tangent(t2)
                    new_tangent2 = new_tangent2 / np.linalg.norm(new_tangent2) * tangent_scale
                    
                    new_arrow1 = Arrow3D(
                        start=new_pos1,
                        end=new_pos1 + new_tangent1,
                        color=YELLOW,
                        thickness=0.02
                    )
                    new_arrow2 = Arrow3D(
                        start=new_pos2,
                        end=new_pos2 + new_tangent2,
                        color=ORANGE,
                        thickness=0.02
                    )
                    
                    self.play(
                        moving_point1.animate.move_to(new_pos1),
                        moving_point2.animate.move_to(new_pos2),
                        Transform(arrow1, new_arrow1),
                        Transform(arrow2, new_arrow2),
                        run_time=1/30,
                        rate_func=linear
                    )
                
                self.wait(1)
                
                self.begin_ambient_camera_rotation(rate=0.2)
                self.wait(3)
                self.stop_ambient_camera_rotation()
                
                self.wait(1)
        
        if output_file is None:
            output_dir = tempfile.mkdtemp()
            output_file = os.path.join(output_dir, "3d_differentiation.mp4")
        
        original_media_dir = config.media_dir
        
        try:
            output_dir = os.path.join(os.getcwd(), "temp_render")
            os.makedirs(output_dir, exist_ok=True)
            config.media_dir = output_dir
            
            config.quality = "medium_quality"
            config.frame_rate = 30
            config.pixel_height = 720
            config.pixel_width = 1280
            config.disable_caching = True
            
            scene = ThreeDDifferentiationScene()
            scene.render()
            
            video_files = []
            for root, dirs, files in os.walk(output_dir):
                for file in files:
                    if file.endswith(".mp4") and "ThreeDDifferentiationScene" in file:
                        video_files.append(os.path.join(root, file))
            
            if video_files:
                generated_video = video_files[0]
                
                if output_file:
                    os.makedirs(os.path.dirname(output_file), exist_ok=True)
                    
                    if os.path.exists(generated_video) and os.path.getsize(generated_video) > 1000:
                        import shutil
                        shutil.copy2(generated_video, output_file)
                        return output_file
                
            raise FileNotFoundError("未找到生成的视频文件")
                
        except Exception as e:
            import traceback
            print(f"生成三维微分动画时出错: {str(e)}")
            print(traceback.format_exc())
            raise
        finally:
            config.media_dir = original_media_dir

    def play_animation(self, video_file):
        """使用系统播放器播放动画"""
        try:
            if not os.path.exists(video_file):
                raise FileNotFoundError(f"视频文件不存在: {video_file}")
                
            if sys.platform == "win32":
                os.startfile(video_file)
            elif sys.platform == "darwin":
                subprocess.run(["open", video_file])
            else:
                subprocess.run(["xdg-open", video_file])
            return True
        except Exception as e:
            print(f"播放视频失败: {str(e)}")
            return False

    def cleanup_temp_files(self):
        """清理临时文件"""
        temp_dir = os.path.join(os.getcwd(), "temp_render")
        if os.path.exists(temp_dir):
            import shutil
            try:
                shutil.rmtree(temp_dir, ignore_errors=True)
                print(f"已清理临时目录: {temp_dir}")
            except Exception as e:
                print(f"清理临时目录失败: {e}")

    def create_3d_riemann_integration(self, func_str, 
                                     x_range=(-10, 10), y_range=(-10, 10),
                                     subdivisions=10,
                                     animation_duration=5,
                                     show_progression=True,
                                     camera_phi=45,
                                     camera_theta=-45,
                                     output_file=None):
        """创建三维黎曼积分可视化动画 - 重构版本
        
        基于黎曼积分原理，展示曲面下的体积近似过程：
        1. 在xoy平面上创建均匀网格，以1×1为最小面积单位
        2. 分层立方体生成：
           - 第一层：4×4立方体
           - 第二层：2×2立方体
           - 第三层：1×1立方体
        3. 每个立方体的高度h = f(x_center, y_center)
        4. 展示积分值收敛过程
        
        Args:
            func_str: 曲面函数表达式 z = f(x, y)
            x_range: x轴范围
            y_range: y轴范围
            subdivisions: 初始细分数量（已弃用，保留兼容性）
            animation_duration: 动画时长
            show_progression: 是否展示细分过程
            camera_phi: 相机俯仰角（与z轴夹角，单位：度）
            camera_theta: 相机方位角（绕z轴旋转角度，单位：度）
            output_file: 输出文件路径
        """
        print(f"三维黎曼积分参数 - 函数: {func_str}")
        print(f"坐标范围 - X: {x_range}, Y: {y_range}")
        print(f"动画时长: {animation_duration}秒")
        print(f"相机参数 - φ: {camera_phi}°, θ: {camera_theta}°")
        
        x, y = symbols('x y')
        func = self.parse_function(func_str)
        func_lambda = lambdify((x, y), func, 'numpy')
        
        def compute_exact_integral(func, x_range, y_range):
            """计算精确积分值（使用数值积分）"""
            from scipy import integrate
            
            def integrand(y_val, x_val):
                try:
                    return float(func_lambda(x_val, y_val))
                except:
                    return 0.0
            
            try:
                result, _ = integrate.dblquad(
                    integrand,
                    x_range[0], x_range[1],
                    lambda x: y_range[0],
                    lambda x: y_range[1]
                )
                return result
            except:
                return None
        
        def compute_riemann_volume(func, x_range, y_range, box_size):
            """计算黎曼和体积"""
            total_volume = 0
            
            x_start = int(np.ceil(x_range[0] / box_size)) * box_size
            y_start = int(np.ceil(y_range[0] / box_size)) * box_size
            
            x_current = x_start
            while x_current + box_size/2 < x_range[1]:
                y_current = y_start
                while y_current + box_size/2 < y_range[1]:
                    x_center = x_current + box_size/2
                    y_center = y_current + box_size/2
                    
                    if x_range[0] <= x_center <= x_range[1] and y_range[0] <= y_center <= y_range[1]:
                        try:
                            z_value = func(x_center, y_center)
                            total_volume += z_value * box_size * box_size
                        except:
                            pass
                    
                    y_current += box_size
                x_current += box_size
            
            return total_volume
        
        class RiemannIntegration3D(ThreeDScene):
            def construct(self):
                axes = ThreeDAxes(
                    x_range=[x_range[0], x_range[1], 1],
                    y_range=[y_range[0], y_range[1], 1],
                    z_range=[-5, 5, 1],
                )
                
                axes_labels = axes.get_axis_labels(x_label="x", y_label="y", z_label="z")
                
                self.set_camera_orientation(phi=camera_phi * DEGREES, theta=camera_theta * DEGREES)
                
                self.play(Create(axes), Write(axes_labels))
                self.wait(0.5)
                
                surface = Surface(
                    lambda u, v: np.array([u, v, func_lambda(u, v)]),
                    u_range=x_range,
                    v_range=y_range,
                    resolution=(30, 30),
                    color=GREEN
                )
                surface.set_fill(GREEN, opacity=0.5)
                surface.set_stroke(WHITE, width=0.5)
                
                self.play(Create(surface), run_time=2)
                self.wait(0.5)
                
                z0_plane = Rectangle(
                    width=x_range[1] - x_range[0],
                    height=y_range[1] - y_range[0],
                    color=GRAY,
                    fill_opacity=0.2,
                    stroke_width=1
                )
                z0_plane.rotate(PI/2, axis=RIGHT)
                z0_plane.move_to(axes.c2p(0, 0, 0))
                
                self.play(Create(z0_plane), run_time=1)
                self.wait(0.3)
                
                exact_volume = compute_exact_integral(func_lambda, x_range, y_range)
                
                box_sizes = [4, 2, 1] if show_progression else [1]
                
                previous_boxes = None
                
                for stage_idx, box_size in enumerate(box_sizes):
                    boxes = self.create_riemann_boxes(func_lambda, x_range, y_range, box_size, axes)
                    
                    if not boxes:
                        continue
                    
                    if previous_boxes:
                        self.play(
                            FadeOut(VGroup(*previous_boxes)),
                            run_time=0.5
                        )
                    
                    self.play_boxes_growth(boxes, axes, run_time=animation_duration/len(box_sizes))
                    
                    volume = compute_riemann_volume(func_lambda, x_range, y_range, box_size)
                    
                    if exact_volume is not None:
                        error = abs(volume - exact_volume)
                        error_percent = (error / abs(exact_volume) * 100) if exact_volume != 0 else 0
                        volume_text = Text(
                            f"立方体尺寸: {box_size}×{box_size}\n体积: {volume:.4f}\n精确值: {exact_volume:.4f}\n误差: {error_percent:.2f}%",
                            font_size=20
                        ).to_corner(UL)
                    else:
                        volume_text = Text(
                            f"立方体尺寸: {box_size}×{box_size}\n体积: {volume:.4f}",
                            font_size=20
                        ).to_corner(UL)
                    
                    if stage_idx > 0:
                        self.play(Transform(volume_display, volume_text))
                    else:
                        volume_display = volume_text
                        self.add_fixed_in_frame_mobjects(volume_display)
                        self.play(Write(volume_display))
                    
                    self.wait(0.5)
                    previous_boxes = boxes
                
                self.begin_ambient_camera_rotation(rate=0.3)
                self.wait(3)
                self.stop_ambient_camera_rotation()
                
                self.wait(1)
            
            def create_riemann_boxes(self, func, x_range, y_range, box_size, axes):
                """创建黎曼长方体组 - 按照网格对齐"""
                boxes = []
                
                x_start = int(np.ceil(x_range[0] / box_size)) * box_size
                y_start = int(np.ceil(y_range[0] / box_size)) * box_size
                
                x_current = x_start
                while x_current + box_size/2 < x_range[1]:
                    y_current = y_start
                    while y_current + box_size/2 < y_range[1]:
                        x_center = x_current + box_size/2
                        y_center = y_current + box_size/2
                        
                        if not (x_range[0] <= x_center <= x_range[1] and y_range[0] <= y_center <= y_range[1]):
                            y_current += box_size
                            continue
                        
                        try:
                            z_value = func(x_center, y_center)
                        except:
                            y_current += box_size
                            continue
                        
                        if abs(z_value) < 1e-10:
                            y_current += box_size
                            continue
                        
                        box_width = box_size * 0.95
                        box_depth = box_size * 0.95
                        box_height = abs(z_value)
                        
                        if z_value > 0:
                            box_color = BLUE
                            z_bottom = 0
                        else:
                            box_color = YELLOW
                            z_bottom = z_value
                            box_height = abs(z_value)
                        
                        box = Prism(
                            dimensions=[box_width, box_depth, box_height],
                            fill_color=box_color,
                            fill_opacity=0.8,
                            stroke_color=box_color,
                            stroke_width=0.5
                        )
                        
                        box.move_to(axes.c2p(x_center, y_center, z_bottom + box_height/2))
                        
                        box.target_height = box_height
                        box.z_value = z_value
                        box.x_center = x_center
                        box.y_center = y_center
                        
                        boxes.append(box)
                        
                        y_current += box_size
                    x_current += box_size
                
                return boxes
            
            def play_boxes_growth(self, boxes, axes, run_time=2):
                """播放长方体同步升起动画"""
                flat_boxes = []
                target_boxes = []
                
                for box in boxes:
                    flat_box = Prism(
                        dimensions=[box.width, box.depth, 0.01],
                        fill_color=box.get_fill_color(),
                        fill_opacity=0.8,
                        stroke_color=box.get_stroke_color(),
                        stroke_width=0.5
                    )
                    
                    if box.z_value > 0:
                        flat_box.move_to(axes.c2p(box.x_center, box.y_center, 0.005))
                    else:
                        flat_box.move_to(axes.c2p(box.x_center, box.y_center, box.z_value + 0.005))
                    
                    flat_boxes.append(flat_box)
                    target_boxes.append(box)
                
                self.play(*[Create(fb) for fb in flat_boxes], run_time=run_time*0.3)
                
                animations = []
                for fb, tb in zip(flat_boxes, target_boxes):
                    animations.append(Transform(fb, tb))
                
                self.play(*animations, run_time=run_time*0.7)
                
                for fb, tb in zip(flat_boxes, target_boxes):
                    fb.become(tb)
        
        if output_file is None:
            output_dir = tempfile.mkdtemp()
            output_file = os.path.join(output_dir, "3d_riemann_integration.mp4")
        
        original_media_dir = config.media_dir
        
        try:
            output_dir = os.path.join(os.getcwd(), "temp_render")
            os.makedirs(output_dir, exist_ok=True)
            config.media_dir = output_dir
            
            config.quality = "medium_quality"
            config.frame_rate = 30
            config.pixel_height = 720
            config.pixel_width = 1280
            config.disable_caching = True
            
            scene = RiemannIntegration3D()
            scene.render()
            
            video_files = []
            for root, dirs, files in os.walk(output_dir):
                for file in files:
                    if file.endswith(".mp4") and "RiemannIntegration3D" in file:
                        video_files.append(os.path.join(root, file))
            
            if video_files:
                generated_video = video_files[0]
                
                if output_file:
                    os.makedirs(os.path.dirname(output_file), exist_ok=True)
                    
                    if os.path.exists(generated_video) and os.path.getsize(generated_video) > 1000:
                        import shutil
                        shutil.copy2(generated_video, output_file)
                        return output_file
                
            raise FileNotFoundError("未找到生成的视频文件")
                
        except Exception as e:
            import traceback
            print(f"生成三维黎曼积分动画时出错: {str(e)}")
            print(traceback.format_exc())
            raise
        finally:
            config.media_dir = original_media_dir


# 测试代码
if __name__ == "__main__":
    animator = ThreeDAnimator()
    try:
        # 测试平面 z = x + y
        #result = animator.create_3d_animation("x + y", "surface", (-3, 3), (-3, 3), (-3, 3), "test_3d_plane.mp4")
        #print(f"三维平面动画生成成功: {result}")
        
        # 测试曲线 y = x^2 (在三维空间中)
        result2 = animator.create_3d_animation("x**2", "curve", (-2, 2), (-2, 2), (-2, 2), "test_3d_curve.mp4")
        print(f"三维曲线动画生成成功: {result2}")
    except Exception as e:
        print(f"测试失败: {e}")