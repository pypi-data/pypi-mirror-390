# setup.py
from setuptools import setup, find_packages, Extension
from Cython.Build import cythonize
import os
import sys
from pathlib import Path

# 获取项目根目录
project_root = Path(__file__).parent


def get_package_data():
    """获取包数据文件"""
    package_data = {}

    # 检查是否已经编译了扩展
    compiled_dir = project_root / "src" / "celldect"
    for ext in ['.pyd', '.so']:
        compiled_files = list(compiled_dir.glob(f"*{ext}"))
        if compiled_files:
            package_data['celldect'] = [f"*{ext}"]
            break

    return package_data


# 判断是否发布模式
is_publish = os.environ.get('BUILD_FOR_PUBLISH') == '1'

if not is_publish:
    # 开发模式：编译Cython扩展
    extensions = cythonize([
        Extension(
            "celldect.core",
            ["src/celldect/core.pyx"],
            extra_compile_args=['/O2', '/GL-'] if os.name == 'nt' else ['-O3', '-Wno-unused-function'],
            define_macros=[('NPY_NO_DEPRECATED_API', 'NPY_1_7_API_VERSION')],
        )
    ], compiler_directives={
        'language_level': "3",
        'boundscheck': False,
        'wraparound': False,
        'initializedcheck': False,
        'nonecheck': False,
    })
else:
    # 发布模式：不编译，只包含已编译的文件
    extensions = []

setup(
    name="celldect",
    version="0.1.0",
    author="cellman",
    author_email="cellman1980@google.com",
    description="A cell image process Python package",
    long_description=open('README.md').read() if Path('README.md').exists() else "",
    long_description_content_type="text/markdown",
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    ext_modules=extensions,
    package_data=get_package_data(),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        # 你的依赖
        "numpy>=1.18.0",
    ],
    setup_requires=[
        "cython>=0.29.0",
        "numpy>=1.18.0",
    ],
)