# filename: openai_o3.py
# @Time    : 2025/11/8 13:33
# @Author  : JQQ
# @Email   : jiaqia@qknode.com
# @Software: PyCharm
from whosellm.capabilities import ModelCapabilities
from whosellm.models.base import ModelFamily
from whosellm.models.config import ModelFamilyConfig, SpecificModelConfig
from whosellm.provider import Provider

# ============================================================================
# O3 系列 / O3 Series
# ============================================================================


O3 = ModelFamilyConfig(
    family=ModelFamily.O3,
    provider=Provider.OPENAI,
    version_default="3.0",
    variant_priority_default=(1,),  # base 的优先级 / base priority
    patterns=[
        "o3-{variant:variant}-{year:4d}-{month:2d}-{day:2d}",
        "o3-{variant:variant}",
        "o3-{year:4d}-{month:2d}-{day:2d}",
        "o3",
    ],
    capabilities=ModelCapabilities(
        supports_streaming=True,
        supports_function_calling=True,
        supports_structured_outputs=True,
        supports_json_outputs=True,
    ),
    specific_models={
        "o3": SpecificModelConfig(
            version_default="3.0",
            variant_default="base",
            variant_priority=(1,),  # base 的优先级 / base priority
            capabilities=ModelCapabilities(
                supports_streaming=True,
                supports_function_calling=True,
                supports_structured_outputs=True,
                supports_json_outputs=True,
            ),
            patterns=[
                "o3-{year:4d}-{month:2d}-{day:2d}",
                "o3",
            ],
        ),
        "o3-mini": SpecificModelConfig(
            version_default="3.0",
            variant_default="mini",
            variant_priority=(0,),  # mini 的优先级 / mini priority
            capabilities=ModelCapabilities(
                supports_streaming=True,
                supports_function_calling=True,
                supports_structured_outputs=True,
                supports_json_outputs=True,
            ),
            patterns=[
                "o3-mini-{year:4d}-{month:2d}-{day:2d}",
                "o3-mini",
            ],
        ),
        "o3-pro": SpecificModelConfig(
            version_default="3.0",
            variant_default="pro",
            variant_priority=(4,),  # pro 的优先级 / pro priority
            capabilities=ModelCapabilities(
                supports_streaming=False,
                supports_function_calling=True,
                supports_structured_outputs=True,
                supports_json_outputs=True,
            ),
            patterns=[
                "o3-pro-{year:4d}-{month:2d}-{day:2d}",
                "o3-pro",
            ],
        ),
        "o3-deep-research": SpecificModelConfig(
            version_default="3.0",
            variant_default="deep-research",
            variant_priority=(1,),  # deep-research 的优先级 / deep-research priority
            capabilities=ModelCapabilities(
                supports_streaming=True,
                supports_function_calling=False,
                supports_structured_outputs=False,
                supports_json_outputs=False,
            ),
            patterns=[
                "o3-deep-research-{year:4d}-{month:2d}-{day:2d}",
                "o3-deep-research",
            ],
        ),
    },
)
