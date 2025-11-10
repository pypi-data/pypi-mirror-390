# filename: others.py
# @Time    : 2025/11/7 17:35
# @Author  : JQQ
# @Email   : jqq1716@gmail.com
# @Software: PyCharm
"""
其他提供商模型家族配置 / Other providers' model family configurations

包含：百度、腾讯、月之暗面、MiniMax 等
Including: Baidu, Tencent, Moonshot, MiniMax, etc.
"""

from whosellm.capabilities import ModelCapabilities
from whosellm.models.base import ModelFamily
from whosellm.models.config import ModelFamilyConfig
from whosellm.provider import Provider

# ============================================================================
# 百度 ERNIE 系列 / Baidu ERNIE Series
# ============================================================================

ERNIE = ModelFamilyConfig(
    family=ModelFamily.ERNIE,
    provider=Provider.BAIDU,
    version_default="1.0",
    variant_priority_default=(1,),  # base 的优先级 / base priority
    patterns=[
        "ernie-{version:d}-{variant:variant}",
        "ernie-{variant:variant}",
        "ernie",
        "wenxin",  # 别名 / Alias
    ],
    capabilities=ModelCapabilities(
        supports_function_calling=True,
        supports_streaming=True,
        max_tokens=8192,
        context_window=8192,
    ),
)

# ============================================================================
# 腾讯混元系列 / Tencent Hunyuan Series
# ============================================================================

HUNYUAN = ModelFamilyConfig(
    family=ModelFamily.HUNYUAN,
    provider=Provider.TENCENT,
    version_default="1.0",
    variant_priority_default=(1,),  # base 的优先级 / base priority
    patterns=[
        "hunyuan-{variant:variant}",
        "hunyuan",
    ],
    capabilities=ModelCapabilities(
        supports_function_calling=True,
        supports_streaming=True,
        max_tokens=8192,
        context_window=32000,
    ),
)

# ============================================================================
# 月之暗面 Moonshot 系列 / Moonshot Series
# ============================================================================

MOONSHOT = ModelFamilyConfig(
    family=ModelFamily.MOONSHOT,
    provider=Provider.MOONSHOT,
    version_default="1.0",
    variant_priority_default=(1,),  # base 的优先级 / base priority
    patterns=[
        "moonshot-{version:d}-{variant:variant}",
        "moonshot-{variant:variant}",
        "moonshot",
    ],
    capabilities=ModelCapabilities(
        supports_function_calling=True,
        supports_streaming=True,
        max_tokens=8192,
        context_window=200000,
    ),
)

# ============================================================================
# MiniMax ABAB 系列 / MiniMax ABAB Series
# =========================================================================

ABAB = ModelFamilyConfig(
    family=ModelFamily.ABAB,
    provider=Provider.MINIMAX,
    version_default="1.0",
    variant_priority_default=(1,),  # base 的优先级 / base priority
    patterns=[
        "abab-{version:d}-{variant:variant}",
        "abab-{variant:variant}",
        "abab",
    ],
    capabilities=ModelCapabilities(
        supports_function_calling=True,
        supports_streaming=True,
        max_tokens=8192,
        context_window=8192,
    ),
)
