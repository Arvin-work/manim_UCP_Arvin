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
                'sin': sp.sin, 'cos': sp.cos, 'tan': sp.tan,
                'exp': sp.exp, 'log': sp.log, 'sqrt': sp.sqrt,
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
    
    def simplify_polynomial_display(self, poly):
        """简化多项式显示"""
        poly_str = str(poly)
        # 替换符号表示
        poly_str = poly_str.replace("**", "^")
        poly_str = poly_str.replace("*", "")
        # 简化分数表示
        poly_str = poly_str.replace("1.0*", "")
        poly_str = poly_str.replace("0.0", "0")
        poly_str = poly_str.replace("1.0", "1")
        # 简化常见函数
        poly_str = poly_str.replace("sin", "s")
        poly_str = poly_str.replace("cos", "c")
        poly_str = poly_str.replace("exp", "e")
        
        # 如果太长，截断
        if len(poly_str) > 50:
            poly_str = poly_str[:47] + "..."
            
        return poly_str
    
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
            def simplify_polynomial_display(self, poly):
                """简化多项式显示 - 在内部类中定义"""
                poly_str = str(poly)
                # 替换符号表示
                poly_str = poly_str.replace("**", "^")
                poly_str = poly_str.replace("*", "")
                # 简化分数表示
                poly_str = poly_str.replace("1.0*", "")
                poly_str = poly_str.replace("0.0", "0")
                poly_str = poly_str.replace("1.0", "1")
                # 简化常见函数
                poly_str = poly_str.replace("sin", "s")
                poly_str = poly_str.replace("cos", "c")
                poly_str = poly_str.replace("exp", "e")
                
                # 如果太长，截断
                if len(poly_str) > 50:
                    poly_str = poly_str[:47] + "..."
                    
                return poly_str
            
            def setup(self):
                # 创建简化的坐标轴 - 去除网格线和数字
                self.axes = Axes(
                    x_range=[x_range[0], x_range[1], 1],
                    y_range=[y_range[0], y_range[1], 1],
                    axis_config={
                        "color": anim_config['axes_color'],
                        "stroke_width": 2,
                        "include_numbers": False,  # 不显示数字
                        "include_ticks": False,    # 不显示刻度
                    },
                    x_axis_config={
                        "numbers_to_include": [],
                    },
                    y_axis_config={
                        "numbers_to_include": [],
                    },
                )
                # 不添加坐标
                
                # 原始函数
                original_lambda = lambdify(x, original_func, 'numpy')
                self.original_graph = self.axes.plot(
                    original_lambda,
                    x_range=[x_range[0], x_range[1]],
                    color=anim_config['graph_color'],
                    stroke_width=4
                )
                
                # 泰勒多项式列表
                self.taylor_graphs = []
                for i, term_info in enumerate(taylor_terms):
                    poly_lambda = lambdify(x, term_info['polynomial'], 'numpy')
                    graph = self.axes.plot(
                        poly_lambda,
                        x_range=[x_range[0], x_range[1]],
                        color=anim_config['taylor_colors'][i % len(anim_config['taylor_colors'])],
                        stroke_width=3
                    )
                    self.taylor_graphs.append(graph)
                
                # 展开点标记
                original_value = original_func.subs(x, expansion_point)
                self.expansion_point = Dot(
                    self.axes.coords_to_point(expansion_point, float(original_value)),
                    color=RED,
                    radius=0.08
                )
                
                # 文本标签 - 完全使用Text，不使用Tex
                self.title = Text("泰勒展开演示", font_size=36, color=WHITE).to_edge(UP)
                
                # 函数表达式显示
                func_display = f"函数: f(x) = {func_str}"
                self.function_label = Text(func_display, font_size=20, color=WHITE).next_to(self.title, DOWN)
                
                # 展开点显示
                expansion_display = f"展开点: x = {expansion_point}"
                self.expansion_label = Text(expansion_display, font_size=20, color=WHITE).next_to(self.function_label, DOWN)
                
                # 当前阶数显示
                self.order_text = Text("", font_size=24, color=WHITE).to_edge(DOWN)
                
                # 多项式显示区域
                self.poly_text = Text("", font_size=16, color=WHITE).next_to(self.expansion_label, DOWN)
            
            def construct(self):
                # 添加标题和标签
                self.play(Write(self.title))
                self.play(Write(self.function_label))
                self.play(Write(self.expansion_label))
                self.wait(1)
                
                # 创建坐标轴
                self.play(Create(self.axes), run_time=2)
                self.wait(1)
                
                # 显示原始函数
                self.play(Create(self.original_graph), run_time=2)
                self.add(self.expansion_point)
                self.wait(1)
                
                # 逐步显示泰勒多项式
                for i, (taylor_graph, term_info) in enumerate(zip(self.taylor_graphs, taylor_terms)):
                    # 更新阶数文本
                    order_label = Text(f"当前阶数: {term_info['order']}", font_size=24, color=WHITE).to_edge(DOWN)
                    
                    if i == 0:
                        self.play(Write(self.order_text))
                        self.order_text = order_label
                    else:
                        self.play(Transform(self.order_text, order_label))
                    
                    # 显示当前泰勒多项式 - 使用简化显示
                    if term_info['order'] == 0:
                        poly_display = f"P0(x) = {self.simplify_polynomial_display(term_info['polynomial'])}"
                    else:
                        poly_display = f"P{term_info['order']}(x) = P{term_info['order']-1}(x) + {self.simplify_polynomial_display(term_info['term'])}"
                    
                    poly_label = Text(poly_display, font_size=14, color=WHITE)
                    poly_label.next_to(self.expansion_label, DOWN)
                    
                    if i == 0:
                        self.play(Write(self.poly_text))
                        self.poly_text = poly_label
                    else:
                        self.play(Transform(self.poly_text, poly_label))
                    
                    # 创建并显示泰勒多项式曲线
                    self.play(Create(taylor_graph), run_time=1.5)
                    
                    # 短暂暂停以观察
                    if i < len(self.taylor_graphs) - 1:
                        self.wait(0.5)
                    
                    # 对于低阶多项式，可以更长时间观察
                    if term_info['order'] <= 3:
                        self.wait(0.3)
                
                # 最终展示所有曲线
                self.wait(1)
                
                # 高亮原始函数
                self.play(self.original_graph.animate.set_stroke(width=6), run_time=1)
                self.wait(1)
                
                # 渐出其他曲线，只保留原始函数和最高阶泰勒多项式
                graphs_to_fade = [graph for graph in self.taylor_graphs[:-1]]
                self.play(
                    *[FadeOut(graph) for graph in graphs_to_fade],
                    self.poly_text.animate.set_opacity(0.3),
                    self.order_text.animate.set_opacity(0.3),
                    run_time=1
                )
                
                # 显示最终对比
                final_comparison = Text(
                    f"最高{max_order}阶泰勒多项式与原函数的对比",
                    font_size=20,
                    color=WHITE
                ).to_edge(DOWN)
                
                self.play(Transform(self.order_text, final_comparison))
                self.wait(2)
        
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
            config.quality = "high_quality"  # 使用高质量
            config.frame_rate = 60  # 高帧率
            config.pixel_height = 1080  # 1080p分辨率
            config.pixel_width = 1920
            
            # 启用高质量渲染
            config.disable_caching = False
            
            # 创建并渲染场景
            scene = TaylorExpansionScene()
            scene.render()
            
            # 查找生成的视频文件
            video_files = []
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    if file.endswith(".mp4") and "TaylorExpansionScene" in file:
                        video_files.append(os.path.join(root, file))
            
            if video_files:
                # 使用第一个找到的MP4文件
                generated_video = video_files[0]
                
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