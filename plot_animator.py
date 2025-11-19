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
                'sin': sp.sin, 'cos': sp.cos, 'tan': sp.tan,
                'exp': sp.exp, 'log': sp.log, 'sqrt': sp.sqrt,
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
                # 创建NumberPlane作为背景网格 - 使用默认的蓝白色网格
                plane = NumberPlane(
                    x_range=[x_range[0], x_range[1], (x_range[1]-x_range[0])//10],
                    y_range=[y_range[0], y_range[1], (y_range[1]-y_range[0])//10],
                    # 使用默认的蓝白色网格样式
                )
                
                # 函数图像 - 直接使用NumberPlane的坐标系
                func_lambda = lambdify(x, func, 'numpy')
                
                # 使用NumberPlane的plot方法创建函数图像
                func_graph = plane.plot(
                    func_lambda,
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
            
            # 设置视频质量 - 使用与泰勒展开相同的设置
            config.quality = "high_quality"
            config.frame_rate = 60
            config.pixel_height = 1080
            config.pixel_width = 1920
            
            # 启用高质量渲染
            config.disable_caching = False
            
            # 创建并渲染场景
            scene = FunctionPlotScene()
            scene.render()
            
            # 使用与泰勒展开相同的方法查找视频文件
            video_files = []
            
            # 查找所有可能的视频文件路径
            possible_paths = [
                os.path.join(output_dir, "videos", "FunctionPlotScene", "1080p60", "FunctionPlotScene.mp4"),
                os.path.join(output_dir, "FunctionPlotScene.mp4"),
            ]
            
            # 同时搜索整个目录
            for root, dirs, files in os.walk(output_dir):
                for file in files:
                    if file.endswith(".mp4") and "FunctionPlotScene" in file:
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