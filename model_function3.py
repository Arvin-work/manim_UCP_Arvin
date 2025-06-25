from manim import * # type: ignore
import numpy as np
import os
import sys


def get_float_input(prompt, default):
    user_input = input(f"{prompt}（默认{default}）：")
    return float(user_input) if user_input.strip() != "" else default


class PolarGraphExample(Scene):
    def construct(self):
        # 获取极坐标参数
        radius_max = get_float_input("请输入半径最大值", 4)
        azimuth_step = get_float_input("请输入角度步长（度数）", 30)
        radius_step = get_float_input("请输入半径步长", 1)

        # 从环境变量读取极坐标方程
        func_expr = os.getenv("POLAR_FUNC")

        if not func_expr:
            error_text = Text("未输入极坐标方程！", color=RED)
            self.play(Write(error_text))
            self.wait(2)
            return

        try:
            # 定义r(theta)函数
            r_func = lambda theta: eval(
                func_expr,
                {
                    "theta": theta,
                    "sin": np.sin,
                    "cos": np.cos,
                    "exp": np.exp,
                    "sqrt": np.sqrt,
                    "log": np.log
                }
            )
            # 测试函数是否有效
            r_func(0)
        except Exception as e:
            error_text = Text(f"方程解析失败: {str(e)}", color=RED, font_size=24)
            self.play(Write(error_text))
            self.wait(2)
            return

        # 创建极坐标系
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
        self.add(polar_plane)

        # 创建极坐标图形
        graph = ParametricFunction(
            lambda t: np.array([
                r_func(t) * np.cos(t),  # x坐标
                r_func(t) * np.sin(t),  # y坐标
                0
            ]),
            t_range=[0, 2 * PI], # type: ignore
            color=RED,
            stroke_width=3
        )

        # 动画展示
        self.play(Create(graph), run_time=3)
        self.wait(2)


if __name__ == "__main__":
    # 获取用户输入的极坐标方程
    user_input = input("请输入极坐标方程（使用theta变量，例如'2 + 2*sin(theta)'）: ").strip()

    if not user_input:
        print("错误：未输入方程！")
        sys.exit(1)

    # 验证方程合法性
    try:
        test_func = lambda theta: eval(
            user_input,
            {
                "theta": theta,
                "sin": np.sin,
                "cos": np.cos,
                "exp": np.exp,
                "sqrt": np.sqrt,
                "log": np.log
            }
        )
        test_func(0)  # 测试theta=0时的值
    except Exception as e:
        print(f"方程错误: {str(e)}")
        sys.exit(1)

    # 存入环境变量
    os.environ["POLAR_FUNC"] = user_input

    # 渲染场景
    current_file = os.path.basename(__file__)
    os.system(f"manim -pqh {current_file} PolarGraphExample")