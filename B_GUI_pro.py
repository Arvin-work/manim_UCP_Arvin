from tkinter import *
from tkinter import ttk
import tkinter as tk


def create_new_window(number):
    new_window = tk.Toplevel(root)
    new_window.title("按钮信息")
    label = tk.Label(new_window, text=f"你点击了按钮 {number}", padx=20, pady=20)
    label.pack()
    close_button = tk.Button(new_window, text="关闭", command=new_window.destroy)
    close_button.pack(pady=5)


def create_one_window(number):
    window = tk.Toplevel(root)
    window.title("绘制二维平面图形（显式）")
    window.geometry("400x300")

    style = ttk.Style()
    style.configure('TEntry', padding=5)
    style.configure('Title.TLabel', font=('微软雅黑', 10, 'bold'))

    if number == 1:
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

for row in range(3):
    for col in range(3):
        button_number = row * 3 + col + 1
        if button_number == 1:
            btn = tk.Button(root,
                            text="绘制二维\n平面图形\n（显式）",
                            width=8,
                            height=4,
                            command=lambda num=button_number: create_one_window(num))
        else:
            btn = tk.Button(root,
                            text=str(button_number),
                            width=8,
                            height=4,
                            command=lambda num=button_number: create_new_window(num))
        btn.grid(row=row, column=col, padx=5, pady=5)

root.mainloop()