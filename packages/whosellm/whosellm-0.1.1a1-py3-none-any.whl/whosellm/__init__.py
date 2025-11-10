# filename: __init__.py
# @Time    : 2025/11/7 13:56
# @Author  : JQQ
# @Email   : jqq1716@gmail.com
# @Software: PyCharm
"""
LLMeta - 统一的大语言模型版本和能力管理库 / A unified LLM model version and capability management library
"""

__version__ = "0.1.1a1"

from whosellm.capabilities import ModelCapabilities
from whosellm.model_version import LLMeta
from whosellm.models.base import ModelFamily
from whosellm.provider import Provider

__all__ = [
    "LLMeta",
    "ModelCapabilities",
    "ModelFamily",
    "Provider",
    "__version__",
]
