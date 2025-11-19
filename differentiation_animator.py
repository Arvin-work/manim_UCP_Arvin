import os
import sys
import tempfile
import subprocess
from manim import *
import sympy as sp
import numpy as np
from sympy import symbols, lambdify, diff

class DifferentiationAnimator:
    """微分展示动画生成器"""
    
    def __init__(self):
        self.config = {
            'graph_color': YELLOW,
            'point_color': RED,
            'secant_color': GREEN,
            'tangent_color': BLUE,
            'axes_color': WHITE
        }
    
    def parse_function(self, func_str):
        """解析函数字符串为sympy表达式"""
        try:
            # 安全地评估数学表达式
            allowed_locals = {
                'sin': sp.sin, 'cos': sp.cos, 'tan': sp.tan,
                'exp': sp.exp, 'log': sp.log, 'sqrt': sp.sqrt,
                'pi': sp.pi, 'e': sp.E
            }
            
            # 使用sympify安全转换
            expr = sp.sympify(func_str, locals=allowed_locals)
            return expr
        except Exception as e:
            raise ValueError(f"函数解析错误: {str(e)}")
    
    def create_differentiation_animation(self, func_str, fit_point, radius, 
                                       x_range=(-10, 10), y_range=(-10, 10),
                                       output_file=None):
        """创建微分展示动画"""
        
        # 解析函数
        x = symbols('x')
        func = self.parse_function(func_str)
        
        # 计算导数
        derivative = diff(func, x)
        derivative_at_point = derivative.subs(x, fit_point)
        
        # 计算函数在拟合点的值
        func_value_at_point = func.subs(x, fit_point)
        
        # 创建动画场景
        class DifferentiationScene(Scene):
            def construct(self):
                # 创建密集网格背景
                plane = NumberPlane(
                    x_range=[x_range[0], x_range[1], (x_range[1]-x_range[0])//20],
                    y_range=[y_range[0], y_range[1], (y_range[1]-y_range[0])//20],
                )
                
                # 函数图像
                func_lambda = lambdify(x, func, 'numpy')
                func_graph = plane.plot(
                    func_lambda,
                    x_range=[x_range[0], x_range[1]],
                    color=self.config['graph_color'],
                    stroke_width=4
                )
                
                # 拟合点
                fit_point_dot = Dot(
                    plane.coords_to_point(fit_point, float(func_value_at_point)),
                    color=self.config['point_color'],
                    radius=0.08
                )
                
                # 步骤1: 显示函数和拟合点
                self.play(Create(plane), run_time=1.5)
                self.wait(0.5)
                self.play(Create(func_graph), run_time=2)
                self.play(Create(fit_point_dot), run_time=1)
                self.wait(1)
                
                # 步骤2: 创建割线的两个点
                x1 = fit_point - radius
                x2 = fit_point + radius
                y1 = func.subs(x, x1)
                y2 = func.subs(x, x2)
                
                point1 = Dot(
                    plane.coords_to_point(float(x1), float(y1)),
                    color=self.config['point_color'],
                    radius=0.06
                )
                
                point2 = Dot(
                    plane.coords_to_point(float(x2), float(y2)),
                    color=self.config['point_color'],
                    radius=0.06
                )
                
                # 割线
                secant_line = Line(
                    plane.coords_to_point(float(x1), float(y1)),
                    plane.coords_to_point(float(x2), float(y2)),
                    color=self.config['secant_color'],
                    stroke_width=3
                )
                
                # 显示割线的两个点和割线
                self.play(Create(point1), Create(point2), run_time=1)
                self.play(Create(secant_line), run_time=1.5)
                self.wait(1)
                
                # 步骤3: 两点逐渐靠近，割线变为切线
                steps = 10
                current_radius = radius
                
                for i in range(steps):
                    # 计算新的半径
                    new_radius = radius * (1 - (i + 1) / steps)
                    
                    # 新的两个点
                    new_x1 = fit_point - new_radius
                    new_x2 = fit_point + new_radius
                    new_y1 = func.subs(x, new_x1)
                    new_y2 = func.subs(x, new_x2)
                    
                    # 创建新的点和割线
                    new_point1 = Dot(
                        plane.coords_to_point(float(new_x1), float(new_y1)),
                        color=self.config['point_color'],
                        radius=0.06
                    )
                    
                    new_point2 = Dot(
                        plane.coords_to_point(float(new_x2), float(new_y2)),
                        color=self.config['point_color'],
                        radius=0.06
                    )
                    
                    new_secant = Line(
                        plane.coords_to_point(float(new_x1), float(new_y1)),
                        plane.coords_to_point(float(new_x2), float(new_y2)),
                        color=self.config['secant_color'],
                        stroke_width=3
                    )
                    
                    # 变换动画
                    self.play(
                        Transform(point1, new_point1),
                        Transform(point2, new_point2),
                        Transform(secant_line, new_secant),
                        run_time=0.5
                    )
                
                # 最终显示切线
                tangent_slope = derivative_at_point
                tangent_intercept = float(func_value_at_point) - tangent_slope * fit_point
                
                # 切线函数
                def tangent_func(x_val):
                    return tangent_slope * x_val + tangent_intercept
                
                tangent_graph = plane.plot(
                    tangent_func,
                    x_range=[fit_point - 2, fit_point + 2],
                    color=self.config['tangent_color'],
                    stroke_width=4
                )
                
                # 移除割线，显示切线
                self.play(FadeOut(secant_line), run_time=0.5)
                self.play(Create(tangent_graph), run_time=1.5)
                
                # 高亮显示切线和拟合点
                self.play(
                    tangent_graph.animate.set_stroke(width=5),
                    fit_point_dot.animate.set_color(PURE_RED),
                    run_time=1
                )
                
                # 最终停留
                self.wait(2)
        
        # 渲染动画
        if output_file is None:
            output_dir = tempfile.mkdtemp()
            output_file = os.path.join(output_dir, "differentiation_demo.mp4")
        
        # 保存原始配置
        original_media_dir = config.media_dir
        
        try:
            # 创建专用的输出目录
            output_dir = os.path.join(os.getcwd(), "temp_render")
            os.makedirs(output_dir, exist_ok=True)
            config.media_dir = output_dir
            
            # 设置视频质量
            config.quality = "high_quality"
            config.frame_rate = 60
            config.pixel_height = 1080
            config.pixel_width = 1920
            config.disable_caching = False
            
            # 创建并渲染场景
            scene = DifferentiationScene()
            scene.render()
            
            # 查找生成的视频文件
            video_files = []
            possible_paths = [
                os.path.join(output_dir, "videos", "DifferentiationScene", "1080p60", "DifferentiationScene.mp4"),
                os.path.join(output_dir, "DifferentiationScene.mp4"),
            ]
            
            # 搜索整个目录
            for root, dirs, files in os.walk(output_dir):
                for file in files:
                    if file.endswith(".mp4") and "DifferentiationScene" in file:
                        video_files.append(os.path.join(root, file))
            
            # 添加可能的路径
            for path in possible_paths:
                if os.path.exists(path) and path not in video_files:
                    video_files.append(path)
            
            if video_files:
                # 使用第一个找到的MP4文件
                generated_video = video_files[0]
                
                # 确保输出目录存在
                if output_file:
                    os.makedirs(os.path.dirname(output_file), exist_ok=True)
                    
                    # 检查源文件是否存在且大小合理
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
            print(f"生成微分展示动画时出错: {str(e)}")
            print(f"错误详情: {error_details}")
            raise
        finally:
            # 恢复原始配置
            config.media_dir = original_media_dir

    def play_animation(self, video_file):
        """使用系统播放器播放动画"""
        try:
            # 确保文件存在
            if not os.path.exists(video_file):
                raise FileNotFoundError(f"视频文件不存在: {video_file}")
                
            if sys.platform == "win32":
                os.startfile(video_file)
            elif sys.platform == "darwin":  # macOS
                subprocess.run(["open", video_file])
            else:  # Linux
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
    print("DifferentiationAnimator 类已定义")