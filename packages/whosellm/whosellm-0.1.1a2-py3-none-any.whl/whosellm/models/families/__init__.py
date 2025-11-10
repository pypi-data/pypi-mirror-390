# filename: __init__.py
# @Time    : 2025/11/7 17:35
# @Author  : JQQ
# @Email   : jqq1716@gmail.com
# @Software: PyCharm
"""
自动导入所有模型家族配置 / Auto-import all model family configurations

导入所有提供商的配置文件，触发自动注册
Import all provider configuration files to trigger auto-registration
"""

# 导入所有提供商的配置，触发自动注册
# Import all provider configurations to trigger auto-registration
from whosellm.models.families import (
    alibaba,
    anthropic,
    deepseek,
    openai,
    others,
    vidu,
    zhipu,
)

__all__ = [
    "alibaba",
    "anthropic",
    "deepseek",
    "openai",
    "others",
    "vidu",
    "zhipu",
]
