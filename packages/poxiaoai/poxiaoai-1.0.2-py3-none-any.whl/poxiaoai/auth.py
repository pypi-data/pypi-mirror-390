import os
import getpass
import hashlib
import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import json

class ActivationManager:
    def __init__(self):
        self.activation_file = os.path.expanduser("~/.poxiaoai_activation")
        self.fixed_key = "poxiaoai"

    def is_activated(self):
        """检查是否已激活"""
        if not os.path.exists(self.activation_file):
            return False

        try:
            with open(self.activation_file, 'r') as f:
                data = json.load(f)
                activation_code = data.get('activation_code', '')
                return self._verify_activation_code(activation_code)
        except:
            return False

    def _verify_activation_code(self, code):
        """验证激活码"""
        # 使用固定密钥poxiaoai进行验证
        expected_hash = hashlib.sha256(self.fixed_key.encode()).hexdigest()
        input_hash = hashlib.sha256(code.encode()).hexdigest()
        return expected_hash == input_hash

    def activate(self, activation_code):
        """激活软件"""
        if self._verify_activation_code(activation_code):
            os.makedirs(os.path.dirname(self.activation_file), exist_ok=True)
            with open(self.activation_file, 'w') as f:
                json.dump({
                    'activation_code': activation_code,
                    'activated': True
                }, f)
            return True
        return False

    def decrypt_content(self, encrypted_content):
        """解密内容"""
        if not self.is_activated():
            raise PermissionError("请先激活软件: poxiaoai code")

        try:
            # 使用激活码作为密钥解密
            key = hashlib.sha256(self.fixed_key.encode()).digest()
            encrypted_data = base64.b64decode(encrypted_content)

            cipher = AES.new(key, AES.MODE_ECB)
            decrypted = cipher.decrypt(encrypted_data)
            decrypted = unpad(decrypted, AES.block_size)

            return decrypted.decode('utf-8')
        except Exception as e:
            raise ValueError(f"解密失败: {e}")

activation_manager = ActivationManager()