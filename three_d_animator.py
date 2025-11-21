import os
import sys
import tempfile
import subprocess
from manim import *
import sympy as sp
import numpy as np
from sympy import symbols, lambdify

class ThreeDAnimator:
    """三维场景绘制动画生成器"""
    
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
    
    def create_3d_animation(self, func_str, x_range=(-5, 5), y_range=(-5, 5), z_range=(-5, 5),
                          output_file=None):
        """创建三维场景绘制动画"""
        
        print(f"三维场景绘制参数 - 函数: {func_str}")
        print(f"坐标范围 - X: {x_range}, Y: {y_range}, Z: {z_range}")

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
                
                # 根据函数类型创建不同的三维对象
                if "z" in str(func):
                    # 如果函数包含z，可能是平面方程
                    surface = self.create_surface(axes, func, x_range, y_range, z_range)
                    self.play(Create(axes), Write(axes_labels))
                    self.play(Create(surface), run_time=3)
                else:
                    # 否则可能是参数曲线
                    curve = self.create_curve(axes, func, x_range)
                    self.play(Create(axes), Write(axes_labels))
                    self.play(Create(curve), run_time=3)
                
                # 旋转相机视角展示三维效果
                self.begin_ambient_camera_rotation(rate=0.2)
                self.wait(4)
                self.stop_ambient_camera_rotation()
                
                # 最终停留
                self.wait(2)
            
            def create_surface(self, axes, func, x_range, y_range, z_range):
                """创建三维曲面"""
                # 将函数转换为数值函数
                x_sym, y_sym, z_sym = symbols('x y z')
                func_lambda = lambdify((x_sym, y_sym), func, 'numpy')
                
                # 创建曲面
                surface = Surface(
                    lambda u, v: axes.c2p(
                        u, v, func_lambda(u, v)
                    ),
                    u_range=[x_range[0], x_range[1]],
                    v_range=[y_range[0], y_range[1]],
                    resolution=(30, 30),
                    color=BLUE,
                    opacity=0.8
                )
                
                return surface
            
            def create_curve(self, axes, func, x_range):
                """创建三维曲线"""
                # 将函数转换为数值函数
                x_sym = symbols('x')
                func_lambda = lambdify(x_sym, func, 'numpy')
                
                # 创建参数曲线 (x, f(x), 0) 或类似形式
                curve = ParametricFunction(
                    lambda t: axes.c2p(
                        t, func_lambda(t), 0  # 在xy平面上
                    ),
                    t_range=[x_range[0], x_range[1]],
                    color=RED,
                    stroke_width=4
                )
                
                return curve
        
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
            config.quality = "high_quality"
            config.frame_rate = 60
            config.pixel_height = 1080
            config.pixel_width = 1920
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

# 测试代码
if __name__ == "__main__":
    animator = ThreeDAnimator()
    try:
        # 测试平面 z = x + y
        result = animator.create_3d_animation("x + y", (-3, 3), (-3, 3), (-3, 3), "test_3d_plane.mp4")
        print(f"三维平面动画生成成功: {result}")
        
        # 测试曲线 y = x^2 (在三维空间中)
        result2 = animator.create_3d_animation("x**2", (-2, 2), (-2, 2), (-2, 2), "test_3d_curve.mp4")
        print(f"三维曲线动画生成成功: {result2}")
    except Exception as e:
        print(f"测试失败: {e}")