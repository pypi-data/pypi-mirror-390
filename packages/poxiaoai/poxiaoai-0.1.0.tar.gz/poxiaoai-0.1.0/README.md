# Poxiaoai

一个实用的Python工具类集合，提供常用的字符串处理等功能。

## 安装

```bash
pip install poxiaoai
```
```python
from poxiaoai import StringUtils

# 转换为驼峰命名
result = StringUtils.to_camel_case("hello_world")  # 返回 "helloWorld"

# 反转字符串
reversed_str = StringUtils.reverse_string("hello")  # 返回 "olleh"

# 检查回文
is_pal = StringUtils.is_palindrome("A man a plan a canal Panama")  # 返回 True
```