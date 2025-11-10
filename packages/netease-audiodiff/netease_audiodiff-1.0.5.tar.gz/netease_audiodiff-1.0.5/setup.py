from setuptools import setup
import setuptools
import os

with open("README.md", "r",encoding="utf-8") as fh:
    long_description = fh.read()

# 修复 data_files 路径问题：确保文件能正确打包（兼容不同目录结构）
def get_data_files():
    data_files = []
    # 定义需要打包的文件及其目标目录
    file_list = [
        "AUDIODIFF/ffmpeg.exe",
        "AUDIODIFF/ffprobe.exe",
        "AUDIODIFF/config.json"
    ]
    for file_path in file_list:
        # 检查文件是否存在（避免打包失败）
        if os.path.exists(file_path):
            # 目标目录为空字符串，表示打包到包的根目录
            data_files.append(('', [file_path]))
        else:
            print(f"警告：文件 {file_path} 不存在，将不会被打包")
    return data_files

setup(
    name='netease_audiodiff',
    version='1.0.5',
    packages=setuptools.find_packages(),
    url='https://g.hz.netease.com/hzpansongsheng/audio_diff/-/tree/feature/pypi',
    license='MIT',
    author=' PAN SONGSHENG',
    author_email='hzpansongsheng@corp.netease.com',
    description='With this Toolset and one audio cable you can simply built end2end audio test paltform base on mac,which means,Its very Lightweight，Easy to build and carry',
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=[
    'argparse',
    'numpy',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Operating System :: MacOS :: MacOS X",  # 明确支持 macOS（根据 description 补充）
        "Operating System :: Microsoft :: Windows",  # 如果你也支持 Windows（根据之前的报错补充）
    ],
    package_data={
        'netease_audiodiff': [  # 包名（必须和实际包目录一致）
            'ffmpeg.exe',
            'ffprobe.exe',
            'config.json'
        ]
    },
    include_package_data=True,  # 确保包内数据文件被正确包含
    python_requires='>=3.7',
)

