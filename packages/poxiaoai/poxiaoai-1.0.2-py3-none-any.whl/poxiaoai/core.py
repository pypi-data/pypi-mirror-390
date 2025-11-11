import sys
import importlib.abc
import importlib.util
import os
from .auth import activation_manager


class EncryptedModuleLoader(importlib.abc.SourceLoader):
    def __init__(self, encrypted_content):
        self.encrypted_content = encrypted_content

    def get_filename(self, fullname):
        return f"<encrypted>{fullname}"

    def get_data(self, filename):
        """获取解密后的源码"""
        if not activation_manager.is_activated():
            print("请先激活软件，运行: poxiaoai code")
            sys.exit(1)

        try:
            return activation_manager.decrypt_content(self.encrypted_content)
        except Exception as e:
            print(f"模块加载失败: {e}")
            sys.exit(1)


def load_encrypted_module(module_name, encrypted_content):
    """动态加载加密模块"""
    loader = EncryptedModuleLoader(encrypted_content)
    spec = importlib.util.spec_from_loader(module_name, loader)
    module = importlib.util.module_from_spec(spec)

    # 将模块添加到sys.modules中
    sys.modules[module_name] = module
    spec.loader.exec_module(module)

    return module