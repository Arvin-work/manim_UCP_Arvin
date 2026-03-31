import os
import sys
import tempfile
import subprocess
from manim import *
import numpy as np

class PolarAnimator:
    """极坐标绘制动画生成器"""
    
    def __init__(self):
        self.config = {
            'curve_color': RED,
            'point_color': YELLOW,
            'axes_color': BLUE_E
        }
    
    def create_polar_function(self, func_str):
        """创建极坐标函数 r(theta)
        
        支持的函数: sin, cos, tan, exp, sqrt, log, pi, e
        变量: theta (角度，弧度制)
        """
        try:
            func = lambda theta: eval(
                func_str,
                {
                    "theta": theta,
                    "sin": np.sin,
                    "cos": np.cos,
                    "tan": np.tan,
                    "exp": np.exp,
                    "sqrt": np.sqrt,
                    "log": np.log,
                    "pi": np.pi,
                    "e": np.e
                }
            )
            func(0)
            return func
        except Exception as e:
            raise ValueError(f"极坐标函数解析错误: {str(e)}")
    
    def create_spherical_function(self, r_str, phi_str=None):
        """创建球坐标函数 r(theta, phi)
        
        二维极坐标: r = r(theta)
        三维球坐标: r = r(theta, phi)
        
        theta: 方位角 (xy平面内的角度)
        phi: 俯角 (从z轴向下测量的角度)
        """
        try:
            if phi_str:
                func = lambda theta, phi: eval(
                    r_str,
                    {
                        "theta": theta,
                        "phi": phi,
                        "sin": np.sin,
                        "cos": np.cos,
                        "tan": np.tan,
                        "exp": np.exp,
                        "sqrt": np.sqrt,
                        "log": np.log,
                        "pi": np.pi,
                        "e": np.e
                    }
                )
                func(0, 0)
                return func
            else:
                r_func = lambda theta: eval(
                    r_str,
                    {
                        "theta": theta,
                        "sin": np.sin,
                        "cos": np.cos,
                        "tan": np.tan,
                        "exp": np.exp,
                        "sqrt": np.sqrt,
                        "log": np.log,
                        "pi": np.pi,
                        "e": np.e
                    }
                )
                r_func(0)
                return r_func
        except Exception as e:
            raise ValueError(f"球坐标函数解析错误: {str(e)}")
    
    def create_polar_plot(self, func_str, radius_max=4, azimuth_step=30, 
                         radius_step=1, theta_range=(0, 2*np.pi),
                         color_scheme='red', stroke_width=3,
                         animation_style='draw', output_file=None):
        """创建二维极坐标图像动画
        
        Args:
            func_str: 极坐标方程 r(theta)，例如 '2 + 2*sin(theta)'
            radius_max: 半径最大值
            azimuth_step: 角度步长（度数）
            radius_step: 半径步长
            theta_range: theta的范围，默认 (0, 2*pi)
            color_scheme: 曲线颜色
            stroke_width: 曲线粗细
            animation_style: 动画风格 ('draw', 'fade_in', 'none')
            output_file: 输出文件路径
        """
        
        r_func = self.create_polar_function(func_str)
        
        color_map = {
            'red': RED,
            'blue': BLUE,
            'green': GREEN,
            'yellow': YELLOW,
            'purple': PURPLE
        }
        curve_color = color_map.get(color_scheme, RED)
        
        class PolarPlotScene(Scene):
            def construct(self):
                polar_plane = PolarPlane(
                    radius_max=radius_max,
                    azimuth_step=azimuth_step,
                    radius_step=radius_step,
                    background_line_style={
                        "stroke_color": BLUE_E,
                        "stroke_width": 2,
                        "stroke_opacity": 0.6
                    },
                )
                
                self.play(Create(polar_plane), run_time=1)
                self.wait(0.2)
                
                graph = ParametricFunction(
                    lambda t: np.array([
                        r_func(t) * np.cos(t),
                        r_func(t) * np.sin(t),
                        0
                    ]),
                    t_range=[theta_range[0], theta_range[1]],
                    color=curve_color,
                    stroke_width=stroke_width
                )
                
                if animation_style == 'draw':
                    self.play(Create(graph), run_time=3)
                elif animation_style == 'fade_in':
                    self.play(FadeIn(graph), run_time=1.5)
                else:
                    self.add(graph)
                    self.wait(0.5)
                
                self.wait(1.5)
        
        if output_file is None:
            output_dir = tempfile.mkdtemp()
            output_file = os.path.join(output_dir, "polar_plot.mp4")
        
        original_media_dir = config.media_dir
        
        try:
            output_dir = os.path.join(os.getcwd(), "temp_render")
            os.makedirs(output_dir, exist_ok=True)
            config.media_dir = output_dir
            
            config.quality = "high_quality"
            config.frame_rate = 60
            config.pixel_height = 1080
            config.pixel_width = 1920
            config.disable_caching = False
            
            scene = PolarPlotScene()
            scene.render()
            
            video_files = []
            for root, dirs, files in os.walk(output_dir):
                for file in files:
                    if file.endswith(".mp4") and "PolarPlotScene" in file:
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
            print(f"生成极坐标图像时出错: {str(e)}")
            print(f"错误详情: {error_details}")
            raise
        finally:
            config.media_dir = original_media_dir
    
    def create_spherical_plot(self, r_str, phi_str=None, 
                             theta_range=(0, 2*np.pi), phi_range=(0, np.pi),
                             resolution=50, color_scheme='blue',
                             animation_style='draw', output_file=None):
        """创建三维球坐标图像动画
        
        Args:
            r_str: 球坐标方程 r(theta, phi)
            phi_str: 俯角表达式（可选，用于更复杂的曲面）
            theta_range: 方位角范围
            phi_range: 俯角范围
            resolution: 采样分辨率
            color_scheme: 曲面颜色
            animation_style: 动画风格
            output_file: 输出文件路径
        """
        
        r_func = self.create_spherical_function(r_str, phi_str)
        
        color_map = {
            'red': RED,
            'blue': BLUE,
            'green': GREEN,
            'yellow': YELLOW,
            'purple': PURPLE
        }
        surface_color = color_map.get(color_scheme, BLUE)
        
        class SphericalPlotScene(ThreeDScene):
            def construct(self):
                self.set_camera_orientation(phi=75 * DEGREES, theta=30 * DEGREES)
                
                axes = ThreeAxes(
                    x_range=[-4, 4, 1],
                    y_range=[-4, 4, 1],
                    z_range=[-4, 4, 1],
                )
                
                self.play(Create(axes), run_time=1)
                
                if phi_str:
                    def param_func(u, v):
                        theta = theta_range[0] + u * (theta_range[1] - theta_range[0])
                        phi = phi_range[0] + v * (phi_range[1] - phi_range[0])
                        r = r_func(theta, phi)
                        return np.array([
                            r * np.sin(phi) * np.cos(theta),
                            r * np.sin(phi) * np.sin(theta),
                            r * np.cos(phi)
                        ])
                else:
                    def param_func(u, v):
                        theta = theta_range[0] + u * (theta_range[1] - theta_range[0])
                        phi = phi_range[0] + v * (phi_range[1] - phi_range[0])
                        r = r_func(theta)
                        return np.array([
                            r * np.sin(phi) * np.cos(theta),
                            r * np.sin(phi) * np.sin(theta),
                            r * np.cos(phi)
                        ])
                
                surface = Surface(
                    param_func,
                    u_range=[0, 1],
                    v_range=[0, 1],
                    resolution=(resolution, resolution),
                    fill_color=surface_color,
                    fill_opacity=0.7,
                    stroke_width=0.5,
                    stroke_color=WHITE
                )
                
                if animation_style == 'draw':
                    self.play(Create(surface), run_time=3)
                elif animation_style == 'fade_in':
                    self.play(FadeIn(surface), run_time=1.5)
                else:
                    self.add(surface)
                    self.wait(0.5)
                
                self.begin_ambient_camera_rotation(rate=0.2)
                self.wait(5)
                self.stop_ambient_camera_rotation()
        
        if output_file is None:
            output_dir = tempfile.mkdtemp()
            output_file = os.path.join(output_dir, "spherical_plot.mp4")
        
        original_media_dir = config.media_dir
        
        try:
            output_dir = os.path.join(os.getcwd(), "temp_render")
            os.makedirs(output_dir, exist_ok=True)
            config.media_dir = output_dir
            
            config.quality = "high_quality"
            config.frame_rate = 60
            config.pixel_height = 1080
            config.pixel_width = 1920
            config.disable_caching = False
            
            scene = SphericalPlotScene()
            scene.render()
            
            video_files = []
            for root, dirs, files in os.walk(output_dir):
                for file in files:
                    if file.endswith(".mp4") and "SphericalPlotScene" in file:
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
            print(f"生成球坐标图像时出错: {str(e)}")
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
    animator = PolarAnimator()
    try:
        result = animator.create_polar_plot(
            "2 + 2*sin(theta)",
            radius_max=5,
            output_file="test_polar_heart.mp4"
        )
        print(f"极坐标图像生成成功: {result}")
    except Exception as e:
        print(f"测试失败: {e}")
