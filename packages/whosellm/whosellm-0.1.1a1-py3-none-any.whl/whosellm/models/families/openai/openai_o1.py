# filename: openai_o1.py
# @Time    : 2025/11/8 13:33
# @Author  : JQQ
# @Email   : jiaqia@qknode.com
# @Software: PyCharm
from whosellm.capabilities import ModelCapabilities
from whosellm.models.base import ModelFamily
from whosellm.models.config import ModelFamilyConfig, SpecificModelConfig
from whosellm.provider import Provider

# ============================================================================
# O1 系列 / O1 Series
# ============================================================================

O1 = ModelFamilyConfig(
    family=ModelFamily.O1,
    provider=Provider.OPENAI,
    version_default="1.0",
    variant_priority_default=(1,),  # base 的优先级 / base priority
    patterns=[
        "o1-{year:4d}-{month:2d}-{day:2d}",
        "o1-{variant:variant}-{year:4d}-{month:2d}-{day:2d}",
        "o1-{variant:variant}",
        "o1",
    ],
    capabilities=ModelCapabilities(
        supports_thinking=True,
        supports_function_calling=True,
        supports_streaming=True,
        supports_structured_outputs=True,
        supports_json_outputs=True,
        max_tokens=100000,
        context_window=200000,
    ),
    specific_models={
        "o1-pro": SpecificModelConfig(
            version_default="1.0",
            variant_default="pro",
            variant_priority=(4,),  # pro 的优先级 / pro priority
            capabilities=ModelCapabilities(
                supports_thinking=True,
                supports_function_calling=True,
                supports_streaming=False,
                supports_structured_outputs=True,
                supports_json_outputs=True,
                max_tokens=100000,
                context_window=200000,
            ),
            patterns=[
                "o1-pro-{year:4d}-{month:2d}-{day:2d}",
                "o1-pro",
            ],
        ),
    },
)
