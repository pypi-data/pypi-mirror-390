from .auth import activation_manager
from .core import load_encrypted_module

# 这里放置加密后的np_log模块内容
# 这个内容会在构建时由加密脚本生成
NP_LOG_ENCRYPTED = """
U2FsdGVkX1+... (这里会是加密后的内容)
"""

__version__ = "1.0.0"
__author__ = "Your Name"

# 尝试加载np_log模块
try:
    if activation_manager.is_activated():
        np_log_module = load_encrypted_module('poxiaoai.np_log', NP_LOG_ENCRYPTED)
        
        # 将np_log的功能暴露到包级别
        if hasattr(np_log_module, 'get_logger'):
            get_logger = np_log_module.get_logger
        if hasattr(np_log_module, 'setup_logging'):
            setup_logging = np_log_module.setup_logging
            
except Exception as e:
    # 在未激活时，提供友好的错误信息
    pass

def require_activation():
    """检查激活状态的装饰器"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            if not activation_manager.is_activated():
                raise PermissionError("请先激活软件: poxiaoai code")
            return func(*args, **kwargs)
        return wrapper
    return decorator