"""
完整的日志管理器模块
这个文件在构建时会被加密
"""
import os
import logging
import sys
from pathlib import Path
from datetime import datetime

class LogManager:
    """高级日志管理器"""

    def __init__(self):
        self.default_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        self.default_level = logging.INFO

    def setup_logging(self,
                     name=None,
                     level=logging.INFO,
                     log_dir=None,
                     format_string=None,
                     file_mode='a',
                     stream=True,
                     max_bytes=10*1024*1024,  # 10MB
                     backup_count=5):
        """
        设置日志配置

        Args:
            name: 日志器名称，默认为调用者模块名
            level: 日志级别，默认INFO
            log_dir: 日志目录，默认为当前目录下的logs文件夹
            format_string: 日志格式字符串
            file_mode: 文件模式，'a'为追加，'w'为覆盖
            stream: 是否输出到控制台
            max_bytes: 日志文件最大字节数
            backup_count: 备份文件数量

        Returns:
            logging.Logger: 配置好的日志器
        """
        # 如果没有提供名称，使用调用者的模块名
        if name is None:
            import inspect
            frame = inspect.currentframe()
            try:
                # 回溯到调用setup_logging的帧
                caller_frame = frame.f_back
                caller_module = caller_frame.f_globals['__name__']
                name = caller_module
            finally:
                del frame

        # 创建日志器
        logger = logging.getLogger(name)
        logger.setLevel(level)

        # 避免重复添加处理器
        if logger.handlers:
            return logger

        # 设置日志格式
        if format_string is None:
            format_string = self.default_format
        formatter = logging.Formatter(format_string)

        # 设置日志目录
        if log_dir is None:
            log_dir = Path.cwd() / 'logs'
        else:
            log_dir = Path(log_dir)

        log_dir.mkdir(exist_ok=True)

        # 生成日志文件名
        log_file = log_dir / f"{name}.log"

        try:
            # 使用RotatingFileHandler支持日志轮转
            from logging.handlers import RotatingFileHandler
            file_handler = RotatingFileHandler(
                log_file,
                mode=file_mode,
                encoding='utf-8',
                maxBytes=max_bytes,
                backupCount=backup_count
            )
        except ImportError:
            # 回退到普通FileHandler
            file_handler = logging.FileHandler(log_file, mode=file_mode, encoding='utf-8')

        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        # 控制台处理器
        if stream:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(level)
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)

        return logger

    def get_logger(self, name=None):
        """
        获取日志器（简化版本，使用默认配置）

        Args:
            name: 日志器名称

        Returns:
            logging.Logger: 配置好的日志器
        """
        return self.setup_logging(name=name)

    def set_level(self, logger, level):
        """
        设置日志级别

        Args:
            logger: 日志器
            level: 日志级别
        """
        logger.setLevel(level)
        for handler in logger.handlers:
            handler.setLevel(level)

    def add_file_handler(self, logger, file_path, level=logging.INFO, format_string=None):
        """
        添加文件处理器

        Args:
            logger: 日志器
            file_path: 文件路径
            level: 日志级别
            format_string: 日志格式
        """
        if format_string is None:
            format_string = self.default_format

        file_handler = logging.FileHandler(file_path, encoding='utf-8')
        file_handler.setLevel(level)
        file_handler.setFormatter(logging.Formatter(format_string))
        logger.addHandler(file_handler)

# 创建全局日志管理器实例
_log_manager = LogManager()

# 便捷函数
def setup_logging(name=None, level=logging.INFO, log_dir=None, format_string=None, file_mode='a', stream=True):
    """设置日志配置的便捷函数"""
    return _log_manager.setup_logging(
        name=name,
        level=level,
        log_dir=log_dir,
        format_string=format_string,
        file_mode=file_mode,
        stream=stream
    )

def get_logger(name=None):
    """获取日志器的便捷函数"""
    return _log_manager.get_logger(name=name)

def set_level(logger, level):
    """设置日志级别的便捷函数"""
    _log_manager.set_level(logger, level)

def add_file_handler(logger, file_path, level=logging.INFO, format_string=None):
    """添加文件处理器的便捷函数"""
    _log_manager.add_file_handler(logger, file_path, level, format_string)