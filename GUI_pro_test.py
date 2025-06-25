from tkinter import ttk
import tkinter as tk
import os
import sys
import subprocess


def create_new_window(number):
    new_window = tk.Toplevel(root)
    new_window.title("按钮信息")
    label = ttk.Label(new_window, text=f"你点击了按钮 {number}", padding=10)
    label.pack()
    close_button = ttk.Button(new_window, text="关闭", command=new_window.destroy)
    close_button.pack(pady=5)


def run_script(script_name):
    def wrapper():
        current_dir = os.path.dirname(os.path.abspath(__file__))
        cmd_command = f'cd /d "{current_dir}" && "{sys.executable}" "{script_name}"'
        subprocess.Popen(
            f'start cmd /k "{cmd_command}"',
            shell=True,
            cwd=current_dir
        )

    return wrapper


def create_one_window(text):
    window = tk.Toplevel(root)
    window.title(f"{text}")
    window.geometry("400x300")

    style = ttk.Style()
    style.configure('TEntry', padding=5)
    style.configure('Title.TLabel', font=('微软雅黑', 10, 'bold'))

    # 第一行输入框
    input_frame = ttk.Frame(window)
    input_frame.pack(pady=10, fill='x', padx=10)
    ttk.Label(input_frame, text="y=", style='Title.TLabel').grid(row=0, column=0)
    equation_entry = ttk.Entry(input_frame, width=25)
    equation_entry.grid(row=0, column=1, padx=5)
    action_btn = ttk.Button(input_frame, text="解析并绘制信息",
                            command=lambda: print("解析并绘制信息"))
    action_btn.grid(row=0, column=2, padx=5)

    # 区域设置
    region_frame = ttk.LabelFrame(window, text="区域设置", padding=(10, 5))  # 修正点
    region_frame.pack(pady=10, fill='x', padx=10)

    # x范围
    ttk.Label(region_frame, text="x范围 =").grid(row=0, column=0, sticky='w')
    x_start = ttk.Entry(region_frame, width=15)
    x_start.grid(row=0, column=1, padx=2)
    ttk.Label(region_frame, text="到").grid(row=0, column=2)  # 列索引修正
    x_end = ttk.Entry(region_frame, width=15)
    x_end.grid(row=0, column=3, padx=(2, 10))

    # y范围
    ttk.Label(region_frame, text="y范围 =").grid(row=1, column=0, sticky='w', pady=5)
    y_start = ttk.Entry(region_frame, width=15)
    y_start.grid(row=1, column=1, padx=2)
    ttk.Label(region_frame, text="到").grid(row=1, column=2)
    y_end = ttk.Entry(region_frame, width=15)
    y_end.grid(row=1, column=3, padx=(2, 10))

    # 显示选项
    option_frame = ttk.Frame(window)
    option_frame.pack(pady=15, fill='x', padx=10)

    deriv_var = tk.BooleanVar()
    ttk.Checkbutton(option_frame,
                    text="导数展示",
                    variable=deriv_var,
                    command=lambda: print("导数展示")).pack(side=tk.LEFT, padx=20)

    integral_var = tk.BooleanVar()  # 变量名修正
    ttk.Checkbutton(option_frame,
                    text="积分展示",
                    variable=integral_var,
                    command=lambda: print("积分展示")).pack(side=tk.RIGHT, padx=20)

    # 响应式布局
    window.columnconfigure(0, weight=1)
    for frame in [input_frame, region_frame, option_frame]:
        frame.columnconfigure(1, weight=1)


# 创建主窗口
root = tk.Tk()
root.title("Manim命令中心")
root.geometry('500x450')

# 配置ttk样式
style = ttk.Style()
style.theme_use('clam')  # 使用支持自定义样式的主题

# 自定义按钮样式
style.configure('Custom.TButton',
                font=('微软雅黑', 10),
                background='#E1F5FE',
                bordercolor='#B3E5FC',
                relief='groove',
                padding=10,
                width=15)

style.map('Custom.TButton',
          background=[('active', '#B3E5FC'), ('disabled', '#F5F5F5')],
          relief=[('pressed', 'sunken'), ('!pressed', 'groove')])

buttons_config = [
    {"text": "二维显式函数", "script": "model_function1.py", "row": 0, "col": 0},
    {"text": "二维隐函数", "script": "model_function2.py", "row": 1, "col": 0},
    {"text": "极坐标参数方程", "script": "model_function3.py", "row": 2, "col": 0},
    {"text": "二维显式积分", "script": "intergral_function1.py", "row": 0, "col": 1},
    {"text": "极坐标积分", "script": "intergeal_function3.py", "row": 1, "col": 1},
    {"text": "三维图形绘制", "script": "model_3d_function1.py", "row": 2, "col": 1},
    {"text": "显式求导", "script": "derivative_function1.py", "row": 0, "col": 2},
    {"text": "隐函数求导", "script": "derivative_function2.py", "row": 1, "col": 2},
    {"text": "三维相机设置", "script": "3Dcamera_new.py", "row": 2, "col": 2}
]

# 创建ttk按钮
for config in buttons_config:
    if config["script"] == "model_function1.py":
        btn = ttk.Button(
            root,
            text=config["text"],
            style='Custom.TButton',
            command=lambda: create_one_window("二维显式函数"),
            width=15
        )
    else:
        btn = ttk.Button(
            root,
            text=config["text"],
            style='Custom.TButton',
            command=run_script(config["script"]),
            width=15
        )

    btn.grid(
        row=config["row"],
        column=config["col"],
        sticky="nsew",
        padx=5,
        pady=5,
        ipady=8  # 增加垂直内边距
    )

# 配置网格布局权重
for col in range(3):
    root.columnconfigure(col, weight=1)
for row in range(3):
    root.rowconfigure(row, weight=1)

# 状态栏升级为ttk
status_bar = ttk.Label(
    root,
    text=f"当前工作目录：{os.path.dirname(os.path.abspath(__file__))}",
    relief="sunken",
    padding=(10, 5),
    anchor="w"
)
status_bar.grid(row=3, column=0, columnspan=3, sticky="ew")

root.mainloop()