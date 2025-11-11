# poxiaoai Python工具包开发与发布指南

## 项目概述

创建一个名为 `poxiaoai` 的Python工具包，该包需要授权激活才能使用。

## 项目结构

```
poxiaoai-project/
├── setup.py
├── README.md
├── LICENSE
└── poxiaoai/
    ├── __init__.py
    ├── auth.py
    └── cli.py
```

## 1. 创建项目文件

### 1.1 创建项目目录
```bash
mkdir poxiaoai-project
cd poxiaoai-project
mkdir poxiaoai
```

### 1.2 创建 `poxiaoai/__init__.py`
```python
"""
poxiaoai - 需要授权激活的Python工具包
"""

from .auth import activate, is_activated
from .cli import main

__version__ = "1.0.0"
__author__ = "poxiaoai"
```

### 1.3 创建 `poxiaoai/auth.py`
```python
import os
import json
from pathlib import Path

class ActivationManager:
    def __init__(self):
        self.config_dir = Path.home() / ".poxiaoai"
        self.config_file = self.config_dir / "activation.json"
        self.expected_key = "test"  # 授权码
    
    def is_activated(self):
        """检查是否已激活"""
        if not self.config_file.exists():
            return False
            
        try:
            with open(self.config_file, 'r') as f:
                data = json.load(f)
            return data.get('activated', False)
        except:
            return False
    
    def activate(self, activation_code):
        """激活软件"""
        if activation_code.strip() == self.expected_key:
            # 创建配置目录
            self.config_dir.mkdir(exist_ok=True)
            
            # 保存激活信息
            activation_data = {'activated': True}
            
            with open(self.config_file, 'w') as f:
                json.dump(activation_data, f)
            
            print("✅ 激活成功！软件功能已解锁。")
            return True
        else:
            print("❌ 激活码错误！请检查后重试。")
            return False

# 全局激活管理器
_activation_manager = ActivationManager()

def is_activated():
    return _activation_manager.is_activated()

def activate(activation_code):
    return _activation_manager.activate(activation_code)
```

### 1.4 创建 `poxiaoai/cli.py`
```python
import argparse
import getpass
import sys
from .auth import activate, is_activated

def main():
    parser = argparse.ArgumentParser(description='poxiaoai 工具包')
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # 激活命令
    activate_parser = subparsers.add_parser('code', help='输入激活码')
    
    # 状态命令
    status_parser = subparsers.add_parser('status', help='查看激活状态')
    
    args = parser.parse_args()
    
    if args.command == 'code':
        activation_code = getpass.getpass("请输入激活码: ")
        if activate(activation_code):
            sys.exit(0)
        else:
            sys.exit(1)
    
    elif args.command == 'status':
        if is_activated():
            print("✅ 软件已激活")
        else:
            print("❌ 软件未激活")
            print("请运行 'poxiaoai code' 进行激活")
    
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
```

### 1.5 创建 `setup.py`
```python
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="poxiaoai",
    version="1.0.0",
    author="poxiaoai",
    author_email="your_email@example.com",
    description="一个需要授权激活的Python工具包",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    python_requires=">=3.7",
    entry_points={
        "console_scripts": [
            "poxiaoai=poxiaoai.cli:main",
        ],
    },
    keywords="tools, utilities, activation",
)
```

### 1.6 创建 `README.md`
```markdown
# poxiaoai

一个需要授权激活的Python工具包。

## 安装

```bash
pip install poxiaoai
```

## 激活

安装后，首先需要激活：

```bash
poxiaoai code
```

然后输入授权码：`test`

## 使用

查看激活状态：
```bash
poxiaoai status
```

## 许可证

MIT License
```

### 1.7 创建 `LICENSE`
```
MIT License

Copyright (c) 2024 poxiaoai

Permission is hereby granted...
```

## 2. 本地测试

### 2.1 安装开发版本
```bash
# 在项目根目录执行
pip install -e .
```

### 2.2 测试功能
```bash
# 查看帮助
poxiaoai --help

# 查看状态（应该显示未激活）
poxiaoai status

# 激活（输入授权码：test）
poxiaoai code

# 再次查看状态（应该显示已激活）
poxiaoai status
```

## 3. 打包项目

### 3.1 安装打包工具
```bash
pip install setuptools wheel twine
```

### 3.2 构建包
```bash
python setup.py sdist bdist_wheel
```

这会在 `dist/` 目录生成两个文件：
- `poxiaoai-1.0.0-py3-none-any.whl`
- `poxiaoai-1.0.0.tar.gz`

## 4. 上传到PyPI

### 4.1 注册PyPI账号
1. 访问 [PyPI官网](https://pypi.org/)
2. 点击"Register"注册账号
3. 验证邮箱

### 4.2 创建API Token（推荐）
1. 登录PyPI
2. 进入Account Settings → API tokens
3. 创建新的token，scope选择"Entire account"

### 4.3 配置PyPI凭证
创建 `~/.pypirc` 文件（Linux/Mac）或 `%USERPROFILE%\.pypirc`（Windows）：
```ini
[pypi]
username = __token__
password = pypi-你的token内容
```

### 4.4 上传包
```bash
twine upload dist/*
```

## 5. 安装测试

### 5.1 从PyPI安装
```bash
pip install poxiaoai
```

### 5.2 测试功能
```bash
# 激活
poxiaoai code
# 输入: poxiaoai

# 查看状态
poxiaoai status
```

## 6. 版本更新流程

当需要更新版本时：

### 6.1 修改版本号
在 `setup.py` 中更新版本号：
```python
version="1.0.1",  # 增加版本号
```

### 6.2 重新打包
```bash
python setup.py sdist bdist_wheel
```

### 6.3 上传新版本
```bash
twine upload dist/*
```

## 常见问题

### Q: 上传时遇到"File already exists"错误
A: 需要更新版本号，PyPI不允许重复版本

### Q: 激活状态文件在哪里？
A: 在用户主目录的 `.poxiaoai/activation.json`

### Q: 如何重置激活状态？
A: 删除 `~/.poxiaoai/activation.json` 文件

### Q: 如何卸载包？
A: `pip uninstall poxiaoai`

## 注意事项

1. **保护授权码**：实际项目中不要将授权码硬编码在源码中
2. **版本管理**：每次更新都要修改版本号
3. **测试充分**：上传前务必在本地测试所有功能
4. **备份凭证**：妥善保管PyPI API token

## 下一步扩展

- 添加更多工具功能
- 实现网络验证授权
- 添加使用期限限制
- 实现更复杂的加密保护

这样就完成了从开发到发布的完整流程！