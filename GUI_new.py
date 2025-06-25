from tkinter import *
import os
import sys
import subprocess

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

root = Tk()
root.title("Manim命令中心")
root.geometry('500x450')

# 配置网格布局
for i in range(3):
    root.grid_rowconfigure(i, weight=1, minsize=80)
for j in range(3):
    root.grid_columnconfigure(j, weight=1, minsize=120)

# 按钮配置
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

# 创建按钮
for config in buttons_config:
    btn = Button(
        root,
        text=config["text"],
        command=run_script(config["script"]),
        wraplength=100,
        padx=10,
        pady=10,
        bg="#E1F5FE",
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