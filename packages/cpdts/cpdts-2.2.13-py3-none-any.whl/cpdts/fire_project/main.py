
import os
from pathlib import Path
from ..utils import create_file_with_path
import questionary
import json


def fire_create():
    # 获取当前模块文件的目录

    project_name= questionary.text("请输入项目名称").ask().strip()
    pypi_name_check = questionary.confirm("是否进行PYPI项目名称检查").ask()
    if pypi_name_check:
        try:
            while True: 
                if not check_pypi_package_name(project_name):
                    break 
                else:
                    print("包名已存在，请重新输入")
                    project_name= questionary.text("请输入项目名称").ask().strip()
                    continue
        except :
            return
    
    creat_process(project_name)

def check_pypi_package_name(package_name):
    # 检查当前 package_name 是否已经存在于 PyPI 上
    import requests
    try:
        response = requests.get(f"https://pypi.org/pypi/{package_name}/json", timeout=10)
        if response.status_code == 200:
            print("包名已存在，不可以使用")
            return True  # 包名已存在
        elif response.status_code == 404:
            print("包名不存在，可以正常使用")
            # print(json.dumps(response.json(), indent=2, ensure_ascii=False))
            # 虽然能够检查到 包名是不是已经存在了 但是仍然无法判断这个包名能不能用 真的头痛

            return False  # 包名不存在，可以使用
        else:
            print(f"检查包名时出现异常状态码: {response.status_code}")
            return None  # 检查失败
    except requests.exceptions.RequestException as e:
        print(f"检查包名时网络请求失败: {e}")
        return None  # 检查失败



def creat_process(project_name):
    current_dir = Path(__file__).parent

    items = {
        ".vscode/settings.json":{
            "template": "/templates/vscode/settings.json",
        },
        ".kiro/hooks/auto-init-imports.kiro.hook":{
            "template": "/templates/kiro/auto-init-imports.kiro.hook",
        },
        ".kiro/steering/main.md":{
            "template": "/templates/kiro/main.md",
        },
        f"src/{project_name}/__init__.py":{
            "template": "templates/src/init.py",
        },
        f"src/{project_name}/decorators/singleton.py":{
            "template": "templates/src/decorators/singleton.py",
        },
        f"scripts/build_and_publish.py":{
            "template": "templates/scripts/build_and_publish.py",
        },
        "pyproject.toml":{
            "template": "templates/pyproject.toml.j2",
            "data": {
                "project_name": project_name
            }
        },
        ".gitignore":{
            "template": "templates/.gitignore",
        },
        "README.md":{
            "template": "templates/README.md",
        }
    }


    for item in items:
        template = items[item]["template"]
        data = items[item].get("data", {})
        create_file_with_path(f'{project_name}/{item}', f"{current_dir}/{template}", data)

    pass