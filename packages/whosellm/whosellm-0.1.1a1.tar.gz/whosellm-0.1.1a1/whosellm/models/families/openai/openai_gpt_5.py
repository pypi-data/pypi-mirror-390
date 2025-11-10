# filename: gpt_5.py
# @Time    : 2025/11/8 13:28
# @Author  : JQQ
# @Email   : jiaqia@qknode.com
# @Software: PyCharm
from whosellm.capabilities import ModelCapabilities
from whosellm.models.base import ModelFamily
from whosellm.models.config import ModelFamilyConfig, SpecificModelConfig
from whosellm.provider import Provider

# ============================================================================
# GPT-5 系列 / GPT-5 Series
# ============================================================================


GPT_5 = ModelFamilyConfig(
    family=ModelFamily.GPT_5,
    provider=Provider.OPENAI,
    version_default="5.0",
    variant_priority_default=(1,),  # base 的优先级 / base priority
    patterns=[
        "gpt-5-{variant:variant}-{year:4d}-{month:2d}-{day:2d}",  # gpt-5-mini-2025-08-07
        "gpt-5-{variant:variant}",  # gpt-5-mini
        "gpt-5",  # gpt-5 (base)
    ],
    capabilities=ModelCapabilities(
        supports_function_calling=True,
        supports_streaming=True,
        supports_structured_outputs=True,
        supports_json_outputs=True,
        supports_fine_tuning=False,
        supports_distillation=True,
        max_tokens=16384,
        context_window=256000,
    ),
    specific_models={
        "gpt-5-mini": SpecificModelConfig(
            version_default="5.0",
            variant_default="mini",
            variant_priority=(0,),  # mini 的优先级 / mini priority
            capabilities=ModelCapabilities(
                supports_function_calling=True,
                supports_streaming=True,
                supports_structured_outputs=True,
                supports_json_outputs=True,
                supports_fine_tuning=False,
                supports_distillation=False,
                max_tokens=8192,
                context_window=128000,
            ),
            patterns=[
                "gpt-5-mini-{year:4d}-{month:2d}-{day:2d}",
                "gpt-5-mini",
            ],
        ),
        "gpt-5-nano": SpecificModelConfig(
            version_default="5.0",
            variant_default="nano",
            variant_priority=(0,),  # nano 的优先级 / nano priority
            capabilities=ModelCapabilities(
                supports_function_calling=True,
                supports_streaming=True,
                supports_structured_outputs=True,
                supports_json_outputs=True,
                supports_fine_tuning=False,
                supports_distillation=False,
                max_tokens=4096,
                context_window=64000,
            ),
            patterns=[
                "gpt-5-nano-{year:4d}-{month:2d}-{day:2d}",
                "gpt-5-nano",
            ],
        ),
        "gpt-5-pro": SpecificModelConfig(
            version_default="5.0",
            variant_default="pro",
            variant_priority=(4,),  # pro 的优先级 / pro priority
            capabilities=ModelCapabilities(
                supports_function_calling=True,
                supports_streaming=True,
                supports_structured_outputs=True,
                supports_json_outputs=True,
                supports_fine_tuning=False,
                supports_distillation=False,
                max_tokens=24576,  # Pro版本token限制更高
                context_window=256000,
            ),
            patterns=[
                "gpt-5-pro-{year:4d}-{month:2d}-{day:2d}",
                "gpt-5-pro",
            ],
        ),
    },
)
