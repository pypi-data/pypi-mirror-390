"""
加密模块加载器
"""
import os
import base64
import zlib
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import importlib.util


def generate_decryption_key(password: str, salt: bytes) -> bytes:
    """生成解密密钥"""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))


def load_encrypted_module(module_name: str):
    """加载加密模块"""
    try:
        # 加密密码（与构建时相同）
        password = "poxiaoai_encryption_key_2024"

        # 模块路径
        package_dir = os.path.dirname(__file__)
        encrypted_file = os.path.join(package_dir, 'encrypted', f'{module_name}.py')

        if not os.path.exists(encrypted_file):
            raise FileNotFoundError(f"加密模块文件不存在: {encrypted_file}")

        # 读取加密文件
        with open(encrypted_file, 'rb') as f:
            salt = f.read(16)
            encrypted_data = f.read()

        # 生成密钥并解密
        key = generate_decryption_key(password, salt)
        fernet = Fernet(key)

        decrypted = fernet.decrypt(encrypted_data)
        decompressed = zlib.decompress(decrypted)
        source_code = decompressed.decode('utf-8')

        # 创建模块
        spec = importlib.util.spec_from_loader(
            module_name,
            loader=None,
            origin=encrypted_file
        )
        module = importlib.util.module_from_spec(spec)

        # 执行解密后的代码
        exec(source_code, module.__dict__)

        return module

    except Exception as e:
        print(f"加载加密模块 {module_name} 失败: {e}")
        return None