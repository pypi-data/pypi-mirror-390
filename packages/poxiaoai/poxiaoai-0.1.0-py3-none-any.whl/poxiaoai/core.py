class StringUtils:
    """
    一个简单的字符串处理工具类
    """

    @staticmethod
    def to_camel_case(text: str, delimiter: str = '_') -> str:
        """
        将下划线命名转换为驼峰命名

        Args:
            text: 要转换的文本
            delimiter: 分隔符，默认为下划线

        Returns:
            驼峰命名字符串
        """
        parts = text.split(delimiter)
        return parts[0] + ''.join(part.capitalize() for part in parts[1:])

    @staticmethod
    def reverse_string(text: str) -> str:
        """
        反转字符串

        Args:
            text: 要反转的文本

        Returns:
            反转后的字符串
        """
        return text[::-1]

    @staticmethod
    def is_palindrome(text: str) -> bool:
        """
        检查字符串是否为回文

        Args:
            text: 要检查的文本

        Returns:
            如果是回文返回True，否则返回False
        """
        cleaned = ''.join(filter(str.isalnum, text)).lower()
        return cleaned == cleaned[::-1]
