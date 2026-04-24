import os
import sys
import tempfile
import subprocess
from manim import *
import sympy as sp
import numpy as np
from sympy import symbols, lambdify

class ImplicitFunctionAnimator:
    """隐函数绘制动画生成器 - 使用 Manim 原生 ImplicitFunction"""
    
    def __init__(self):
        self.config = {
            'curve_color': YELLOW,
            'point_color': RED,
            'tangent_color': BLUE,
            'axes_color': WHITE
        }
    
    def parse_implicit_function(self, func_str):
        """解析隐函数字符串为 sympy 表达式
        
        隐函数形式: F(x, y) = 0
        例如: x**2 + y**2 - 1 = 0 (圆)
              x**2/4 + y**2 - 1 = 0 (椭圆)
              y - x**2 = 0 (抛物线，可转为显式)
        """
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
                'pi': sp.pi, 'e': sp.E,
                # 变量
                'x': symbols('x'),
                'y': symbols('y')
            }
            
            expr = sp.sympify(func_str, locals=allowed_locals)
            return expr
        except Exception as e:
            raise ValueError(f"隐函数解析错误: {str(e)}")
    
    def create_numpy_function(self, func_str):
        """创建用于 Manim ImplicitFunction 的 numpy 函数
        
        返回一个接受 (x, y) 并返回 F(x, y) 的函数
        """
        try:
            func = lambda x, y: eval(
                func_str,
                {
                    "x": x,
                    "y": y,
                    "sin": np.sin,
                    "cos": np.cos,
                    "tan": np.tan,
                    "exp": np.exp,
                    "sqrt": np.sqrt,
                    "log": np.log,
                    "arctan": np.arctan,
                    "pi": np.pi,
                    "e": np.e
                }
            )
            func(0, 0)
            return func
        except Exception as e:
            raise ValueError(f"函数表达式错误: {str(e)}")
    
    def compute_tangent_at_point(self, func_str, point_x, point_y):
        """计算隐函数在某点的切线
        
        使用隐函数求导: dy/dx = -∂F/∂x / ∂F/∂y
        """
        x, y = symbols('x y')
        func = self.parse_implicit_function(func_str)
        
        dF_dx = sp.diff(func, x)
        dF_dy = sp.diff(func, y)
        
        dF_dx_val = float(dF_dx.subs([(x, point_x), (y, point_y)]))
        dF_dy_val = float(dF_dy.subs([(x, point_x), (y, point_y)]))
        
        if abs(dF_dy_val) < 1e-10:
            return None, None, None, None
        
        slope = -dF_dx_val / dF_dy_val
        
        def tangent_func(x_val):
            return slope * (x_val - point_x) + point_y
        
        return slope, point_x, point_y, tangent_func
    
    def find_point_on_curve(self, func_str, target_x, x_range, y_range):
        """在隐函数曲线上找到最接近目标 x 值的点
        
        使用数值方法搜索曲线上的点
        """
        func = self.create_numpy_function(func_str)
        
        best_y = None
        best_dist = float('inf')
        
        y_vals = np.linspace(y_range[0], y_range[1], 500)
        
        for y_val in y_vals:
            try:
                result = func(target_x, y_val)
                if abs(result) < best_dist:
                    best_dist = abs(result)
                    best_y = y_val
            except:
                continue
        
        if best_y is None or best_dist > 0.5:
            return None, None
        
        return target_x, best_y
    
    def create_implicit_plot(self, func_str, x_range=(-10, 10), y_range=(-10, 10),
                           resolution=200, color_scheme='yellow', stroke_width=4,
                           animation_style='none', output_file=None):
        """创建隐函数图像动画 - 使用 Manim 原生 ImplicitFunction"""
        
        func = self.create_numpy_function(func_str)
        
        color_map = {
            'yellow': YELLOW,
            'blue': BLUE,
            'red': RED,
            'green': GREEN,
            'purple': PURPLE
        }
        curve_color = color_map.get(color_scheme, YELLOW)
        
        class ImplicitPlotScene(Scene):
            def construct(self):
                plane_width = 14 * 0.9
                plane_height = 8 * 0.9
                plane = NumberPlane(
                    x_range=[x_range[0], x_range[1], (x_range[1]-x_range[0])/10],
                    y_range=[y_range[0], y_range[1], (y_range[1]-y_range[0])/10],
                    x_length=plane_width,
                    y_length=plane_height,
                )
                
                self.play(Create(plane), run_time=1)
                self.wait(0.2)
                
                graph = ImplicitFunction(
                    func,
                    x_range=x_range,
                    y_range=y_range,
                    color=curve_color,
                    stroke_width=stroke_width
                )
                
                if animation_style == 'draw':
                    self.play(Create(graph), run_time=2.5)
                elif animation_style == 'fade_in':
                    self.play(FadeIn(graph), run_time=1.5)
                else:
                    self.add(graph)
                    self.wait(0.5)
                
                self.wait(1.5)
        
        if output_file is None:
            output_dir = tempfile.mkdtemp()
            output_file = os.path.join(output_dir, "implicit_plot.mp4")
        
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
            
            config.quality = "high_quality"
            config.frame_rate = 60
            config.pixel_height = 1080
            config.pixel_width = 1920
            config.disable_caching = True
            
            scene = ImplicitPlotScene()
            scene.render()
            
            video_files = []
            for root, dirs, files in os.walk(output_dir):
                for file in files:
                    if file.endswith(".mp4") and "ImplicitPlotScene" in file:
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
            print(f"生成隐函数图像时出错: {str(e)}")
            print(f"错误详情: {error_details}")
            raise
        finally:
            config.media_dir = original_media_dir
    
    def create_implicit_differentiation_animation(self, func_str, fit_point_x, 
                                                 x_range=(-10, 10), y_range=(-10, 10),
                                                 resolution=200, output_file=None):
        """创建隐函数微分展示动画
        
        展示隐函数在某点的切线
        """
        
        point_x, point_y = self.find_point_on_curve(func_str, fit_point_x, x_range, y_range)
        
        if point_x is None:
            raise ValueError(f"无法在曲线上找到 x={fit_point_x} 附近的点")
        
        tangent_result = self.compute_tangent_at_point(func_str, point_x, point_y)
        
        if tangent_result[0] is None:
            raise ValueError("无法计算该点的切线（可能是垂直切线）")
        
        slope, px, py, tangent_func = tangent_result
        func = self.create_numpy_function(func_str)
        
        class ImplicitDifferentiationScene(Scene):
            def construct(self):
                plane_width = 14 * 0.9
                plane_height = 8 * 0.9
                plane = NumberPlane(
                    x_range=[x_range[0], x_range[1], (x_range[1]-x_range[0])/20],
                    y_range=[y_range[0], y_range[1], (y_range[1]-y_range[0])/20],
                    x_length=plane_width,
                    y_length=plane_height,
                )
                
                self.play(Create(plane), run_time=1.5)
                self.wait(0.5)
                
                graph = ImplicitFunction(
                    func,
                    x_range=x_range,
                    y_range=y_range,
                    color=YELLOW,
                    stroke_width=4
                )
                
                self.play(Create(graph), run_time=2)
                
                fit_point_dot = Dot(
                    plane.coords_to_point(point_x, point_y),
                    color=RED,
                    radius=0.1
                )
                self.play(Create(fit_point_dot), run_time=1)
                self.wait(1)
                
                tangent_line = plane.plot(
                    tangent_func,
                    x_range=[x_range[0], x_range[1]],
                    color=BLUE,
                    stroke_width=3
                )
                
                self.play(Create(tangent_line), run_time=1.5)
                self.wait(1)
                
                self.play(
                    tangent_line.animate.set_stroke(width=5),
                    fit_point_dot.animate.set_color(PURE_RED),
                    run_time=1
                )
                
                self.wait(2)
        
        if output_file is None:
            output_dir = tempfile.mkdtemp()
            output_file = os.path.join(output_dir, "implicit_differentiation.mp4")
        
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
            
            config.quality = "high_quality"
            config.frame_rate = 60
            config.pixel_height = 1080
            config.pixel_width = 1920
            config.disable_caching = True
            
            scene = ImplicitDifferentiationScene()
            scene.render()
            
            video_files = []
            for root, dirs, files in os.walk(output_dir):
                for file in files:
                    if file.endswith(".mp4") and "ImplicitDifferentiationScene" in file:
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
            print(f"生成隐函数微分动画时出错: {str(e)}")
            print(f"错误详情: {error_details}")
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

if __name__ == "__main__":
    animator = ImplicitFunctionAnimator()
    try:
        result = animator.create_implicit_plot(
            "x**2 + y**2 - 4", 
            (-3, 3), (-3, 3), 
            resolution=200,
            color_scheme='yellow',
            output_file="test_implicit_circle.mp4"
        )
        print(f"隐函数图像生成成功: {result}")
    except Exception as e:
        print(f"测试失败: {e}")
