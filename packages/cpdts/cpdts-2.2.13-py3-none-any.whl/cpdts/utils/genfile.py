



import os
from jinja2 import Template


def create_file_with_path(relative_path,template_path,data):
    # 优雅地分割文件路径和文件名
    directory, filename = os.path.split(relative_path)


    # 在当前文件夹下创建文件路径
    if directory:
        os.makedirs(directory, exist_ok=True)
    # 在创建好的文件路径下创建文件


    # 读取模板文件
    with open(template_path, 'r', encoding='utf-8') as template_file:
        template_content = template_file.read()
    
    # 创建Jinja2模板对象
    template = Template(template_content)
    
    # 渲染模板（这里可以传入变量字典，暂时为空）
    rendered_content = template.render(data)
    
    # 创建并写入文件
    with open(relative_path, 'w', encoding='utf-8') as new_file:
        new_file.write(rendered_content)
    


# print(os.path.split("/test/test/1.txt"))
# print(os.path.split("/test/testdir/"))