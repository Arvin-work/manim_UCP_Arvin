from manim import * # type: ignore
import numpy as np
import os
import ast

# 辅助函数：获取浮点数输入
def get_float_input(prompt, default):
    user_input = input(f"{prompt}（默认{default}）：")
    return float(user_input) if user_input.strip() != "" else default

class ThreeDCamera(ThreeDScene):
    def construct(self):
        # 配置摄像机参数
        self.camera.frame_width = 12  # 设置画面宽度
        self.camera.frame_height = 8  # 设置画面高度
        self.camera.focal_distance = 5  # 设置焦距（影响透视效果）
        
        # 获取相关参数
        vertical_viewing_angle = get_float_input("初始垂直视角参数", 75)
        horizontal_rotation_angle = get_float_input("初始水平视角参数", -45)
        distance = get_float_input("初始距离参数", 6)
        scale_factor = get_float_input("初始缩放系数", 1)

        # 运动时相关参数设置
        moving_speed_horizontal = get_float_input("运行时水平运动速度", 0.2)
        moving_distance = get_float_input("运动时距离参数", 6)
        moving_zoom = get_float_input("运动时缩放设置", 1)

        # 设置初始摄像机位置和方向
        self.set_camera_orientation(
            phi = vertical_viewing_angle * DEGREES,    # 垂直视角（0为俯视，90为平视）
            theta = horizontal_rotation_angle * DEGREES, # 水平旋转角度（0到360）
            distance = distance,         # 摄像机距离原点的距离
            zoom = scale_factor              # 缩放系数
        )

        # 创建莫比乌斯带
        mobius = Surface(
            lambda u, v: np.array([
                (1 + v/2 * np.cos(u/2)) * np.cos(u),
                (1 + v/2 * np.cos(u/2)) * np.sin(u),
                v/2 * np.sin(u/2)
            ]),
            u_range=(0, 2*PI),
            v_range=(-0.3, 0.3),
            resolution=(24, 8),
            checkerboard_colors=False
        ).set_color(BLUE).scale(2)

        # 添加坐标系辅助参考
        axes = ThreeDAxes()
        
        # 场景组成
        self.play(Create(axes))
        self.play(Create(mobius))

        self.begin_3dillusion_camera_rotation(rate=moving_speed_horizontal)
        self.move_camera(
            zoom=moving_zoom,
            distance = moving_distance
        )

        self.wait(8)


    current_file = os.path.basename(__file__)
    os.system(f"manim -pqh {current_file} FunctionPlot")