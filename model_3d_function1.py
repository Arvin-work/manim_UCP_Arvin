from manim import * # type: ignore
import numpy as np
import os
import sys
import ast

def get_input(prompt, default, is_required=True):
    """安全获取用户输入"""
    while True:
        user_input = input(f"{prompt}（默认：{default}）: ").strip()
        if not user_input:
            if is_required:
                print("此参数为必填项！")
                continue
            user_input = default
        try:
            # 使用AST解析进行基本安全检查
            ast.parse(user_input, mode='eval')
            return user_input
        except:
            print("输入包含非法字符，请重新输入！")

class InteractiveSurface(ThreeDScene):
    def construct(self):
        # 从环境变量获取参数
        params = {
            'u_var': os.getenv("U_VAR", "u"),
            'v_var': os.getenv("V_VAR", "v"),
            'x_expr': os.getenv("X_EXPR"),
            'y_expr': os.getenv("Y_EXPR"),
            'z_expr': os.getenv("Z_EXPR"),
            'u_min': float(os.getenv("U_MIN", "-2")),
            'u_max': float(os.getenv("U_MAX", "2")),
            'v_min': float(os.getenv("V_MIN", "-2")),
            'v_max': float(os.getenv("V_MAX", "2"))
        }

        # 验证必要参数
        if None in [params['x_expr'], params['y_expr'], params['z_expr']]:
            error = Text("缺少必要参数！", color=RED)
            self.play(Write(error))
            self.wait(2)
            return

        # 创建安全评估环境
        math_env = {
            "sin": np.sin, "cos": np.cos, "exp": np.exp,
            "sqrt": np.sqrt, "log": np.log, "pi": np.pi,
            "e": np.e, "u": 0.0, "v": 0.0  # 初始化参数值
        }

        # 定义参数方程生成器
        try:
            def param_func(u, v):
                math_env[params['u_var']] = u
                math_env[params['v_var']] = v
                x = eval(params['x_expr'], {"__builtins__": None}, math_env)
                y = eval(params['y_expr'], {"__builtins__": None}, math_env)
                z = eval(params['z_expr'], {"__builtins__": None}, math_env)
                return np.array([x, y, z])
            
            # 测试函数
            test_point = param_func(0, 0)
            if len(test_point) != 3:
                raise ValueError("输出必须是三维坐标")
        except Exception as e:
            error = Text(f"方程错误: {str(e)}", color=RED, font_size=24)
            self.play(Write(error))
            self.wait(3)
            return

        # 创建三维场景
        self.set_camera_orientation(phi=75*DEGREES, theta=-45*DEGREES)
        axes = ThreeDAxes()
        
        # 创建曲面
        surface = Surface(
            param_func,
            u_range=[params['u_min'], params['u_max']],
            v_range=[params['v_min'], params['v_max']],
            resolution=(32, 32),
            fill_opacity=0.7,
            stroke_width=1.5,
            color=BLUE
        )
        
        # 添加动画
        self.play(Create(axes))
        self.play(Create(surface), time=2)
        self.begin_ambient_camera_rotation(rate=0.3)
        self.wait(5)

if __name__ == "__main__":
    # 收集用户输入
    print("""=== 三维曲面参数输入 ===
         （表达式可以使用sin/cos/exp/sqrt/log等函数）
         （示例：x=u, y=v, z=u**2 + v**2）""")

    u_var = get_input("请输入u参数名称", "u")
    v_var = get_input("请输入v参数名称", "v")
    x_expr = get_input("输入x的表达式（使用u/v变量）", "", is_required=True)
    y_expr = get_input("输入y的表达式（使用u/v变量）", "", is_required=True)
    z_expr = get_input("输入z的表达式（使用u/v变量）", "", is_required=True)

    # 设置参数范围
    u_min = float(get_input("输入u最小值", "-2", is_required=False))
    u_max = float(get_input("输入u最大值", "2", is_required=False))
    v_min = float(get_input("输入v最小值", "-2", is_required=False))
    v_max = float(get_input("输入v最大值", "2", is_required=False))

    # 存入环境变量
    os.environ.update({
        "U_VAR": u_var,
        "V_VAR": v_var,
        "X_EXPR": x_expr,
        "Y_EXPR": y_expr,
        "Z_EXPR": z_expr,
        "U_MIN": str(u_min),
        "U_MAX": str(u_max),
        "V_MIN": str(v_min),
        "V_MAX": str(v_max)
    })

    # 启动渲染
    current_file = os.path.basename(__file__)
    os.system(f"manim -pqh {current_file} InteractiveSurface")