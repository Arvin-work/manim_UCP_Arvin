"""对于相关函数进行绘制，并同时对于函数取其斜线来展现微分的意义"""
from manim import *
import numpy as np
import os

def get_float_input(prompt, default):
    user_input = input(f"{prompt}（默认{default}）：")
    return float(user_input) if user_input.strip() != "" else default

class FunctionPlot(Scene):

    def construct(self):
        # 通过类属性获取参数
        axes = Axes(
            x_range=[self.x_left, self.x_right, self.x_step],
            y_range=[self.y_left, self.y_right, self.y_step],
            axis_config={"color": GREY}
        )
        graph = axes.plot(self.func, color=BLUE)
        
        self.play(Create(axes), run_time=2)
        self.play(Create(graph), run_time=3)
        self.wait(2)

        # 动态点和切线
        moving_dot = Dot(color=BLUE_A)
        t = ValueTracker(self.x_left)

        def update_dot(mob):
            x = t.get_value()
            mob.move_to(axes.c2p(x, self.func(x)))

        def update_tangent():
            x = t.get_value()
            return axes.get_secant_slope_group(
                x, graph, dx=0.01,
                secant_line_length=3,
                secant_line_color=YELLOW
            )
        
        moving_dot.add_updater(update_dot)
        tangent_group = always_redraw(update_tangent)

        self.add(moving_dot, tangent_group)
        self.wait(0.5)

        self.play(
            t.animate.set_value(self.x_right),
            run_time=6,
            rate_func=linear
        )
        
        moving_dot.remove_updater(update_dot)
        self.wait(2)

if __name__ == "__main__":
    # 用户输入部分
    global x_left, x_right, x_step, y_left, y_right, y_step, func

    # 类属性存储配置参数
    x_left, x_right, x_step = -10.0, 10.0, 1.0
    y_left, y_right, y_step = -10.0, 10.0, 1.0
    func = lambda x: x**2

    x_left = get_float_input("x轴左侧边界", x_left)
    x_right = get_float_input("x轴右侧边界", x_right)
    x_step = get_float_input("x轴步长", x_step)

    y_left = get_float_input("y轴左侧边界", y_left)
    y_right = get_float_input("y轴右侧边界", y_right)
    y_step = get_float_input("y轴步长", y_step)

    func_input = input("请输入显式函数 y = f(x)（例如 x**2）：").strip() or "x**2"
    try:
        func = lambda x: eval(func_input, {"x": x, "sin": np.sin, "cos": np.cos, "exp": np.exp, "sqrt": np.sqrt})
    except Exception as e:
        print(f"函数解析错误: {e}")
        exit()

    current_file = os.path.basename(__file__)
    os.system(f"manim -pqh {current_file} FunctionPlot")