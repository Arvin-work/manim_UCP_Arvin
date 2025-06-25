from manim import *
import os
import sys
import numpy as np


class ImplicitGraphScene(Scene):
    def construct(self):
        # 从环境变量获取隐函数方程
        func_expr = os.getenv("IMPLICIT_FUNC")

        if not func_expr:
            error_text = Text("未输入隐函数方程！", color=RED)
            self.play(Write(error_text))
            self.wait(2)
            return

        # 从环境变量获取坐标参数
        try:
            x_min = float(os.getenv("X_MIN", "-5.0"))
            x_max = float(os.getenv("X_MAX", "5.0"))
            x_step = float(os.getenv("X_STEP", "1.0"))
            y_min = float(os.getenv("Y_MIN", "-5.0"))
            y_max = float(os.getenv("Y_MAX", "5.0"))
            y_step = float(os.getenv("Y_STEP", "1.0"))
        except Exception as e:
            error_text = Text(f"参数错误: {str(e)}", color=RED)
            self.play(Write(error_text))
            self.wait(2)
            return

        # 创建坐标系
        axes = Axes(
            x_range=[x_min, x_max, x_step],
            y_range=[y_min, y_max, y_step],
            axis_config={"include_tip": False}
        )

        # 尝试编译函数表达式
        try:
            func = lambda x, y: eval(
                func_expr,
                {
                    "x": x,
                    "y": y,
                    "sin": np.sin,
                    "cos": np.cos,
                    "exp": np.exp,
                    "sqrt": np.sqrt,
                    "log": np.log,
                    "arctan": np.arctan # 新增这一行
                }
            )
        except Exception as e:
            error_text = Text(f"表达式错误: {str(e)}", color=RED)
            self.play(Write(error_text))
            self.wait(2)
            return

        # 创建隐函数图形
        graph = ImplicitFunction(
            func,
            x_range=[x_min, x_max],
            y_range=[y_min, y_max],
            color=BLUE,
            stroke_width=3
        )

        self.play(Create(axes))
        self.play(Create(graph), run_time=3)
        self.wait(2)


def get_float_input(prompt, default):
    while True:
        user_input = input(f"{prompt}（默认{default}）：")
        if not user_input.strip():
            return default
        try:
            return float(user_input)
        except ValueError:
            print(f"输入错误：'{user_input}' 不是有效数字，请重新输入")


if __name__ == "__main__":
    # 获取隐函数方程
    func_expr = input("请输入隐函数方程（使用x和y变量）: ").strip()

    # 验证方程合法性
    try:
        test = lambda x, y: eval(
            func_expr,
            {
                "x": x,
                "y": y,
                "sin": np.sin,
                "cos": np.cos,
                "exp": np.exp,
                "sqrt": np.sqrt,
                "log": np.log,
                "arctan": np.arctan  # 新增此行
            }
        )
        test(0, 0)  # 测试点
    except Exception as e:
        print(f"表达式错误: {str(e)}")
        sys.exit(1)

    # 获取坐标参数
    print("\n设置坐标范围：")
    x_min = get_float_input("x轴最小值", -5.0)
    x_max = get_float_input("x轴最大值", 5.0)
    x_step = get_float_input("x轴步长", 1.0)
    y_min = get_float_input("y轴最小值", -5.0)
    y_max = get_float_input("y轴最大值", 5.0)
    y_step = get_float_input("y轴步长", 1.0)

    # 存入环境变量
    os.environ["IMPLICIT_FUNC"] = func_expr
    os.environ["X_MIN"] = str(x_min)
    os.environ["X_MAX"] = str(x_max)
    os.environ["X_STEP"] = str(x_step)
    os.environ["Y_MIN"] = str(y_min)
    os.environ["Y_MAX"] = str(y_max)
    os.environ["Y_STEP"] = str(y_step)

    # 渲染场景
    current_file = os.path.basename(__file__)
    os.system(f"manim -pqh {current_file} ImplicitGraphScene")