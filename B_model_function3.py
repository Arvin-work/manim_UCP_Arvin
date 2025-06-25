from manim import *
import numpy as np
import os

# 为极坐标创建相关的实现方式
class PolarGraphExample(Scene):
    def construct(self):
        # 创建极坐标系
        polar_plane = PolarPlane(
            radius_max=4,
            azimuth_step=30,  # 角度步长30度
            radius_step=1,  # 半径步长1
            background_line_style={
                "stroke_color": BLUE_E,
                "stroke_width": 2,
                "stroke_opacity": 0.6
            },
        )
        self.add(polar_plane)

        # 创建极坐标方程对应的曲线（心形线）
        graph = ParametricFunction(
            lambda t: np.array([
                (2 + 2 * np.sin(t)) * np.cos(t),  # x坐标
                (2 + 2 * np.sin(t)) * np.sin(t),  # y坐标
                0
            ]),
            t_range=[0, 2 * PI],  # θ从0到2π
            color=RED,
            stroke_width=3
        )

        # 添加方程文本
        equation = MathTex(r"r = 2 + 2\sin\theta").to_edge(UR)
        equation.add_background_rectangle(opacity=0.8, buff=0.2)

        # 动画展示
        self.play(Create(graph), run_time=3)
        self.play(Write(equation))
        self.wait(2)