import os
import json
from pathlib import Path


class ActivationManager:
    def __init__(self):
        self.config_dir = Path.home() / ".poxiaoai"
        self.config_file = self.config_dir / "activation.json"
        self.expected_key = "poxiaoai"  # 授权码

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