from .auth import is_activated


class ToolManager:
    """工具管理器"""

    def __init__(self):
        if not is_activated():
            raise PermissionError("软件未激活！请先运行 'poxiaoai code' 进行激活。")

    def process_data(self, data):
        """处理数据"""
        if not is_activated():
            raise PermissionError("软件未激活！")

        # 这里实现你的数据处理逻辑
        return f"处理后的数据: {data}"

    def analyze_file(self, file_path):
        """分析文件"""
        if not is_activated():
            raise PermissionError("软件未激活！")

        # 这里实现文件分析逻辑
        return f"已分析文件: {file_path}"


class DataProcessor:
    """数据处理器"""

    def __init__(self):
        if not is_activated():
            raise PermissionError("软件未激活！")

    def transform(self, data):
        """数据转换"""
        if not is_activated():
            raise PermissionError("软件未激活！")
        return data.upper()

    def validate(self, data):
        """数据验证"""
        if not is_activated():
            raise PermissionError("软件未激活！")
        return len(data) > 0


class FileHandler:
    """文件处理器"""

    def __init__(self):
        if not is_activated():
            raise PermissionError("软件未激活！")

    def read_file(self, path):
        """读取文件"""
        if not is_activated():
            raise PermissionError("软件未激活！")
        with open(path, 'r') as f:
            return f.read()

    def write_file(self, path, content):
        """写入文件"""
        if not is_activated():
            raise PermissionError("软件未激活！")
        with open(path, 'w') as f:
            f.write(content)