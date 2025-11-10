# filename: tencent.py
# @Time    : 2025/11/9 16:54
# @Author  : Cascade AI
"""
腾讯云提供的 DeepSeek 模型家族配置 / Tencent Cloud DeepSeek model family configuration

腾讯云提供多个 DeepSeek 系列模型
Tencent Cloud provides multiple DeepSeek series models
"""

from whosellm.capabilities import ModelCapabilities
from whosellm.models.base import ModelFamily
from whosellm.models.config import ModelFamilyConfig, SpecificModelConfig
from whosellm.provider import Provider

# 腾讯云 DeepSeek 家族配置
DEEPSEEK_TENCENT = ModelFamilyConfig(
    family=ModelFamily.DEEPSEEK,
    provider=Provider.TENCENT,
    version_default="v3",
    variant_default="base",
    variant_priority_default=(1,),
    patterns=[
        "deepseek-v{version}",
        "deepseek-r{version}",
    ],
    capabilities=ModelCapabilities(
        supports_function_calling=True,
        supports_streaming=True,
        max_tokens=16000,
        context_window=64000,
    ),
    specific_models={
        # DeepSeek-V3-0324
        "deepseek-v3-0324": SpecificModelConfig(
            version_default="v3-0324",
            variant_default="v3-0324",
            capabilities=ModelCapabilities(
                supports_function_calling=True,
                supports_streaming=True,
                max_tokens=16000,
                context_window=128000,
            ),
            variant_priority=(1,),
            patterns=[
                "deepseek-v3-0324",
            ],
        ),
        # DeepSeek-V3
        "deepseek-v3": SpecificModelConfig(
            version_default="v3",
            variant_default="v3",
            capabilities=ModelCapabilities(
                supports_function_calling=True,
                supports_streaming=True,
                max_tokens=16000,
                context_window=64000,
            ),
            variant_priority=(1,),
            patterns=[
                "deepseek-v3",
            ],
        ),
        # DeepSeek-R1
        "deepseek-r1": SpecificModelConfig(
            version_default="r1",
            variant_default="r1",
            capabilities=ModelCapabilities(
                supports_thinking=True,
                supports_function_calling=True,
                supports_streaming=True,
                max_tokens=16000,
                context_window=96000,
            ),
            variant_priority=(2,),
            patterns=[
                "deepseek-r1",
            ],
        ),
        # DeepSeek-R1-0528
        "deepseek-r1-0528": SpecificModelConfig(
            version_default="r1-0528",
            variant_default="r1-0528",
            capabilities=ModelCapabilities(
                supports_thinking=True,
                supports_function_calling=True,
                supports_streaming=True,
                max_tokens=16000,
                context_window=128000,
            ),
            variant_priority=(2,),
            patterns=[
                "deepseek-r1-0528",
            ],
        ),
        # DeepSeek-V3.1
        "deepseek-v3.1": SpecificModelConfig(
            version_default="v3.1",
            variant_default="v3.1",
            capabilities=ModelCapabilities(
                supports_thinking=True,
                supports_function_calling=True,
                supports_streaming=True,
                max_tokens=32000,
                context_window=128000,
            ),
            variant_priority=(1,),
            patterns=[
                "deepseek-v3.1",
            ],
        ),
        # DeepSeek-V3.1-Terminus
        "deepseek-v3.1-terminus": SpecificModelConfig(
            version_default="v3.1-terminus",
            variant_default="v3.1-terminus",
            capabilities=ModelCapabilities(
                supports_thinking=True,
                supports_function_calling=True,
                supports_streaming=True,
                max_tokens=32000,
                context_window=128000,
            ),
            variant_priority=(1,),
            patterns=[
                "deepseek-v3.1-terminus",
            ],
        ),
        # DeepSeek-V3.2-Exp
        "deepseek-v3.2-exp": SpecificModelConfig(
            version_default="v3.2-exp",
            variant_default="v3.2-exp",
            capabilities=ModelCapabilities(
                supports_thinking=True,
                supports_function_calling=True,
                supports_streaming=True,
                max_tokens=64000,
                context_window=128000,
            ),
            variant_priority=(1,),
            patterns=[
                "deepseek-v3.2-exp",
            ],
        ),
    },
)
