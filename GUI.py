from tkinter import *

root = Tk()
root.title("Manim激活区域")
root.geometry('400x400')

# 目前需要此软件激活相关环境,目前需要绑定几个按键各自分别激活相关的python文件以供运行
# 按键1，名字“绘制二维平面图形（显式）”，激活model_function1.py ，位置（1，1）
# 按键2，名字“绘制二维平面图形（隐函数）”，激活model_function2.py，位置（2，1）
# 按键3，名字“绘制二维平面图形（极坐标参数方程）”，激活model_function3.py，位置（3，1）
# 按键4，名字“绘制二维平面积分（显式）”，激活intergeal_function1.py，位置（1，2）
# 按键5，名字“绘制二维平面图形（极坐标参数方程）”，激活intergeal_function3.py，位置（2，2）
# 按键6，名字“绘制三维平面图形”，激活model_3d_function1.py,位置（3，2）
# 按键7，名字“绘制平面曲线求导（显式）”，激活deriviative_function1.py，位置（1，3）
# 按键8，名字“绘制平面曲线求导（隐函数）”，激活deriviative_function2.py，位置（2，3）

root.mainloop()