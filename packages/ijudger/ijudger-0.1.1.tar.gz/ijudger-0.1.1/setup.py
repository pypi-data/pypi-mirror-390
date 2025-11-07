from setuptools import setup, find_packages

setup(
    name="ijudger",             # 你的项目名
    version="0.1.1",              # 新版本号，必须比 PyPI 上大
    packages=find_packages(),      # 自动找所有包
    install_requires=[             # 依赖列表
        # "numpy>=1.25",
    ],
    python_requires=">=3.8",       # 你的 Python 版本要求
    author="icaijy",
    author_email="caijunyi08@outlook.com",
    description="A small judge system for competitive programming",
    url="https://github.com/icaijy/ijudger",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
