"""
认证和激活管理模块
这个模块不会被加密，因为需要用于激活检查
"""
import os
import json
import base64
import zlib
import hashlib
from pathlib import Path
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class ActivationManager:
    def __init__(self):
        self.config_dir = Path.home() / ".poxiaoai"
        self.config_file = self.config_dir / "activation.json"
        self.expected_key = "poxiaoai"  # 用户激活码
        self.encryption_key = "poxiaoai_encryption_key_2024"  # 源码加密密码

    def _get_machine_fingerprint(self):
        """生成机器指纹"""
        try:
            import getpass
            import platform
            username = getpass.getuser()
            hostname = platform.node()
            fingerprint_str = f"{username}@{hostname}"
            return hashlib.sha256(fingerprint_str.encode()).hexdigest()[:16]
        except:
            return "default_fingerprint"

    def _generate_decryption_key(self, salt):
        """生成解密密钥"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        return base64.urlsafe_b64encode(kdf.derive(self.encryption_key.encode()))

    def decrypt_module(self, encrypted_data):
        """解密模块"""
        if not self.is_activated():
            raise PermissionError("软件未激活，无法解密模块！")

        try:
            # 提取salt和加密内容
            salt = encrypted_data[:16]
            encrypted_content = encrypted_data[16:]

            # 生成解密密钥
            key = self._generate_decryption_key(salt)
            fernet = Fernet(key)

            # 解密
            decrypted = fernet.decrypt(encrypted_content)
            decompressed = zlib.decompress(decrypted)
            return decompressed.decode('utf-8')
        except Exception as e:
            raise PermissionError(f"模块解密失败: {e}")

    def is_activated(self):
        """检查是否已激活"""
        if not self.config_file.exists():
            return False

        try:
            with open(self.config_file, 'r') as f:
                data = json.load(f)

            # 验证激活状态
            if data.get('activated') != True:
                return False

            # 验证机器指纹
            current_fingerprint = self._get_machine_fingerprint()
            if data.get('fingerprint') != current_fingerprint:
                print("检测到运行环境变化，需要重新激活")
                return False

            return True

        except Exception as e:
            return False

    def activate(self, activation_code):
        """激活软件"""
        if activation_code.strip() == self.expected_key:
            # 创建配置目录
            self.config_dir.mkdir(exist_ok=True)

            # 保存激活信息
            activation_data = {
                'activated': True,
                'fingerprint': self._get_machine_fingerprint(),
                'activation_date': str(os.path.getctime(__file__))
            }

            with open(self.config_file, 'w') as f:
                json.dump(activation_data, f)

            print("✅ 激活成功！软件功能已解锁。")
            return True
        else:
            print("❌ 激活码错误！请检查后重试。")
            return False

    def get_activation_info(self):
        """获取激活信息"""
        if self.is_activated():
            with open(self.config_file, 'r') as f:
                return json.load(f)
        return None


# 全局激活管理器
_activation_manager = ActivationManager()


def is_activated():
    return _activation_manager.is_activated()


def activate(activation_code):
    return _activation_manager.activate(activation_code)


def get_activation_info():
    return _activation_manager.get_activation_info()


def decrypt_module(encrypted_data):
    return _activation_manager.decrypt_module(encrypted_data)