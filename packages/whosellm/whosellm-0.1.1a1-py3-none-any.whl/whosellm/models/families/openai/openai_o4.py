# filename: openai_o4.py
# @Time    : 2025/11/8 13:31
# @Author  : JQQ
# @Email   : jiaqia@qknode.com
# @Software: PyCharm
from whosellm.capabilities import ModelCapabilities
from whosellm.models.base import ModelFamily
from whosellm.models.config import ModelFamilyConfig, SpecificModelConfig
from whosellm.provider import Provider

# ============================================================================
# O4 系列 / O4 Series
# ============================================================================

O4 = ModelFamilyConfig(
    family=ModelFamily.O4,
    provider=Provider.OPENAI,
    version_default="4.0",
    variant_priority_default=(1,),  # base 的优先级 / base priority
    patterns=[
        "o4-{variant:variant}-{year:4d}-{month:2d}-{day:2d}",
        "o4-{variant:variant}",
    ],
    capabilities=ModelCapabilities(
        supports_streaming=True,
        supports_function_calling=True,
        supports_structured_outputs=True,
        supports_json_outputs=True,
        supports_fine_tuning=True,
    ),
    specific_models={
        "o4-mini": SpecificModelConfig(
            version_default="4.0",
            variant_default="mini",
            variant_priority=(0,),  # mini 的优先级 / mini priority
            capabilities=ModelCapabilities(
                supports_streaming=True,
                supports_function_calling=True,
                supports_structured_outputs=True,
                supports_json_outputs=True,
                supports_fine_tuning=True,
            ),
            patterns=[
                "o4-mini-{year:4d}-{month:2d}-{day:2d}",
                "o4-mini",
            ],
        ),
        "o4-mini-deep-research": SpecificModelConfig(
            version_default="4.0",
            variant_default="mini-deep-research",
            variant_priority=(0,),  # mini-deep-research 的优先级 / mini-deep-research priority
            capabilities=ModelCapabilities(
                supports_streaming=True,
                supports_function_calling=False,
                supports_structured_outputs=False,
                supports_json_outputs=False,
                supports_fine_tuning=False,
            ),
            patterns=[
                "o4-mini-deep-research-{year:4d}-{month:2d}-{day:2d}",
                "o4-mini-deep-research",
            ],
        ),
    },
)
