from manim import *
import numpy as np
import os

# 辅助函数：获取浮点数输入
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

        # 添加动态切线功能
        x_tracker = ValueTracker(x_left)

        # 进行数值微分计算
        def derivative(x):
            h = 0.001
            return (func(x + h)- func(x - h))/ (2 * h)
        
        # 动态更新元素
        dot = always_redraw(
            lambda: Dot(
                color=BLUE,
                point=axes.c2p(
                    x_tracker.get_value(),
                    func(x_tracker.get_value())
                )
            )
        )

        # 绘制切线相关内容
        tangent_line = always_redraw(
            lambda: axes.plot(
                lambda x: func(x_tracker.get_value()) + derivative(x_tracker.get_value())*(x-x_tracker.get_value()),
                x_range=[
                    x_tracker.get_value() - 1.5,  # 切线的显示范围
                    x_tracker.get_value() + 1.5
                ],
                color=YELLOW
            )
        )

        self.play(Create(axes), run_time=2)
        self.play(Create(graph), run_time=3)

        # 创建导数展示相关元素
        self.add(dot, tangent_line)
        self.play(
            x_tracker.animate.set_value(x_right),  # 从左到右扫描切线
            run_time=8,
            rate_functions=linear
        )

        self.wait(2)

if __name__ == "__main__":
    # 自动渲染（防止重复执行）
    current_file = os.path.basename(__file__)
    os.system(f"manim -pqh {current_file} FunctionPlot")