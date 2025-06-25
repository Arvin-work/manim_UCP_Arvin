"""对于相关函数进行绘制，并同时对于函数取其
    斜线来展现微分的意义"""
# 辅助函数：获取浮点数输入
from manim import *
import numpy as np
import os


def get_float_input(prompt, default):
    user_input = input(f"{prompt}（默认{default}）：")
    return float(user_input) if user_input.strip() != "" else default

# 设置坐标轴范围
x_defaults = (-10.0, 10.0, 1.0)
y_defaults = (-10.0, 10.0, 1.0)

x_left = get_float_input("x轴左侧边界", x_defaults[0])
x_right = get_float_input("x轴右侧边界", x_defaults[1])
x_step = get_float_input("x轴步长", x_defaults[2])

y_left = get_float_input("y轴左侧边界", y_defaults[0])
y_right = get_float_input("y轴右侧边界", y_defaults[1])
y_step = get_float_input("y轴步长", y_defaults[2])

# 获取函数表达式并解析
func_input = input("请输入显式函数 y = f(x)（例如 sin(x)*exp(x)）：")

try:
    # 注入数学函数到作用域
    func = lambda x: eval(
        func_input,
        {
            "x": x,
            "sin": np.sin,    # 直接提供sin函数
            "cos": np.cos,    # 直接提供cos函数
            "exp": np.exp     # 直接提供指数函数
        }
    )
except SyntaxError:
    print("表达式语法错误！")
    exit()
except NameError as e:
    print(f"函数未定义: {e}")
    exit()

class FunctionPlot(Scene):
    def construct(self):
        axes = Axes(
            x_range=[x_left, x_right, x_step],
            y_range=[y_left, y_right, y_step],
            axis_config={"color": GREY}
        )
        graph = axes.plot(func, color=BLUE)
        self.play(Create(axes), run_time=2)
        self.play(Create(graph), run_time=3)
        self.wait(2)

        # 开始创造切线并进行求导
        # 确定切点

        moving_dot = Dot(color=BLUE_A)

        # 创建值追踪器
        t = ValueTracker(x_left)

        # 点的位置更新函数
        def update_dot(mob):
            x = t.get_value()
            mob.move_to(axes.c2p(x, func(x)))

        # 切线更新
        def update_tangent():
            x = t.get_value()
            return axes.get_secant_slope_group(
                x, graph, dx=0.01,
                secant_line_length=3,
                secant_line_color=YELLOW
            )
        
        
        
        # 设置更新器
        moving_dot.add_updater(update_dot)
        tangent_group = always_redraw(update_tangent)

        # 添加相关元素
        self.add(moving_dot, tangent_group)
        self.wait(0.5)

        self.play(
            t.animate.set_value(x_right),
            run_time=6,
            rate_func=linear
        )
        
        # 清楚更新器
        moving_dot.remove_updater(update_dot)
        self.wait(2)
        

if __name__ == "__main__":
    # 自动渲染（防止重复执行）
    current_file = os.path.basename(__file__)
    os.system(f"manim -pqh {current_file} FunctionPlot")