# coding=utf-8
import os
import io
from setuptools import setup, find_packages

# 读取 README.md 作为长描述
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), "README.md")
    if os.path.exists(readme_path):
        with io.open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return ""

setup(
    name="pyinstallerex",           # 包名（PyPI 上必须唯一）
    version="0.1.6",                # 版本号（每次发布必须更新）
    description=u"扩展PyInstaller 使其拥有单文件安装功能 不用每次都解压执行",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    license="MIT",
    author="lixin",
    author_email="iiixxxiii@qq.com",
    url="https://gitee.com/iiixxxiii/py-installer-ex",
    package_dir={"": "src"},        # 告诉setuptools包在src目录下
    packages=find_packages(where="src"),  # 自动发现src目录下的子包
    include_package_data=True,      # 包含包数据文件
    package_data={
        "PyInstallerEx": ["../bin/*"],  # 包含bin目录中的所有文件
    },
    python_requires=">=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*",  # 兼容 2.7 和 3.4+
    install_requires=[              # 依赖列表
        "PyInstaller>=3.2.1",
    ],
    entry_points={
        'console_scripts': [
            'pyinstallerex=PyInstallerEx.__main__:main',  # 命令行工具
            'PyInstallerEx=PyInstallerEx.__main__:main',  # 添加大写命令别名
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Build Tools",
    ],
    keywords="PyInstaller, expand, single-file, installer",
    zip_safe=False,
)