import os
import sys
import tempfile
import subprocess
from manim import *
import sympy as sp
import numpy as np
from sympy import symbols, lambdify

class IntegrationAnimator:
    """积分展示动画生成器 - 支持正负函数值版本"""
    
    def __init__(self):
        pass
    
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
    
    def create_integration_animation(self, func_str, lower_bound, upper_bound, 
                                   x_range=(-10, 10), y_range=(-10, 10),
                                   output_file=None):
        """创建积分展示动画"""
        
        lower_bound = float(lower_bound)
        upper_bound = float(upper_bound)
        
        print(f"积分展示动画参数 - 函数: {func_str}, 积分区间: [{lower_bound}, {upper_bound}]")
        print(f"坐标范围 - X: {x_range}, Y: {y_range}")

        # 解析函数
        x = symbols('x')
        func = self.parse_function(func_str)
        func_lambda = lambdify(x, func, 'numpy')
        
        # 创建动画场景
        class RiemannIntegration(Scene):
            def construct(self):
                # 步骤1: 创建坐标系和函数图像 - 使用传入的完整y轴范围
                axes = Axes(
                    x_range=[x_range[0], x_range[1], (x_range[1]-x_range[0])//10],
                    y_range=[y_range[0], y_range[1], (y_range[1]-y_range[0])//10],
                    x_length=10,
                    y_length=6,
                    axis_config={"color": WHITE}
                )
                
                # 添加坐标轴标签
                axes_labels = axes.get_axis_labels(x_label="x", y_label="y")
                
                # 函数图像
                graph = axes.plot(
                    func_lambda,
                    x_range=[x_range[0], x_range[1]],
                    color=YELLOW,
                    stroke_width=3
                )
                
                # 显示坐标系和函数
                self.play(Create(axes), Write(axes_labels))
                self.play(Create(graph))
                self.wait(1)
                
                # 标记积分区间
                lower_line = DashedLine(
                    axes.c2p(lower_bound, y_range[0]),
                    axes.c2p(lower_bound, func_lambda(lower_bound)),
                    color=RED
                )
                upper_line = DashedLine(
                    axes.c2p(upper_bound, y_range[0]),
                    axes.c2p(upper_bound, func_lambda(upper_bound)),
                    color=RED
                )
                
                self.play(Create(lower_line), Create(upper_line))
                self.wait(1)
                
                # 步骤2: 创建并显示Δx=0.5的矩形 - 支持正负函数值
                rects_05 = self.create_rectangles(axes, func_lambda, lower_bound, upper_bound, 0.5)
                self.play_rectangles_growth(rects_05, axes)
                self.wait(1)
                
                # 步骤3: 过渡到Δx=0.1的矩形
                rects_01 = self.create_rectangles(axes, func_lambda, lower_bound, upper_bound, 0.1)
                self.play_rectangle_transition(rects_05, rects_01, axes)
                self.wait(1)
                
                # 步骤4: 过渡到Δx=0.01的矩形
                rects_001 = self.create_rectangles(axes, func_lambda, lower_bound, upper_bound, 0.01)
                self.play_rectangle_transition(rects_01, rects_001, axes)
                
                # 最终停留 - 移除面积部分，直接停留在Δx=0.01的矩形
                self.wait(3)
            
            def create_rectangles(self, axes, func, a, b, dx):
                """创建矩形组 - 支持正负函数值"""
                rectangles = []
                x_vals = np.arange(a, b, dx)
                
                for x in x_vals:
                    # 计算矩形应该达到的高度
                    target_height = func(x + dx/2)
                    
                    # 跳过高度为0的矩形
                    if abs(target_height) < 1e-10:
                        continue
                    
                    # 创建矩形 - 初始高度为0
                    rect = Rectangle(
                        width=dx * 0.9,  # 稍微缩小以便看清边界
                        height=0,  # 初始高度为0
                        fill_color=BLUE if target_height > 0 else RED,  # 正值为蓝色，负值为红色
                        fill_opacity=0.7,
                        stroke_color=BLUE if target_height > 0 else RED,
                        stroke_width=1
                    )
                    
                    # 定位矩形 - 底部在x轴上（正值）或顶部在x轴上（负值）
                    if target_height > 0:
                        # 正值矩形：底部在x轴上
                        rect.move_to(
                            axes.c2p(x + dx/2, 0),
                            aligned_edge=DOWN
                        )
                    else:
                        # 负值矩形：顶部在x轴上
                        rect.move_to(
                            axes.c2p(x + dx/2, 0),
                            aligned_edge=UP
                        )
                    
                    # 存储目标高度信息
                    rect.target_height = target_height
                    rectangles.append(rect)
                
                return rectangles
            
            def play_rectangles_growth(self, rectangles, axes):
                """播放矩形从高度0增长到目标高度的动画 - 支持正负函数值"""
                animations = []
                for rect in rectangles:
                    # 创建目标矩形（达到目标高度）
                    target_rect = Rectangle(
                        width=rect.get_width(),
                        height=abs(rect.target_height) * axes.y_axis.unit_size,  # 使用绝对值
                        fill_color=BLUE if rect.target_height > 0 else RED,  # 正值为蓝色，负值为红色
                        fill_opacity=0.7,
                        stroke_color=BLUE if rect.target_height > 0 else RED,
                        stroke_width=1
                    )
                    
                    # 定位目标矩形
                    if rect.target_height > 0:
                        # 正值矩形：底部在x轴上
                        target_rect.move_to(
                            rect.get_center(),
                            aligned_edge=DOWN
                        )
                    else:
                        # 负值矩形：顶部在x轴上
                        target_rect.move_to(
                            rect.get_center(),
                            aligned_edge=UP
                        )
                    
                    animations.append(Transform(rect, target_rect))
                
                self.play(*animations, run_time=2)
            
            def play_rectangle_transition(self, old_rects, new_rects, axes):
                """播放矩形过渡动画"""
                # 先隐藏旧矩形
                self.play(*[FadeOut(rect) for rect in old_rects], run_time=1)
                
                # 显示新矩形并让它们生长
                self.play(*[Create(rect) for rect in new_rects], run_time=1)
                self.play_rectangles_growth(new_rects, axes)
        
        # 渲染动画
        if output_file is None:
            output_dir = tempfile.mkdtemp()
            output_file = os.path.join(output_dir, "integration_demo.mp4")
        
        original_media_dir = config.media_dir
        
        try:
            output_dir = os.path.join(os.getcwd(), "temp_render")
            os.makedirs(output_dir, exist_ok=True)
            config.media_dir = output_dir
            
            # 提高画质设置
            config.quality = "high_quality"
            config.frame_rate = 60
            config.pixel_height = 1080
            config.pixel_width = 1920
            config.disable_caching = True
            
            # 渲染场景
            scene = RiemannIntegration()
            scene.render()
            
            # 查找生成的视频文件
            video_files = []
            for root, dirs, files in os.walk(output_dir):
                for file in files:
                    if file.endswith(".mp4") and "RiemannIntegration" in file:
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
            print(f"生成积分展示动画时出错: {str(e)}")
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
    animator = IntegrationAnimator()
    try:
        # 测试sin(x)函数从-π到π的积分
        result = animator.create_integration_animation("sin(x)", -3.14, 3.14, (-4, 4), (-2, 2), "test_integration.mp4")
        print(f"动画生成成功: {result}")
    except Exception as e:
        print(f"测试失败: {e}")