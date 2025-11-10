# filename: __init__.py
# @Time    : 2025/11/9 15:59
# @Author  : Cascade AI
"""
DeepSeek 模型家族包 / DeepSeek model family package
"""

from whosellm.models.families.deepseek.deepseek_official import DEEPSEEK
from whosellm.models.families.deepseek.tencent import DEEPSEEK_TENCENT

__all__ = ["DEEPSEEK", "DEEPSEEK_TENCENT"]
