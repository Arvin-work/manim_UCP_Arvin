# 创建一个三维坐标系
from manim import *
import numpy as np
import os
import sys


def get_float_input(prompt, default):
    user_input = input(f"{prompt}（默认{default}）：")
    return float(user_input) if user_input.strip() != "" else default


class ThreeD_Example(ThreeDScene):
    def construct(self):
        # create a camera for first()
        self.set_camera_orientation(phi=75*DEGREES, theta=-45*DEGREES)

        # create threeD area
        axes = ThreeDAxes()
        
        # define a function z=x*2 + y*2
        surface = Surface(
            lambda u, v: np.array([u, v, u**2+v**2]),
            u_range=[-2,2],
            v_range=[-2,2],
            resolution=(32, 32),
            fill_opacity=0.7,
            stroke_width=1.5,
            color=BLUE
        )

        # add area and surface
        self.play(Create(axes))
        self.play(Create(surface))

        # make camera revolve
        self.begin_ambient_camera_rotation(rate=0.5)
        self.wait(6)