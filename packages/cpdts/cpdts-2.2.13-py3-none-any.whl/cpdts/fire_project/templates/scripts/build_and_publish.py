
import os
import toml
import subprocess

def dist_clean():
    dist_path = os.path.join(os.getcwd(), 'dist')
    if os.path.exists(dist_path):
        for root, dirs, files in os.walk(dist_path, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir(dist_path)
    else:
        print('dist文件夹不存在')


def version_update():
    pyproject_path = os.path.join(os.getcwd(), 'pyproject.toml')
    
    if not os.path.exists(pyproject_path):
        print('pyproject.toml文件不存在')
        return
    
    try:
        # 读取pyproject.toml文件
        with open(pyproject_path, 'r', encoding='utf-8') as f:
            data = toml.load(f)
        
        # 获取当前版本
        current_version = data.get('project', {}).get('version', '0.0.0')
        
        # 解析版本号并加一
        version_parts = current_version.split('.')
        if len(version_parts) >= 3:
            # 增加补丁版本号
            version_parts[2] = str(int(version_parts[2]) + 1)
        else:
            # 如果版本格式不标准，默认添加.1
            version_parts.append('1')
        
        new_version = '.'.join(version_parts)
        
        # 更新版本号
        if 'project' not in data:
            data['project'] = {}
        data['project']['version'] = new_version
        
        # 写回文件
        with open(pyproject_path, 'w', encoding='utf-8') as f:
            toml.dump(data, f)
        
        print(f'版本号已更新: {current_version} -> {new_version}')
        
    except Exception as e:
        print(f'更新版本号失败: {e}')



def build_wheel():
    try:
        result = subprocess.run(['uv', 'build', '--wheel'], check=True, capture_output=True, text=True)
        print('构建wheel包成功')
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print('构建wheel包失败')
        print(e.stderr)
    except FileNotFoundError:
        print('uv命令未找到，请确保已安装uv')

# 实现 public 函数 来执行 uv public 操作
def public_wheel():
    try:
        result = subprocess.run(['uv', 'publish'], check=True, capture_output=True, text=True)
        print('发布成功')
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print('发布失败')
        print(e.stderr)
    except FileNotFoundError:
        print('uv命令未找到，请确保已安装uv')

if __name__ == '__main__':
    dist_clean()
    version_update()
    build_wheel()
    public_wheel()


