from tkinter import ttk
import tkinter as tk
import os
import sys
import subprocess
from tkinter import *

def create_new_window(number):
    new_window = tk.Toplevel(root)
    new_window.title("按钮信息")
    label = tk.Label(new_window, text=f"你点击了按钮 {number}", padx=20, pady=20)
    label.pack()
    close_button = tk.Button(new_window, text="关闭", command=new_window.destroy)
    close_button.pack(pady=5)

def run_script(script_name):
    def wrapper():
        # 获取当前脚本所在目录的绝对路径
        current_dir = os.path.dirname(os.path.abspath(__file__))

        # 构建完整命令
        cmd_command = f'cd /d "{current_dir}" && "{sys.executable}" "{script_name}"'

        # Windows下打开新cmd窗口执行
        subprocess.Popen(
            f'start cmd /k "{cmd_command}"',
            shell=True,
            cwd=current_dir  # 设置工作目录
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

root = tk.Tk()
root.title("Manim命令中心")
root.geometry('500x450')

# 配置网格布局
for i in range(3):
    root.grid_rowconfigure(i, weight=1, minsize=80)
for j in range(3):
    root.grid_columnconfigure(j, weight=1, minsize=120)

buttons_config = [
    {"text": "二维显式函数", "script": "model_function1.py", "row":0, "col":0},
    {"text": "二维隐函数", "script": "model_function2.py", "row":1, "col":0},
    {"text": "极坐标参数方程", "script": "model_function3.py", "row":2, "col":0},
    {"text": "二维显式积分", "script": "intergral_function1.py", "row":0, "col":1},
    {"text": "极坐标积分", "script": "intergeal_function3.py", "row":1, "col":1},
    {"text": "三维图形绘制", "script": "model_3d_function1.py", "row":2, "col":1},
    {"text": "显式求导", "script": "derivative_function1.py", "row":0, "col":2},
    {"text": "隐函数求导", "script": "derivative_function2.py", "row":1, "col":2},
    {"text": "三维相机设置", "script": "3Dcamera_new.py", "row":2, "col":2}
]

# 创建按钮
for config in buttons_config:

    if config["script"] == "model_function1.py":
        btn = Button(
            root,
            text=config["text"],
            command=lambda: create_one_window("二维显式函数"),
            wraplength=100,
            padx=10,
            pady=10,
            font=('微软雅黑', 10),
            relief=GROOVE
        )
        btn.grid(
            row=config["row"],
            column=config["col"],
            sticky="nsew",
            padx=5,
            pady=5
        )
    else:
        btn = Button(
        root,
        text=config["text"],
        command=run_script(config["script"]),
        wraplength=100,
        padx=10,
        pady=10,
        font=('微软雅黑', 10),
        relief=GROOVE
        )
        btn.grid(
        row=config["row"],
        column=config["col"],
        sticky="nsew",
        padx=5,
        pady=5
        )

# 状态栏
status_bar = Label(
    root,
    text=f"当前工作目录：{os.path.dirname(os.path.abspath(__file__))}",
    bd=1,
    relief=SUNKEN,
    anchor=W
)
status_bar.grid(row=3, column=0, columnspan=3, sticky="ew")


root.mainloop()