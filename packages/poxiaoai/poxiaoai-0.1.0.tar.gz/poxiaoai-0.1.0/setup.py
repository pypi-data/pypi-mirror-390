from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="poxiaoai",
    version="0.1.0",
    author="你的名字",  # 替换为你的名字
    author_email="你的邮箱@example.com",  # 替换为你的邮箱
    description="一个实用的Python工具类集合",  # 简短描述
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",  # 确保与你的LICENSE文件一致
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.7",
    install_requires=[],  # 如有依赖包，在此列出
    entry_points={  # 可选：创建命令行工具
        'console_scripts': [
            'poxiaoai-demo=poxiaoai.core:main',  # 示例，如无命令行功能可删除
        ],
    },
)