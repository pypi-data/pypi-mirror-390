from setuptools import setup, find_packages
import os

# 读取README.md
try:
    with open('README.md', 'r', encoding='utf-8') as f:
        long_description = f.read()
except FileNotFoundError:
    long_description = 'H16Trader - 一个高度自由化的量化交易框架库'

# 读取requirements.txt
try:
    with open('requirements.txt', 'r', encoding='utf-8') as f:
        requirements = f.read().splitlines()
except FileNotFoundError:
    requirements = [
        'pandas>=1.3.0',
        'numpy>=1.20.0',
        'scipy>=1.7.0',
        'matplotlib>=3.3.0',
        'seaborn>=0.11.0'
    ]

setup(
    name="h16trader",
    version="0.1.0",
    author="Aphatar",
    author_email="897367687@qq.com",
    description="一个高度自由化的量化交易框架库",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),  # 这会自动找到 H16Trader 包
    install_requires=requirements,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Financial and Insurance Industry",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)