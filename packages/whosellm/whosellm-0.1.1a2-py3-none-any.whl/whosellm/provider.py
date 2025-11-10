# filename: provider.py
# @Time    : 2025/11/7 13:56
# @Author  : JQQ
# @Email   : jqq1716@gmail.com
# @Software: PyCharm
"""
模型提供商定义 / Model provider definitions
"""

from enum import Enum
from typing import cast

from whosellm.models.dynamic_enum import DynamicEnumMeta


class Provider(str, Enum, metaclass=DynamicEnumMeta):
    """
    支持的模型提供商 / Supported model providers

    支持动态添加新成员，第三方用户可以在运行时扩展
    Supports dynamically adding new members, third-party users can extend at runtime

    Example:
        >>> # 动态添加新的提供商 / Dynamically add new provider
        >>> Provider.add_member("GOOGLE", "google")
        >>> Provider.add_member("META", "meta")
    """

    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    ZHIPU = "zhipu"  # 智谱AI
    ALIBABA = "alibaba"  # 阿里云
    BAIDU = "baidu"  # 百度
    TENCENT = "tencent"  # 腾讯
    MOONSHOT = "moonshot"  # 月之暗面
    VIDU = "vidu"  # Vidu
    DEEPSEEK = "deepseek"  # DeepSeek
    MINIMAX = "minimax"  # MiniMax
    UNKNOWN = "unknown"

    @classmethod
    def from_model_name(cls, model_name: str) -> "Provider":
        """
        从模型名称推断提供商 / Infer provider from model name

        复用模型注册表中的模式匹配逻辑，避免重复定义
        Reuse pattern matching logic from model registry to avoid duplication

        Args:
            model_name: 模型名称 / Model name

        Returns:
            Provider: 提供商枚举 / Provider enum
        """
        from whosellm.models.registry import match_model_pattern

        # 使用模式匹配找到对应的配置 / Use pattern matching to find the configuration
        matched = match_model_pattern(model_name)
        if matched and "provider" in matched:
            return cast("Provider", matched["provider"])

        return cls.UNKNOWN
