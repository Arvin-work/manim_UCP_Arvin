import os
import sys
import tempfile
import subprocess
from manim import *
import sympy as sp
import numpy as np
from sympy import symbols, diff, factorial, lambdify

class TaylorExpansionAnimator:
    """泰勒展开动画生成器"""
    
    def __init__(self):
        self.config = {
            'x_range': [-3, 3],
            'y_range': [-2, 2],
            'axes_color': BLUE,
            'graph_color': YELLOW,
            'taylor_colors': [RED, GREEN, ORANGE, PURPLE, PINK, TEAL, MAROON, GOLD, LIGHT_BROWN, LIGHT_PINK]
        }
    
    def parse_function(self, func_str):
        """解析函数字符串为sympy表达式"""
        try:
            # 安全地评估数学表达式
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
            
            # 使用sympify安全转换
            expr = sp.sympify(func_str, locals=allowed_locals)
            return expr
        except Exception as e:
            raise ValueError(f"函数解析错误: {str(e)}")
    
    def compute_taylor_series(self, func, point, max_order):
        """计算泰勒级数"""
        x = symbols('x')
        taylor_terms = []
        
        for n in range(max_order + 1):
            # 计算n阶导数在展开点的值
            derivative = func
            for _ in range(n):
                derivative = diff(derivative, x)
            
            derivative_at_point = derivative.subs(x, point)
            
            # 构建泰勒项
            term = (derivative_at_point / factorial(n)) * (x - point)**n
            
            # 累加当前多项式
            if n == 0:
                polynomial = term
            else:
                polynomial = taylor_terms[-1]['polynomial'] + term
            
            taylor_terms.append({
                'order': n,
                'term': term,
                'polynomial': polynomial,
                'derivative_value': derivative_at_point
            })
        
        return taylor_terms
    
    def create_taylor_animation(self, func_str, expansion_point, max_order=10, 
                               x_range=(-3, 3), y_range=(-2, 2), output_file=None):
        """创建泰勒展开动画"""
        
        # 解析函数
        x = symbols('x')
        original_func = self.parse_function(func_str)
        
        # 计算泰勒级数
        taylor_terms = self.compute_taylor_series(original_func, expansion_point, max_order)
        
        # 将配置传递给内部类
        anim_config = self.config  # 重命名以避免与Manim的config冲突
        
        # 创建动画场景
        class TaylorExpansionScene(Scene):
            def construct(self):
                # 在construct内部创建所有对象，避免作用域问题
                axes = Axes(
                    x_range=[x_range[0], x_range[1], 1],
                    y_range=[y_range[0], y_range[1], 1],
                    axis_config={
                        "color": anim_config['axes_color'],
                        "stroke_width": 2,
                        "include_numbers": False,
                        "include_ticks": False,
                    },
                )
                
                # 原始函数
                original_lambda = lambdify(x, original_func, 'numpy')
                original_graph = axes.plot(
                    original_lambda,
                    x_range=[x_range[0], x_range[1]],
                    color=anim_config['graph_color'],
                    stroke_width=4
                )
                
                # 创建零线 (y=0)
                zero_line = axes.plot(
                    lambda x: 0,
                    x_range=[x_range[0], x_range[1]],
                    color=WHITE,
                    stroke_width=2,
                    stroke_opacity=0.5
                )
                
                # 泰勒多项式列表
                taylor_graphs = []
                for i, term_info in enumerate(taylor_terms):
                    poly_lambda = lambdify(x, term_info['polynomial'], 'numpy')
                    graph = axes.plot(
                        poly_lambda,
                        x_range=[x_range[0], x_range[1]],
                        color=anim_config['taylor_colors'][i % len(anim_config['taylor_colors'])],
                        stroke_width=3
                    )
                    taylor_graphs.append(graph)
                
                # 展开点标记
                original_value = original_func.subs(x, expansion_point)
                expansion_dot = Dot(
                    axes.coords_to_point(expansion_point, float(original_value)),
                    color=RED,
                    radius=0.08
                )
                
                # 创建坐标轴
                self.play(Create(axes), run_time=2)
                self.wait(0.5)
                
                # 显示零线 (y=0)
                self.play(Create(zero_line), run_time=1)
                self.wait(0.5)
                
                # 显示原始函数
                self.play(Create(original_graph), run_time=2)
                self.add(expansion_dot)
                self.wait(1)
                
                # 从零线开始逐步变换为泰勒多项式
                current_graph = zero_line
                
                # 存储所有显示的曲线
                displayed_graphs = [zero_line.copy()]
                
                for i, (taylor_graph, term_info) in enumerate(zip(taylor_graphs, taylor_terms)):
                    # 创建变换动画，从当前曲线变换为新的泰勒多项式曲线
                    self.play(
                        Transform(current_graph, taylor_graph),
                        run_time=2
                    )
                    
                    # 保存当前显示的曲线
                    displayed_graphs.append(current_graph.copy())
                    
                    # 短暂暂停以观察
                    if i < len(taylor_graphs) - 1:
                        self.wait(0.3)
                    
                    # 对于低阶多项式，可以更长时间观察
                    if term_info['order'] <= 3:
                        self.wait(0.2)
                
                # 最终展示所有曲线
                self.wait(1)
                
                # 高亮原始函数
                self.play(original_graph.animate.set_stroke(width=6), run_time=1)
                self.wait(1)
                
                # 重新显示所有泰勒曲线（包括零线）
                all_taylor_curves = VGroup(*[graph.copy() for graph in displayed_graphs[1:]])  # 不包括零线
                
                # 先隐藏当前显示的曲线
                self.play(FadeOut(current_graph), run_time=0.5)
                
                # 同时显示所有泰勒曲线
                self.play(
                    *[Create(graph) for graph in all_taylor_curves],
                    run_time=2
                )
                
                # 持续显示所有曲线一段时间
                self.wait(2)
                
                # 渐出其他曲线，只保留原始函数和最高阶泰勒多项式
                curves_to_fade = [graph for graph in all_taylor_curves[:-1]]  # 保留最高阶曲线
                
                self.play(
                    *[FadeOut(graph) for graph in curves_to_fade],
                    FadeOut(zero_line),
                    run_time=2
                )
                
                # 最终停留，展示原始函数和最高阶泰勒多项式
                self.wait(3)
        
        # 渲染动画
        if output_file is None:
            output_dir = tempfile.mkdtemp()
            output_file = os.path.join(output_dir, "taylor_expansion.mp4")
        
        # 保存原始配置
        original_media_dir = config.media_dir
        
        try:
            # 设置临时输出目录
            temp_dir = tempfile.mkdtemp()
            config.media_dir = temp_dir
            
            # 设置最高质量
            config.quality = "high_quality"
            config.frame_rate = 60
            config.pixel_height = 1080
            config.pixel_width = 1920
            config.disable_caching = True
            
            scene = TaylorExpansionScene()
            scene.render()
            
            video_files = []
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    if file.endswith(".mp4") and "TaylorExpansionScene" in file:
                        filepath = os.path.join(root, file)
                        mtime = os.path.getmtime(filepath)
                        video_files.append((-mtime, filepath))
            
            if video_files:
                video_files.sort()
                generated_video = video_files[0][1]
                
                # 如果指定了输出文件，则移动文件
                if output_file:
                    os.makedirs(os.path.dirname(output_file), exist_ok=True)
                    import shutil
                    shutil.move(generated_video, output_file)
                    return output_file
                else:
                    return generated_video
            else:
                # 如果没找到，尝试默认路径
                default_path = os.path.join(temp_dir, "videos", "TaylorExpansionScene", "1080p60", "TaylorExpansionScene.mp4")
                if os.path.exists(default_path):
                    if output_file:
                        import shutil
                        shutil.move(default_path, output_file)
                        return output_file
                    else:
                        return default_path
                else:
                    # 尝试其他可能的路径
                    for root, dirs, files in os.walk(temp_dir):
                        for file in files:
                            if file.endswith(".mp4"):
                                found_video = os.path.join(root, file)
                                if output_file:
                                    import shutil
                                    shutil.move(found_video, output_file)
                                    return output_file
                                else:
                                    return found_video
                    raise FileNotFoundError("未找到生成的视频文件")
                
        except Exception as e:
            raise e
        finally:
            # 恢复原始配置
            config.media_dir = original_media_dir
            
            # 清理临时目录
            try:
                import shutil
                shutil.rmtree(temp_dir, ignore_errors=True)
            except:
                pass

    def play_animation(self, video_file):
        """使用系统播放器播放动画"""
        try:
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