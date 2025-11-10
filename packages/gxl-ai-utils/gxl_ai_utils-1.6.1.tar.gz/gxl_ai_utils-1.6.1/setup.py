from setuptools import setup, find_packages

# 使用 find_packages 查找包
packages = find_packages(where='gxl_ai_utils')

# 打印所有找到的包，格式化为 'gxl_ai_utils/A', 'gxl_ai_utils/B', 'gxl_ai_utils/C' 的样式
formatted_packages = [f"gxl_ai_utils/{package}" for package in packages]
print("Found packages:", formatted_packages)

setup(
    name='gxl_ai_utils',
    version='1.6.1',
    author='Xuelong Geng',
    description='这个是耿雪龙的工具包模块，更新： add func: do_files_identical, update time: 2025-11.10',
    author_email='3349495429@qq.com',
    packages=formatted_packages,  # 在安装时使用的包列表
    install_requires=[  # 安装依赖库
        'jsonlines',
        'colorama',
        'tqdm',
    ],
    package_dir={'': '.'},  # 设置根目录为.
)
