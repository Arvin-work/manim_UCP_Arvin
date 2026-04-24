import os
import sys
import tempfile
import subprocess
from manim import *
import sympy as sp
import numpy as np
from sympy import symbols, lambdify

class FunctionPlotAnimator:
    """显函数绘制动画生成器"""
    
    def __init__(self):
        self.config = {
            'graph_colors': {
                'blue': BLUE,
                'red': RED,
                'green': GREEN,
                'yellow': YELLOW,
                'purple': PURPLE
            }
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
    
    def create_function_plot(self, func_str, x_range=(-10, 10), y_range=(-10, 10), 
                           resolution=100, color_scheme='yellow', stroke_width=4,
                           animation_style='none', output_file=None):
        """创建函数图像动画"""
        
        # 解析函数
        x = symbols('x')
        func = self.parse_function(func_str)
        
        # 将配置传递给内部类
        graph_colors = self.config['graph_colors']
        
        # 创建动画场景
        class FunctionPlotScene(Scene):
            def construct(self):
                # 创建NumberPlane作为背景网格 - 适配场景大小
                # Manim默认场景宽度约14单位，高度约8单位，缩放以适配
                plane_width = 14 * 0.9
                plane_height = 8 * 0.9
                plane = NumberPlane(
                    x_range=[x_range[0], x_range[1], (x_range[1]-x_range[0])//10],
                    y_range=[y_range[0], y_range[1], (y_range[1]-y_range[0])//10],
                    x_length=plane_width,
                    y_length=plane_height,
                )
                
                # 函数图像 - 对y值进行裁剪防止边界外渲染异常
                raw_func = lambdify(x, func, 'numpy')
                y_min, y_max = y_range
                
                # 使用远大于视图范围的阈值进行裁剪，截断线在视野外不可见
                def clamped_func(x_val):
                    result = raw_func(x_val)
                    # 阈值设为视图范围的5倍，截断线完全在视野外
                    clamp_min = y_min * 5 if y_min != 0 else -100
                    clamp_max = y_max * 5 if y_max != 0 else 100
                    return np.clip(result, clamp_min, clamp_max)
                
                # 使用NumberPlane的plot方法创建函数图像
                func_graph = plane.plot(
                    clamped_func,
                    x_range=[x_range[0], x_range[1]],
                    color=graph_colors[color_scheme],
                    stroke_width=stroke_width
                )
                
                # 显示网格背景
                self.play(Create(plane), run_time=1)
                self.wait(0.2)
                
                # 根据动画风格显示函数图像
                if animation_style == 'draw':
                    # 绘制动画
                    self.play(Create(func_graph), run_time=2.5)
                elif animation_style == 'fade_in':
                    # 渐入显示
                    self.play(FadeIn(func_graph), run_time=1.5)
                else:
                    # 无动画，直接显示
                    self.add(func_graph)
                    self.wait(0.5)
                
                # 最终停留
                self.wait(1.5)
        
        # 渲染动画
        if output_file is None:
            output_dir = tempfile.mkdtemp()
            output_file = os.path.join(output_dir, "function_plot.mp4")
        
        # 保存原始配置
        original_media_dir = config.media_dir
        
        try:
            # 创建专用的输出目录，避免使用系统临时目录
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
            
            # 设置视频质量 - 使用与泰勒展开相同的设置
            config.quality = "high_quality"
            config.frame_rate = 60
            config.pixel_height = 1080
            config.pixel_width = 1920
            
            config.disable_caching = True
            
            scene = FunctionPlotScene()
            scene.render()
            
            video_files = []
            for root, dirs, files in os.walk(output_dir):
                for file in files:
                    if file.endswith(".mp4") and "FunctionPlotScene" in file:
                        filepath = os.path.join(root, file)
                        mtime = os.path.getmtime(filepath)
                        video_files.append((-mtime, filepath))
            
            if video_files:
                video_files.sort()
                generated_video = video_files[0][1]
                
                # 确保输出目录存在
                if output_file:
                    os.makedirs(os.path.dirname(output_file), exist_ok=True)
                    
                    # 检查源文件是否存在且大小合理
                    if os.path.exists(generated_video) and os.path.getsize(generated_video) > 1000:
                        # 直接复制文件
                        import shutil
                        shutil.copy2(generated_video, output_file)
                        
                        # 返回最终文件路径
                        if os.path.exists(output_file):
                            return output_file
                        else:
                            raise FileNotFoundError(f"复制后的文件不存在: {output_file}")
                    else:
                        raise FileNotFoundError(f"生成的视频文件无效: {generated_video}")
                else:
                    return generated_video
            else:
                raise FileNotFoundError("未找到生成的视频文件")
                
        except Exception as e:
            # 记录详细的错误信息
            import traceback
            error_details = traceback.format_exc()
            print(f"生成函数图像时出错: {str(e)}")
            print(f"错误详情: {error_details}")
            raise
        finally:
            # 恢复原始配置
            config.media_dir = original_media_dir
            
            # 不立即清理输出目录，避免文件操作冲突
            # 可以在应用关闭时清理，或者定期清理

    def create_2d_parametric_curve(self, x_expr, y_expr, t_range=(0, 2*np.pi),
                                   color_scheme='blue', stroke_width=4,
                                   output_file=None):
        """创建二维参数曲线动画
        
        Args:
            x_expr: x(t) 表达式字符串
            y_expr: y(t) 表达式字符串
            t_range: 参数t的范围
            color_scheme: 曲线颜色
            stroke_width: 曲线宽度
            output_file: 输出文件路径
        """
        print(f"二维参数曲线绘制参数 - x(t)={x_expr}, y(t)={y_expr}")
        print(f"参数范围 - t: {t_range}")
        
        color_map = {
            'red': RED, 'blue': BLUE, 'green': GREEN,
            'yellow': YELLOW, 'purple': PURPLE
        }
        curve_color = color_map.get(color_scheme, BLUE)
        
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
        
        try:
            x_func(0)
            y_func(0)
        except Exception as e:
            raise ValueError(f"参数方程解析错误: {str(e)}")
        
        class ParametricCurve2DScene(Scene):
            def construct(self):
                plane_width = 14 * 0.9
                plane_height = 8 * 0.9
                plane = NumberPlane(
                    x_range=[-5, 5, 1],
                    y_range=[-5, 5, 1],
                    x_length=plane_width,
                    y_length=plane_height,
                )
                
                self.play(Create(plane), run_time=1)
                self.wait(0.2)
                
                curve = ParametricFunction(
                    lambda t: np.array([
                        x_func(t), y_func(t), 0
                    ]),
                    t_range=t_range,
                    color=curve_color,
                    stroke_width=stroke_width
                )
                
                self.play(Create(curve), run_time=3)
                self.wait(1.5)
        
        if output_file is None:
            output_dir = tempfile.mkdtemp()
            output_file = os.path.join(output_dir, "parametric_curve_2d.mp4")
        
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
            
            scene = ParametricCurve2DScene()
            scene.render()
            
            video_files = []
            for root, dirs, files in os.walk(output_dir):
                for file in files:
                    if file.endswith(".mp4"):
                        if "ParametricCurve2DScene" in file or "ParametricCurveScene" in file:
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
            print(f"生成二维参数曲线动画时出错: {str(e)}")
            print(traceback.format_exc())
            raise
        finally:
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

# 添加这个条件，防止直接运行此文件时执行不必要的代码
if __name__ == "__main__":
    # 这里可以添加一些测试代码
    print("FunctionPlotAnimator 类已定义")