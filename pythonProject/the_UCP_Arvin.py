# 用户操作面板编程
import subprocess
import tkinter

window = tkinter.Tk()
window.title('UCP_Arvin')

var = tkinter.StringVar()


text = tkinter.Label(window, textvariable=var, width=15, height=2)
text.grid(row=0, column=0)
visual = False


# 设置函数输入的文本框
name_f = tkinter.Label(window, text='函数')
name_f.grid(row=1)
content_f = tkinter.Entry(window)
content_f.grid(row=1, column=1)


dynamic_vars = {}


def save_function():
    function_expression = f'            return {content_f.get()}'
    with open("function_Arvin.py", "r") as file:
        lines = file.readlines()

    # Replace the placeholder line with the new function expression
    with open("function_Arvin.py", "w") as file:
        for line in lines:
            if 'return # USER_FUNCTION_PLACEHOLDER' in line:
                file.write(function_expression + '\n')
            else:
                file.write(line)
    var.set("Function saved and new file created.")

save_button = tkinter.Button(window, text='保存', command=save_function)
save_button.grid(row=2, columnspan=2)


def active():
    commend = 'manim -p -qh function_Arvin.py Text'

    process = subprocess.Popen(['powershell', commend], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    stdout, stderr = process.communicate()

    print("Output", stdout)

    if stderr:
        print("Ettor:", stderr)


btn02_text = tkinter.Button(window, text="运行", background="gray", font=('Arial', 12),
                            width=10, height=1, command=active)
btn02_text.grid(row=3, column=0, pady=10)


# 新添加的保存到.txt文件的函数和按钮,即将text.py中的源代码传入.txt当中
def save_to_txt():
    with open("text.py", "r") as source_file:
        content = source_file.read()

    with open("text_content.txt", "w") as target_file:
        target_file.write(content)

    var.set("Content saved to text_sub_content.txt")


btn_save = tkinter.Button(window, text="Save to .txt", background="gray", font=('Arial', 12),
                          width=10, height=1, command=save_to_txt)
btn_save.grid(row=4, column=0, pady=10)


# 将the_main_part.py的文件进行重写
def replace_code():
    # Read the content from text_content.txt
    with open("text_content.txt", "r") as source_file:
        new_content = source_file.read()

    # Replace the content of the_main_part.py with the new content
    with open("the_main_part.py", "w") as target_file:
        target_file.write(new_content)

    var.set("Code replaced in the_main_part.py")


# Button to replace the code
btn_replace_code = tkinter.Button(window, text="Replace Code", background="gray", font=('Arial', 12),
                                  width=10, height=1, command=replace_code)
btn_replace_code.grid(row=5, column=0, pady=10)


def resetting():
    # Read the content from text_content.txt
    with open("text.py", "r") as source_file:
        new_content = source_file.read()

    # Replace the content of the_main_part.py with the new content
    with open("function_Arvin.py", "w") as target_file:
        target_file.write(new_content)

    var.set("Code resetting in the_main_part.py")


# Button to replace the code
btn_resetting = tkinter.Button(window, text="resetting Code", background="gray", font=('Arial', 12),
                                  width=10, height=1, command=resetting)
btn_resetting.grid(row=6, column=0, pady=10)

# 进入消息循环
window.mainloop()