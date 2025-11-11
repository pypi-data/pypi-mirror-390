"""
poxiaoai - 需要授权激活的Python工具包
主入口文件，处理加密模块的动态加载
"""
import sys
import os
import importlib.util

# 导入认证模块（这个模块不会被加密，因为需要用于激活检查）
from .auth import is_activated, activate, get_activation_info, decrypt_module

__version__ = "1.0.0"
__author__ = "poxiaoai"

# 导出的公共API
__all__ = ['activate', 'is_activated', 'get_activation_info']

class EncryptedModuleLoader:
    """加密模块加载器"""

    def __init__(self, encrypted_data, module_name):
        self.encrypted_data = encrypted_data
        self.module_name = module_name

    def create_module(self, spec):
        return None  # 使用默认的模块创建

    def exec_module(self, module):
        # 解密并执行模块代码
        try:
            source_code = decrypt_module(self.encrypted_data)
            exec(source_code, module.__dict__)
        except Exception as e:
            raise ImportError(f"无法加载加密模块 {self.module_name}: {e}") from e

def _load_encrypted_module(module_name):
    """加载加密模块"""
    if not is_activated():
        raise PermissionError(f"软件未激活！无法加载模块 {module_name}。请先运行 'poxiaoai code' 进行激活。")

    try:
        # 模块路径
        package_dir = os.path.dirname(__file__)
        encrypted_file = os.path.join(package_dir, 'encrypted', f'{module_name}.py')

        if not os.path.exists(encrypted_file):
            raise FileNotFoundError(f"加密模块文件不存在: {encrypted_file}")

        # 读取加密文件
        with open(encrypted_file, 'rb') as f:
            encrypted_data = f.read()

        # 创建模块规范
        spec = importlib.util.spec_from_loader(
            f"poxiaoai.{module_name}",
            EncryptedModuleLoader(encrypted_data, module_name)
        )

        # 创建并执行模块
        module = importlib.util.module_from_spec(spec)
        sys.modules[f"poxiaoai.{module_name}"] = module
        spec.loader.exec_module(module)

        return module

    except Exception as e:
        # 提供友好的错误信息
        class StubModule:
            def __getattr__(self, name):
                raise PermissionError(f"无法加载模块 '{module_name}'。错误: {e}")

        return StubModule()

# 动态加载加密模块
if is_activated():
    try:
        # 加载 np_log 模块
        np_log_module = _load_encrypted_module('np_log')
        if np_log_module:
            np_log = np_log_module
            __all__.append('np_log')

        # 加载其他工具模块
        tool_modules = ['file_utils', 'data_processor', 'network_tools']
        for mod_name in tool_modules:
            try:
                mod = _load_encrypted_module(mod_name)
                if mod:
                    globals()[mod_name] = mod
                    __all__.append(mod_name)
            except:
                pass  # 模块可能不存在，忽略

    except Exception as e:
        print(f"警告: 加载加密模块时出错: {e}")
else:
    # 未激活时提供占位符
    class StubModule:
        def __getattr__(self, name):
            raise PermissionError("软件未激活！请先运行 'poxiaoai code' 进行激活。")

    # 为所有可能的模块创建占位符
    possible_modules = ['np_log', 'file_utils', 'data_processor', 'network_tools']
    for mod_name in possible_modules:
        globals()[mod_name] = StubModule()
        __all__.append(mod_name)