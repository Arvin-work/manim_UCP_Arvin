import tkinter

window = tkinter.Tk()
window.title('Text')

name_f = tkinter.Label(window, text='函数')
name_f.grid(row=1)
content_f = tkinter.Entry(window)
content_f.grid(row=1, column=1)


dynamic_vars = {}


def save_tem():
    information_tem = content_f.get()
    for i in range(10):
        # 使用字典的键来存储变量
        if dynamic_vars.get(f'var{i}') is not None:
            continue
        else:
            dynamic_vars[f'var{i}'] = information_tem
            print(dynamic_vars[f'var{i}'])
            break  # 找到第一个空变量后退出循环


# 创建并放置按钮
save_button = tkinter.Button(window, text='保存', command=save_tem)
save_button.grid(row=2, columnspan=2)


window.mainloop()


from manim import *

class Text(Scene):
    def construct(self):
        background = NumberPlane()
        self.play(Create(background))
        x_range = [-10, 10]
        t = ValueTracker(0)

        def func(x):
            return # USER_FUNCTION_PLACEHOLDER

        self.wait()
        graph = background.plot(func, x_range=x_range)
        self.play(FadeIn(graph))
        self.wait(3)


def save_tem():
    information_tem = content_f.get()
    for i in range(10):
        # 使用字典的键来存储变量
        if dynamic_vars.get(f'var{i}') is not None:
            continue
        else:
            dynamic_vars[f'var{i}'] = information_tem
            content = f''
            with open("text_content.txt", "w") as target_file:
                target_file.write(content)
            print(dynamic_vars[f'var{i}'])
            break  # 找到第一个空变量后退出循环


save_button = tkinter.Button(window, text='保存', command=save_tem)
save_button.grid(row=2, columnspan=2)