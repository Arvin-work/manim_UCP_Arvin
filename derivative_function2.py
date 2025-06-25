# 此文件依旧有bug，目前无法修复，暂且不可使用

from manim import *
import os
import sys
import numpy as np
from skimage.measure import find_contours  # 新增轮廓查找库

# 数学函数字典
np_funcs = {
    "sin": np.sin,
    "cos": np.cos,
    "exp": np.exp,
    "sqrt": np.sqrt,
    "log": np.log
}


def get_float_input(prompt, default):
    user_input = input(f"{prompt}（默认{default}）：")
    return float(user_input) if user_input.strip() != "" else default

class ImplicitGraphScene(Scene):

    def create_tangent(self, axes, points, tracker):
        
        index = int(tracker.get_value())
        x, y = points[min(max(index, 0), len(points)-1)]
        
        # 计算偏导数
        h = 1e-7
        Fx = (eval(os.getenv("IMPLICIT_FUNC"), {"x": x+h, "y": y, **np_funcs}) -
                    eval(os.getenv("IMPLICIT_FUNC"), {"x": x-h, "y": y, **np_funcs})) / (2*h)
        Fy = (eval(os.getenv("IMPLICIT_FUNC"), {"x": x, "y": y+h, **np_funcs}) -
                    eval(os.getenv("IMPLICIT_FUNC"), {"x": x, "y": y-h, **np_funcs})) / (2*h)
        # 构造切线方向
        if Fy == 0:
            return Line(axes.c2p(x-1,y), axes.c2p(x+1,y), color=YELLOW)
        slope = -Fx/Fy
        return axes.plot(
                lambda t: y + slope*(t - x),
            x_range=[x-1.5, x+1.5],
            color=YELLOW
            )


    def construct(self):
        # 控制区域范围
        # 设置默认值
        x_defaults = (-10.0, 10.0, 1.0)  # 左边界，右边界，步长
        y_defaults = (-10.0, 10.0, 1.0)  # 左边界，右边界，步长

        x_range_left = get_float_input("请输入x轴的左侧边界", x_defaults[0])
        x_range_right = get_float_input("请输入x轴的右侧边界", x_defaults[1])
        x_range_stride = get_float_input("请输入x轴的步长", x_defaults[2])

        y_range_left = get_float_input("请输入y轴的左侧边界", y_defaults[0])
        y_range_right = get_float_input("请输入y轴的右侧边界", y_defaults[1])
        y_range_stride = get_float_input("请输入y轴的步长", y_defaults[2])

        # 从环境变量读取表达式
        func_expr = os.getenv("IMPLICIT_FUNC")

        if not func_expr:
            error_text = Text("未输入隐函数表达式！", color=RED)
            self.play(Write(error_text))
            self.wait(2)
            return

        try:
            func = lambda x, y: eval(func_expr,
                                     {
                                         "x": x,
                                         "y": y,
                                        "sin": np.sin,
                                        "cos": np.cos,
                                        "exp": np.exp,
                                        "sqrt": np.sqrt,
                                        "log": np.log
            })
        except:
            error_text = Text("表达式解析失败！", color=RED)
            self.play(Write(error_text))
            self.wait(2)
            return

        # 计算坐标轴范围跨度并设置纵横比
        x_span = x_range_right - x_range_left
        y_span = y_range_right - y_range_left
        
        # 定义基准长度（例如10单位）
        base_length = 10

        # 创建坐标系和隐函数图形
        axes = Axes(
            x_range=[x_range_left, x_range_right, x_range_stride],
            y_range=[y_range_left, y_range_right, y_range_stride],
            axis_config={
                "scaling": LinearBase(),  # 确保使用线性比例
                "include_tip": False},
            # 新增比例控制参数
            x_length=base_length,  # 设定x轴可视长度（绝对值）
            y_length=base_length * (y_span / x_span) if x_span != 0 else base_length,  # 根据跨度比例设置y轴
        )

        graph = ImplicitFunction(
            func,
            x_range=[x_range_left, x_range_right],
            y_range=[y_range_left, y_range_right],
            color=BLUE,
            stroke_width=3
        )

        # 生成隐函数数据网络
        resolution = 500
        x = np.linspace(x_range_left, x_range_right, resolution)
        y = np.linspace(y_range_left, y_range_right, resolution)
        X, Y =np.meshgrid(x, y, indexing='xy')

        try:
            Z = eval(func_expr, {"x": X, "y": Y, "sin": np.sin, "cos": np.cos,
                               "exp": np.exp, "sqrt": np.sqrt, "log": np.log})
        except:
            print("表达式求值失败！")
            return
        
        # 查找隐函数轮廓
        contours = find_contours(Z, 0)
        if not contours:
            print("未能找到隐函数曲线!")
            return
        
        # 将轮廓坐标转化为实际坐标
        contour_points = []
        for contour in contours:
            for pt in contour:
                px = np.interp(pt[1], [0,resolution-1], [x_range_left, x_range_right])
                py = np.interp(pt[0], [0,resolution-1], [y_range_left, y_range_right])
                contour_points.append([px, py])
        
        # 创建动态元素
        index_tracker = ValueTracker(0)
        dot = always_redraw(lambda: Dot(color=BLUE).move_to(
            axes.c2p(*contour_points[int(index_tracker.get_value())])
        ))

        # 创建切线
        tangent_line = always_redraw(
            lambda: self.create_tangent(axes, contour_points, index_tracker)
        )

        self.play(Create(axes))
        self.play(Create(graph), run_time=3)
        self.add(dot, tangent_line)
        self.play(
            index_tracker.animate.set_value(len(contour_points)-1),
            run_time=10,
            rate_functions=linear
        )

        self.wait(2)


if __name__ == "__main__":
    user_input = input("请输入隐函数方程（使用x和y变量）: ")

    # 验证表达式合法性
    try:
        test = lambda x, y: eval(user_input,
                                     {
                                         "x": x,
                                         "y": y,
                                        "sin": np.sin,
                                        "cos": np.cos,
                                        "exp": np.exp,
                                        "sqrt": np.sqrt,
                                        "log": np.log
        })
    except Exception as e:
        print(f"表达式错误: {e}")
        sys.exit(1)

    # 将表达式存入环境变量
    os.environ["IMPLICIT_FUNC"] = user_input

    # 渲染命令（自动获取当前文件名）
    current_file = os.path.basename(__file__)
    os.system(f"manim -pqh {current_file} ImplicitGraphScene")