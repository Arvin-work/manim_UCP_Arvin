import os
import sys
import tempfile
import subprocess
import logging
from manim import *
import sympy as sp
import numpy as np
from sympy import symbols, lambdify, sympify

logger = logging.getLogger(__name__)

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
                # 三角函数
                'sin': sp.sin, 'cos': sp.cos, 'tan': sp.tan,
                'sec': sp.sec, 'csc': sp.csc, 'cot': sp.cot,
                # 反三角函数
                'asin': sp.asin, 'acos': sp.acos, 'atan': sp.atan,
                'arcsin': sp.asin, 'arccos': sp.acos, 'arctan': sp.atan,
                'asec': sp.asec, 'acsc': sp.acsc, 'acot': sp.acot,
                # 指数/对数函数
                'exp': sp.exp, 'log': sp.log,
                # 幂函数
                'sqrt': sp.sqrt, 'cbrt': lambda x: x**(sp.Integer(1)/3),
                # 常量
                'pi': sp.pi, 'e': sp.E
            }
            
            expr = sp.sympify(func_str, locals=allowed_locals)
            return expr
        except Exception as e:
            raise ValueError(f"函数解析错误: {str(e)}")
    
    def create_3d_animation(self, func_str, plot_type="auto", x_range=(-5, 5), y_range=(-5, 5), z_range=(-5, 5),
                          camera_phi=45, camera_theta=-45, output_file=None, plane2_str=None, input_type='explicit',
                          parametric1_config=None, parametric2_config=None):
        """创建三维场景绘制动画
        
        Args:
            func_str: 函数表达式 - 平面1
            plot_type: 绘制类型，可以是 "auto", "surface", "curve", "plane"
            x_range, y_range, z_range: 坐标轴范围
            camera_phi: 相机俯仰角（与z轴夹角，单位：度）
            camera_theta: 相机方位角（绕z轴旋转角度，单位：度）
            output_file: 输出文件路径
            plane2_str: 平面2的函数表达式（可选，用于双平面变换）
            input_type: 输入类型 - explicit, implicit, polar, parametric
            parametric1_config: 参数方程模式下平面1的三组参数配置 {x_expr, y_expr, z_expr}
            parametric2_config: 参数方程模式下平面2的三组参数配置 {x_expr, y_expr, z_expr}
        """
        
        if input_type == 'parametric' and parametric1_config and parametric2_config:
            print(f"参数方程曲面变换 - 使用三组参数输入")
            print(f"平面1: x(u,v)={parametric1_config.get('x_expr', '')}, y(u,v)={parametric1_config.get('y_expr', '')}, z(u,v)={parametric1_config.get('z_expr', '')}")
            print(f"平面2: x₂(u,v)={parametric2_config.get('x_expr', '')}, y₂(u,v)={parametric2_config.get('y_expr', '')}, z₂(u,v)={parametric2_config.get('z_expr', '')}")
            print(f"坐标范围 - X: {x_range}, Y: {y_range}, Z: {z_range}")
            print(f"相机参数 - φ: {camera_phi}°, θ: {camera_theta}°")
            return self.create_surface_transform(
                func_str, plane2_str or '',
                x_range, y_range, z_range,
                camera_phi, camera_theta,
                output_file,
                input_type,
                parametric1_config=parametric1_config,
                parametric2_config=parametric2_config
            )
        
        if plane2_str:
            print(f"双平面变换参数 - 平面1: {func_str}, 平面2: {plane2_str}")
            print(f"输入类型: {input_type}")
            print(f"坐标范围 - X: {x_range}, Y: {y_range}, Z: {z_range}")
            print(f"相机参数 - φ: {camera_phi}°, θ: {camera_theta}°")
            return self.create_surface_transform(
                func_str, plane2_str,
                x_range, y_range, z_range,
                camera_phi, camera_theta,
                output_file,
                input_type
            )
        
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
                            u, v, func_lambda(u, v)
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
            
            # 关键：彻底删除整个videos目录，强制Manim重建
            videos_dir = os.path.join(output_dir, "videos")
            if os.path.exists(videos_dir):
                import shutil
                try:
                    shutil.rmtree(videos_dir)
                except:
                    pass
            
            # 三维渲染设置
            config.quality = "medium_quality"
            config.frame_rate = 30
            config.pixel_height = 720
            config.pixel_width = 1280
            config.disable_caching = True
            
            # 渲染场景
            scene = ThreeDPlot()
            scene.render()
            
            # 查找生成的视频文件 - 三级容错机制
            video_files = []
            for root, dirs, files in os.walk(output_dir):
                for file in files:
                    if file.endswith(".mp4"):
                        if "ThreeDPlot" in file:
                            filepath = os.path.join(root, file)
                            mtime = os.path.getmtime(filepath)
                            video_files.append((-mtime, filepath))
            
            if not video_files:
                for root, dirs, files in os.walk(output_dir):
                    for file in files:
                        if file.endswith(".mp4"):
                            filepath = os.path.join(root, file)
                            mtime = os.path.getmtime(filepath)
                            video_files.append((-mtime, filepath))
            
            if video_files:
                video_files.sort()
                generated_video = video_files[0][1]
                
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

    def create_surface_transform(self, plane1_str, plane2_str,
                                 x_range=(-5, 5), y_range=(-5, 5), z_range=(-5, 5),
                                 camera_phi=45, camera_theta=-45,
                                 output_file=None, input_type='explicit', polar1_params=None, polar2_params=None,
                                 parametric1_config=None, parametric2_config=None):
        """创建曲面平滑变换动画 - 从平面1变换到平面2
        
        支持多种输入类型：显函数、隐函数、极坐标、参数方程
        使用 Manim 的 ReplacementTransform 实现平滑变形效果
        
        Args:
            plane1_str: 第一个曲面的函数表达式
            plane2_str: 第二个曲面的函数表达式
            x_range, y_range, z_range: 坐标轴范围
            camera_phi: 相机俯仰角（与z轴夹角，单位：度）
            camera_theta: 相机方位角（绕z轴旋转角度，单位：度）
            output_file: 输出文件路径
            input_type: 输入类型 - explicit, implicit, polar, parametric
            polar1_params: 极坐标模式下平面1的附加参数
            polar2_params: 极坐标模式下平面2的附加参数
            parametric1_config: 参数方程模式下平面1的三组参数配置 {x_expr, y_expr, z_expr}
            parametric2_config: 参数方程模式下平面2的三组参数配置 {x_expr, y_expr, z_expr}
        """
        print(f"曲面变换类型: {input_type}")
        print(f"平面1原始表达式: {plane1_str}")
        print(f"平面2原始表达式: {plane2_str}")
        
        x, y, z, u, v = symbols('x y z u v')
        
        # ==============================================
        # 重要：在嵌套类之前预先处理所有数据！
        # 防止 Python 闭包作用域 self 指向错误
        # ==============================================
        
        # 显函数模式的安全解析：不含z变量（因为 z = f(x,y)）
        def safe_parse_explicit(expr_str, default_func):
            try:
                func = self.parse_function(expr_str)
                if z in func.free_symbols:
                    print(f"警告: 显函数表达式不应含z变量，自动降级为: {default_func}")
                    return self.parse_function(default_func)
                return func
            except Exception as e:
                print(f"解析错误 {e}: 自动降级为: {default_func}")
                return self.parse_function(default_func)
        
        # 通用安全解析：不检查变量（适用于隐函数、极坐标、参数方程）
        def safe_parse_general(expr_str, default_func):
            try:
                return self.parse_function(expr_str)
            except Exception as e:
                print(f"解析错误 {e}: 自动降级为: {default_func}")
                return self.parse_function(default_func)
        
        # 1. 显函数模式数据预处理
        func1_lambda = None
        func2_lambda = None
        if input_type == 'explicit':
            func1 = safe_parse_explicit(plane1_str, 'x**2 + y**2')
            func2 = safe_parse_explicit(plane2_str, 'x**2 - y**2')
            func1_lambda = lambdify((x, y), func1, 'numpy')
            func2_lambda = lambdify((x, y), func2, 'numpy')
            print(f"显函数模式 - 平面1: z = {func1}")
            print(f"显函数模式 - 平面2: z = {func2}")
        
        # 2. 极坐标模式数据预处理 - 真正的旋转曲面参数化
        polar_r1_lambda = None
        polar_r2_lambda = None
        if input_type == 'polar':
            try:
                theta_sym, phi_sym = symbols('theta phi')
                r1_expr = safe_parse_general(plane1_str, '2 + 0.5*cos(theta)')
                r2_expr = safe_parse_general(plane2_str, '3 + sin(theta)')
                
                polar_r1_lambda = lambdify((theta_sym, phi_sym), r1_expr, 'numpy')
                polar_r2_lambda = lambdify((theta_sym, phi_sym), r2_expr, 'numpy')
                print(f"✅ 极坐标模式 - 平面1: r(θ,φ) = {r1_expr}")
                print(f"✅ 极坐标模式 - 平面2: r(θ,φ) = {r2_expr}")
                print("  真正极坐标: 2D极坐标曲线旋转形成3D环面/曲面")
            except Exception as e:
                print(f"极坐标解析错误 {e}，使用默认心形线")
                polar_r1_lambda = lambda theta, phi: 2 + np.cos(theta)
                polar_r2_lambda = lambda theta, phi: 3 + np.sin(theta)
        
        # 3. 参数方程模式数据预处理
        param1_func = None
        param2_func = None
        if input_type == 'parametric':
            try:
                if parametric1_config and parametric2_config:
                    x1_expr = safe_parse_general(parametric1_config.get('x_expr', 'cos(u)*sin(v)'), 'cos(u)*sin(v)')
                    y1_expr = safe_parse_general(parametric1_config.get('y_expr', 'sin(u)*sin(v)'), 'sin(u)*sin(v)')
                    z1_expr = safe_parse_general(parametric1_config.get('z_expr', 'cos(v)'), 'cos(v)')
                    
                    x2_expr = safe_parse_general(parametric2_config.get('x_expr', '2*cos(u)*sin(v)'), '2*cos(u)*sin(v)')
                    y2_expr = safe_parse_general(parametric2_config.get('y_expr', '2*sin(u)*sin(v)'), '2*sin(u)*sin(v)')
                    z2_expr = safe_parse_general(parametric2_config.get('z_expr', '2*cos(v)'), '2*cos(v)')
                    
                    x1_lambda = lambdify((u, v), x1_expr, 'numpy')
                    y1_lambda = lambdify((u, v), y1_expr, 'numpy')
                    z1_lambda = lambdify((u, v), z1_expr, 'numpy')
                    
                    x2_lambda = lambdify((u, v), x2_expr, 'numpy')
                    y2_lambda = lambdify((u, v), y2_expr, 'numpy')
                    z2_lambda = lambdify((u, v), z2_expr, 'numpy')
                    
                    def param1_func_impl(u, v):
                        x_p = x1_lambda(u, v)
                        y_p = y1_lambda(u, v)
                        z_p = z1_lambda(u, v)
                        return x_p, y_p, z_p
                    
                    def param2_func_impl(u, v):
                        x_p = x2_lambda(u, v)
                        y_p = y2_lambda(u, v)
                        z_p = z2_lambda(u, v)
                        return x_p, y_p, z_p
                    
                    param1_func = param1_func_impl
                    param2_func = param2_func_impl
                    print(f"参数方程模式 - 平面1参数化: x(u,v)={x1_expr}, y(u,v)={y1_expr}, z(u,v)={z1_expr}")
                    print(f"参数方程模式 - 平面2参数化: x₂(u,v)={x2_expr}, y₂(u,v)={y2_expr}, z₂(u,v)={z2_expr}")
                else:
                    r1_expr = safe_parse_general(plane1_str, '2')
                    r2_expr = safe_parse_general(plane2_str, '3')
                    r1_lambda = lambdify((u, v), r1_expr, 'numpy')
                    r2_lambda = lambdify((u, v), r2_expr, 'numpy')
                    
                    def param1_func_impl(u, v):
                        r = r1_lambda(u, v)
                        x_p = r * np.sin(v) * np.cos(u)
                        y_p = r * np.sin(v) * np.sin(u)
                        z_p = r * np.cos(v)
                        return x_p, y_p, z_p
                    
                    def param2_func_impl(u, v):
                        r = r2_lambda(u, v)
                        x_p = 1.5 * r * np.sin(v) * np.cos(u)
                        y_p = r * np.sin(v) * np.sin(u)
                        z_p = 0.8 * r * np.cos(v)
                        return x_p, y_p, z_p
                    
                    param1_func = param1_func_impl
                    param2_func = param2_func_impl
                    print(f"参数方程模式 - 平面1参数化: 球面 r={r1_expr}")
                    print(f"参数方程模式 - 平面2参数化: 椭球面 r={r2_expr}")
            except Exception as e:
                print(f"参数方程解析错误 {e}，使用默认值")
                def param1_func_impl(u, v):
                    r = 2
                    x_p = r * np.sin(v) * np.cos(u)
                    y_p = r * np.sin(v) * np.sin(u)
                    z_p = r * np.cos(v)
                    return x_p, y_p, z_p
                
                def param2_func_impl(u, v):
                    r = 3
                    x_p = 1.5 * r * np.sin(v) * np.cos(u)
                    y_p = r * np.sin(v) * np.sin(u)
                    z_p = 0.8 * r * np.cos(v)
                    return x_p, y_p, z_p
                
                param1_func = param1_func_impl
                param2_func = param2_func_impl
        
        # 4. 隐函数模式数据预处理 - 椭球参数化
        implicit_axes1 = None
        implicit_axes2 = None
        implicit_expr1 = None
        implicit_expr2 = None
        
        def extract_ellipsoid_axes(expr_str):
            try:
                expr = safe_parse_general(expr_str, 'x**2+y**2+z**2-9')
                expr_str_clean = expr_str.replace(' ', '').replace('=', '')
                
                import re
                def get_coeff(var, s):
                    match = re.search(rf'(\d*)\*?{var}\*\*2', s)
                    if match:
                        coeff_str = match.group(1)
                        return float(coeff_str) if coeff_str else 1.0
                    if f'{var}**2' in s:
                        return 1.0
                    return 1.0
                
                const_match = re.search(r'-(\d+\.?\d*)', expr_str_clean)
                constant = float(const_match.group(1)) if const_match else 9.0
                
                coeff_x2 = get_coeff('x', expr_str_clean)
                coeff_y2 = get_coeff('y', expr_str_clean)
                coeff_z2 = get_coeff('z', expr_str_clean)
                
                R_sq = constant
                a = float(np.sqrt(R_sq / coeff_x2)) if coeff_x2 != 0 else 3.0
                b = float(np.sqrt(R_sq / coeff_y2)) if coeff_y2 != 0 else 3.0
                c = float(np.sqrt(R_sq / coeff_z2)) if coeff_z2 != 0 else 3.0
                
                return (a, b, c), expr
                
            except Exception as e:
                print(f"半轴提取失败 {e}，使用默认球面")
                return (3.0, 3.0, 3.0), None
        
        if input_type == 'implicit':
            print("=" * 60)
            print("【技术档案】隐函数输入系统 v1.0")
            print("标准格式: A·x² + B·y² + C·z² - R² = 0")
            print("支持类型: 二次型中心对称曲面 (球面、椭球面)")
            print("限制说明: A,B,C > 0，无交叉项，仅闭合拓扑")
            print("=" * 60)
            
            try:
                plane1_clean = plane1_str.replace(' ', '')
                if '=' in plane1_clean:
                    plane1_clean = plane1_clean.split('=')[0]
                plane2_clean = plane2_str.replace(' ', '')
                if '=' in plane2_clean:
                    plane2_clean = plane2_clean.split('=')[0]
                
                implicit_axes1, implicit_expr1 = extract_ellipsoid_axes(plane1_clean)
                implicit_axes2, implicit_expr2 = extract_ellipsoid_axes(plane2_clean)
                
                a1, b1, c1 = implicit_axes1
                a2, b2, c2 = implicit_axes2
                
                print(f"隐函数模式 - 平面1: {implicit_expr1} = 0")
                print(f"  半轴: x={a1:.1f}, y={b1:.1f}, z={c1:.1f}")
                print(f"隐函数模式 - 平面2: {implicit_expr2} = 0")
                print(f"  半轴: x={a2:.1f}, y={b2:.1f}, z={c2:.1f}")
                shape_type1 = "球面" if abs(a1-b1) < 0.01 and abs(b1-c1) < 0.01 else "椭球"
                shape_type2 = "球面" if abs(a2-b2) < 0.01 and abs(b2-c2) < 0.01 else "椭球"
                print(f"  识别形状: 平面1={shape_type1}, 平面2={shape_type2}")
                print("=" * 60)
            except Exception as e:
                print(f"隐函数解析错误 {e}，使用默认球面")
                implicit_axes1 = (3.0, 3.0, 3.0)
                implicit_axes2 = (4.0, 4.0, 4.0)
        
        # 创建动画场景
        class SurfaceTransformScene(ThreeDScene):
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
                
                # 设置相机视角 - 参考配置
                self.set_camera_orientation(
                    phi=camera_phi * DEGREES,
                    theta=camera_theta * DEGREES,
                    distance=50
                )
                
                # 显示坐标系
                self.play(Create(axes), Write(axes_labels))
                self.wait(1)
                
                # 根据输入类型选择变换策略
                if input_type == 'explicit':
                    # 显函数模式: z = f(x, y)
                    # 使用预先处理好的闭包变量 func1_lambda, func2_lambda
                    surface1 = Surface(
                        lambda u, v: axes.c2p(u, v, func1_lambda(u, v)),
                        u_range=[x_range[0], x_range[1]],
                        v_range=[y_range[0], y_range[1]],
                        resolution=(20, 20),
                        checkerboard_colors=None
                    )
                    surface2 = Surface(
                        lambda u, v: axes.c2p(u, v, func2_lambda(u, v)),
                        u_range=[x_range[0], x_range[1]],
                        v_range=[y_range[0], y_range[1]],
                        resolution=(20, 20),
                        checkerboard_colors=None
                    )
                
                elif input_type == 'implicit':
                    print("隐函数模式: 使用椭球参数化")
                    
                    a1, b1, c1 = implicit_axes1
                    a2, b2, c2 = implicit_axes2
                    
                    def surface1_func(u, v):
                        x_p = a1 * np.sin(v) * np.cos(u)
                        y_p = b1 * np.sin(v) * np.sin(u)
                        z_p = c1 * np.cos(v)
                        return axes.c2p(x_p, y_p, z_p)
                    
                    def surface2_func(u, v):
                        x_p = a2 * np.sin(v) * np.cos(u)
                        y_p = b2 * np.sin(v) * np.sin(u)
                        z_p = c2 * np.cos(v)
                        return axes.c2p(x_p, y_p, z_p)
                    
                    surface1 = Surface(
                        surface1_func,
                        u_range=[0, 2 * np.pi],
                        v_range=[0, np.pi],
                        resolution=(20, 20),
                        checkerboard_colors=None
                    )
                    surface2 = Surface(
                        surface2_func,
                        u_range=[0, 2 * np.pi],
                        v_range=[0, np.pi],
                        resolution=(20, 20),
                        checkerboard_colors=None
                    )
                
                elif input_type == 'polar':
                    print("✅ 真正极坐标旋转曲面模式")
                    print("  u = 旋转角 φ (绕z轴旋转)")
                    print("  v = 极角 θ (xy平面内)")
                    print("  数学: r(θ) × 旋转矩阵 → 真正的3D极坐标曲面")
                    
                    def polar1_func(u, v):
                        try:
                            r1_val = polar_r1_lambda(v, u)
                            r1_val = float(r1_val) if np.isscalar(r1_val) else float(r1_val.mean())
                        except:
                            r1_val = 2 + np.cos(v)
                        x_p = r1_val * np.cos(v) * np.cos(u)
                        y_p = r1_val * np.sin(v) * np.cos(u)
                        z_p = r1_val * np.sin(u)
                        return axes.c2p(x_p, y_p, z_p)
                    
                    def polar2_func(u, v):
                        try:
                            r2_val = polar_r2_lambda(v, u)
                            r2_val = float(r2_val) if np.isscalar(r2_val) else float(r2_val.mean())
                        except:
                            r2_val = 3 + np.sin(v)
                        x_p = r2_val * np.cos(v) * np.cos(u)
                        y_p = r2_val * np.sin(v) * np.cos(u)
                        z_p = r2_val * np.sin(u)
                        return axes.c2p(x_p, y_p, z_p)
                    
                    surface1 = Surface(
                        polar1_func,
                        u_range=[-np.pi, np.pi],
                        v_range=[0, 2 * np.pi],
                        resolution=(30, 30),
                        checkerboard_colors=None
                    )
                    surface2 = Surface(
                        polar2_func,
                        u_range=[-np.pi, np.pi],
                        v_range=[0, 2 * np.pi],
                        resolution=(30, 30),
                        checkerboard_colors=None
                    )
                
                else:  # parametric
                    print("参数方程模式: 使用相同 u, v 参数化变换")
                    
                    def param1_surface_func(u, v):
                        x_p, y_p, z_p = param1_func(u, v)
                        return axes.c2p(x_p, y_p, z_p)
                    
                    def param2_surface_func(u, v):
                        x_p, y_p, z_p = param2_func(u, v)
                        return axes.c2p(x_p, y_p, z_p)
                    
                    surface1 = Surface(
                        param1_surface_func,
                        u_range=[0, 2 * np.pi],
                        v_range=[0, np.pi],
                        resolution=(20, 20),
                        checkerboard_colors=None
                    )
                    surface2 = Surface(
                        param2_surface_func,
                        u_range=[0, 2 * np.pi],
                        v_range=[0, np.pi],
                        resolution=(20, 20),
                        checkerboard_colors=None
                    )
                
                # 设置样式
                surface1.set_fill(YELLOW_D, opacity=0.8)
                surface1.set_stroke(WHITE, width=2.5)
                surface2.set_fill(BLUE, opacity=0.8)
                surface2.set_stroke(WHITE, width=2.5)
                
                # 显示第一个曲面
                self.play(Create(surface1), run_time=3)
                self.wait(2)
                
                # 核心: ReplacementTransform 实现平滑变形
                # 参考代码实现方式
                # self.play(ReplacementTransform(surface1, surface2))
                self.play(
                    ReplacementTransform(surface1, surface2),
                    run_time=4
                )
                self.wait(2)
                
                # 旋转相机视角展示变换后的曲面
                self.begin_ambient_camera_rotation(rate=0.2)
                self.wait(4)
                self.stop_ambient_camera_rotation()
                
                # 最终停留
                self.wait(2)
        
        # 渲染动画
        if output_file is None:
            output_dir = tempfile.mkdtemp()
            output_file = os.path.join(output_dir, "surface_transform.mp4")
        
        original_media_dir = config.media_dir
        
        try:
            output_dir = os.path.join(os.getcwd(), "temp_render")
            os.makedirs(output_dir, exist_ok=True)
            config.media_dir = output_dir
            
            # 关键：彻底删除整个videos目录，强制Manim重建
            videos_dir = os.path.join(output_dir, "videos")
            if os.path.exists(videos_dir):
                import shutil
                try:
                    shutil.rmtree(videos_dir)
                except:
                    pass
            
            # 三维渲染设置
            config.quality = "medium_quality"
            config.frame_rate = 30
            config.pixel_height = 720
            config.pixel_width = 1280
            config.disable_caching = True
            
            # 渲染场景
            scene = SurfaceTransformScene()
            scene.render()
            
            # 查找生成的视频文件 - 三级容错机制
            video_files = []
            for root, dirs, files in os.walk(output_dir):
                for file in files:
                    if file.endswith(".mp4"):
                        if "SurfaceTransformScene" in file or "SurfaceTransform" in file:
                            filepath = os.path.join(root, file)
                            mtime = os.path.getmtime(filepath)
                            video_files.append((-mtime, filepath))
            
            if not video_files:
                for root, dirs, files in os.walk(output_dir):
                    for file in files:
                        if file.endswith(".mp4"):
                            filepath = os.path.join(root, file)
                            mtime = os.path.getmtime(filepath)
                            video_files.append((-mtime, filepath))
            
            if video_files:
                video_files.sort()
                generated_video = video_files[0][1]
                
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
            print(f"生成曲面变换动画时出错: {str(e)}")
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
            
            # 关键：彻底删除整个videos目录，强制Manim重建
            videos_dir = os.path.join(output_dir, "videos")
            if os.path.exists(videos_dir):
                import shutil
                try:
                    shutil.rmtree(videos_dir)
                except:
                    pass
            
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
                    if file.endswith(".mp4"):
                        if "ParametricCurveScene" in file or "ParametricCurve" in file:
                            filepath = os.path.join(root, file)
                            mtime = os.path.getmtime(filepath)
                            video_files.append((-mtime, filepath))
            
            if not video_files:
                for root, dirs, files in os.walk(output_dir):
                    for file in files:
                        if file.endswith(".mp4"):
                            filepath = os.path.join(root, file)
                            mtime = os.path.getmtime(filepath)
                            video_files.append((-mtime, filepath))
            
            if video_files:
                video_files.sort()
                generated_video = video_files[0][1]
                
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
            
            # 关键：彻底删除整个videos目录，强制Manim重建
            videos_dir = os.path.join(output_dir, "videos")
            if os.path.exists(videos_dir):
                import shutil
                try:
                    shutil.rmtree(videos_dir)
                except:
                    pass
            
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
                    if file.endswith(".mp4"):
                        if "ParametricSurfaceScene" in file or "ParametricSurface" in file:
                            filepath = os.path.join(root, file)
                            mtime = os.path.getmtime(filepath)
                            video_files.append((-mtime, filepath))
            
            if not video_files:
                for root, dirs, files in os.walk(output_dir):
                    for file in files:
                        if file.endswith(".mp4"):
                            filepath = os.path.join(root, file)
                            mtime = os.path.getmtime(filepath)
                            video_files.append((-mtime, filepath))
            
            if video_files:
                video_files.sort()
                generated_video = video_files[0][1]
                
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
            
            # 关键：彻底删除整个videos目录，强制Manim重建
            videos_dir = os.path.join(output_dir, "videos")
            if os.path.exists(videos_dir):
                import shutil
                try:
                    shutil.rmtree(videos_dir)
                except:
                    pass
            
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
                    if file.endswith(".mp4"):
                        if "ThreeDDifferentiationScene" in file or "Differentiation" in file:
                            filepath = os.path.join(root, file)
                            mtime = os.path.getmtime(filepath)
                            video_files.append((-mtime, filepath))
            
            if not video_files:
                for root, dirs, files in os.walk(output_dir):
                    for file in files:
                        if file.endswith(".mp4"):
                            filepath = os.path.join(root, file)
                            mtime = os.path.getmtime(filepath)
                            video_files.append((-mtime, filepath))
            
            if video_files:
                video_files.sort()
                generated_video = video_files[0][1]
                
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
                                     x_range=(-6, 6), y_range=(-6, 6),
                                     subdivisions=10,
                                     animation_duration=12,
                                     show_progression=True,
                                     camera_phi=56,
                                     camera_theta=-50,
                                     output_file=None):
        """创建三维黎曼积分可视化动画 - Wave of Boxes 风格
        
        参考 Wave_of_boxes_02 实现动态效果：
        1. 一开始展示较大的 box
        2. 逐渐过渡到更高密度、更细长的 box
        3. 平滑的动态更新效果
        4. 基于颜色渐变
        
        Args:
            func_str: 曲面函数表达式 z = f(x, y)
            x_range: x轴范围
            y_range: y轴范围
            subdivisions: 细分等级
            animation_duration: 动画总时长
            show_progression: 是否展示递进过程
            camera_phi: 相机俯仰角
            camera_theta: 相机方位角
            output_file: 输出文件路径
        """
        print(f"三维黎曼积分 (Wave风格) - 函数: {func_str}")
        print(f"坐标范围 - X: {x_range}, Y: {y_range}")
        print(f"动画时长: {animation_duration}秒")
        print(f"相机参数 - φ: {camera_phi}°, θ: {camera_theta}°")
        
        x, y = symbols('x y')
        func = self.parse_function(func_str)
        func_lambda = lambdify((x, y), func, 'numpy')
        
        class RiemannWave3D(ThreeDScene):
            CONFIG = {
                "camera_config": {
                    'background_color': DARK_GRAY,
                }
            }
            
            def construct(self):
                axes = ThreeDAxes(
                    x_range=[x_range[0], x_range[1], 1],
                    y_range=[y_range[0], y_range[1], 1],
                    z_range=[-5, 5, 1],
                )
                
                axes_labels = axes.get_axis_labels(x_label="x", y_label="y", z_label="z")
                
                self.set_camera_orientation(
                    phi=camera_phi * DEGREES, 
                    theta=camera_theta * DEGREES,
                    distance=50
                )
                
                self.play(Create(axes), Write(axes_labels))
                self.wait(0.5)
                
                surface = Surface(
                    lambda u, v: axes.c2p(u, v, func_lambda(u, v)),
                    u_range=x_range,
                    v_range=y_range,
                    resolution=(30, 30),
                    color=GREEN
                )
                surface.set_fill(GREEN, opacity=0.3)
                surface.set_stroke(WHITE, width=0.5)
                
                self.play(Create(surface), run_time=2)
                self.wait(0.5)
                
                self.colors = color_gradient([BLUE, GREEN_D, YELLOW, RED], 100)
                
                box_stages = [
                    {'size': 2.0, 'gap': 0.4},
                    {'size': 1.0, 'gap': 0.2},
                    {'size': 0.5, 'gap': 0.1},
                ]
                
                self.current_stage = 0
                self.transition_progress = 0.0
                self.boxes_group = VGroup()
                
                # 创建第一阶段 boxes
                initial_boxes = self.create_boxes_for_stage(
                    func_lambda, x_range, y_range, axes, box_stages[0]
                )
                
                self.play(Create(initial_boxes), run_time=2)
                
                self.current_boxes = initial_boxes
                
                stage_duration = (animation_duration - 4) / len(box_stages)
                
                for i in range(len(box_stages)):
                    self.wait(stage_duration / 3)
                    
                    if i < len(box_stages) - 1:
                        new_boxes = self.create_boxes_for_stage(
                            func_lambda, x_range, y_range, axes, box_stages[i + 1]
                        )
                        
                        # 阶段平滑过渡 - 彻底解决重叠问题
                        # 问题根源：并行 FadeOut+FadeIn 导致新旧对象在过渡期间同时存在
                        # 优化策略：串行执行 + 间隙窗口
                        # 时间分配:
                        #   40% 时间 - 完全淡出旧 boxes
                        #   10% 时间 - 间隙（屏幕无boxes，仅背景和曲面）
                        #   40% 时间 - 完全淡入新 boxes
                        #   10% 时间 - 稳定显示
                        # 效果：过渡期间任何时刻只有一种尺寸的boxes可见
                        
                        # Step 1: 先完全淡出旧对象
                        self.play(
                            FadeOut(self.current_boxes),
                            run_time=stage_duration * 0.35
                        )
                        
                        # Step 2: 短暂间隙 - 确保旧对象完全消失
                        # 此时屏幕只有曲面和坐标轴，过渡更自然
                        self.wait(stage_duration * 0.05)
                        
                        # Step 3: 再完全淡入新对象
                        self.play(
                            FadeIn(new_boxes),
                            run_time=stage_duration * 0.35
                        )
                        
                        # Step 4: 短暂稳定显示
                        self.wait(stage_duration * 0.25)
                        
                        # 更新当前引用
                        self.current_boxes = new_boxes
                
                self.begin_ambient_camera_rotation(rate=0.2)
                self.wait(4)
                self.stop_ambient_camera_rotation()
                
                self.wait(1)
            
            def create_boxes_for_stage(self, func, x_range, y_range, axes, stage_config):
                """为指定阶段创建 boxes - 优化无重叠版本
                
                实现原理:
                1. 网格对齐算法：每个立方体占据一个 box_size 的单元格
                2. 间隙均匀分布：gap 在立方体四周均匀分配
                3. 实际立方体尺寸 = box_size - gap
                4. 立方体在单元格内居中放置
                5. 确保相邻立方体之间恰好有 gap 的距离
                
                空间分布验证:
                   [cell_start]----[gap/2]----[cube]----[gap/2]----[next_cell_start]
                   两个相邻立方体之间距离 = gap
                   无重叠 = 实际尺寸 + gap = box_size
                
                特别针对高密度阶段（0.5尺寸）：
                - 4个小立方体占据原1个大立方体的空间（四叉树细分）
                - 每个小立方体精确对齐到子网格中心
                """
                box_size = stage_config['size']
                gap = stage_config['gap']
                
                boxes = VGroup()
                
                # 关键：立方体实际尺寸 = 单元格大小 - 间隙
                # 间隙在立方体四周均匀分布，确保相邻立方体间距恰好为 gap
                cube_size = box_size - gap
                
                # 高密度阶段（box_size = 0.5）使用更精确的网格
                # 确保不超出坐标范围
                expansion_factor = 1.0
                if box_size <= 0.5:
                    # 高密度阶段：略微收缩边界，防止边缘立方体越界
                    expansion_factor = 0.99
                
                # 网格计算：从范围起点开始，按 box_size 步进
                # 第一个网格中心点 = x_min + box_size / 2
                x_centers = []
                y_centers = []
                
                x = x_range[0] + box_size / 2
                while x <= x_range[1] - box_size / 2 * expansion_factor:
                    x_centers.append(x)
                    x += box_size
                
                y = y_range[0] + box_size / 2
                while y <= y_range[1] - box_size / 2 * expansion_factor:
                    y_centers.append(y)
                    y += box_size
                
                # 碰撞检测：验证网格分布（数学证明）
                # 理论上：相邻中心距 = box_size
                # 立方体半宽 = cube_size / 2
                # 相邻立方体间距 = box_size - cube_size = gap > 0
                # 因此必然无重叠
                
                for x_center in x_centers:
                    for y_center in y_centers:
                        try:
                            z_val = func(x_center, y_center)
                            z_height = abs(z_val)
                        except:
                            z_height = 0.1
                            z_val = 0.1
                        
                        if abs(z_height) < 0.01:
                            z_height = 0.1
                        
                        color_idx = min(int((z_height + 1) * 20), 99)
                        color = self.colors[color_idx]
                        
                        # 确定 z 方向基准面
                        if z_val >= 0:
                            z_base = 0
                        else:
                            z_base = -z_height
                        
                        # 高密度阶段使用更细的边框，增强视觉区分度
                        stroke_w = 0.2 if box_size <= 0.5 else 0.3
                        
                        # 创建立方体：使用精确的无碰撞尺寸
                        box = Prism(
                            dimensions=[cube_size, cube_size, z_height * 0.98]
                        )
                        
                        box.set_fill(color, opacity=0.85 if box_size <= 0.5 else 0.8)
                        box.set_stroke(WHITE, width=stroke_w)
                        
                        # 精确定位到网格中心
                        # (x_center, y_center) 是单元格的几何中心
                        center = axes.c2p(x_center, y_center, z_base + z_height / 2)
                        box.move_to(center)
                        
                        boxes.add(box)
                
                # 碰撞检测：运行时验证无重叠
                # 数学证明 + 运行时双重保障
                collision_count = self._check_box_collisions(boxes, box_size, gap)
                if collision_count > 0:
                    logger.warning(f"box_size={box_size}: 检测到 {collision_count} 对立方体重叠，正在自动修复")
                    # 自动修复：略微缩小立方体尺寸
                    shrink_factor = 0.95
                    for box in boxes:
                        box.scale(shrink_factor)
                
                return boxes
            
            def _check_box_collisions(self, boxes, box_size, gap):
                """碰撞检测：验证立方体之间无重叠
                
                检测算法：
                1. 对每一对立方体，计算中心距离
                2. 如果 x/y 方向距离 < (cube_size - 1e-6)，则判定为碰撞
                3. 返回碰撞对数
                """
                cube_size = box_size - gap
                collision_count = 0
                n = len(boxes)
                
                for i in range(n):
                    for j in range(i + 1, n):
                        pos_i = boxes[i].get_center()
                        pos_j = boxes[j].get_center()
                        
                        # 计算曼哈顿距离（因为是轴对齐网格）
                        dx = abs(pos_i[0] - pos_j[0])
                        dy = abs(pos_i[1] - pos_j[1])
                        
                        # 允许极小的浮点误差（1e-6）
                        min_safe_distance = cube_size - 1e-6
                        
                        if dx < min_safe_distance and dy < min_safe_distance:
                            collision_count += 1
                
                return collision_count
        
        if output_file is None:
            output_dir = tempfile.mkdtemp()
            output_file = os.path.join(output_dir, "3d_riemann_integration.mp4")
        
        original_media_dir = config.media_dir
        
        try:
            output_dir = os.path.join(os.getcwd(), "temp_render")
            os.makedirs(output_dir, exist_ok=True)
            config.media_dir = output_dir
            
            # 关键：彻底删除整个videos目录，强制Manim重建
            videos_dir = os.path.join(output_dir, "videos")
            if os.path.exists(videos_dir):
                import shutil
                try:
                    shutil.rmtree(videos_dir)
                except:
                    pass
            
            config.quality = "medium_quality"
            config.frame_rate = 30
            config.pixel_height = 720
            config.pixel_width = 1280
            config.disable_caching = True
            
            scene = RiemannWave3D()
            scene.render()
            
            video_files = []
            for root, dirs, files in os.walk(output_dir):
                for file in files:
                    if file.endswith(".mp4") and "RiemannWave3D" in file:
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