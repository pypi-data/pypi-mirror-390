# filename: openai_gpt_4o.py
# @Time    : 2025/11/8 13:29
# @Author  : JQQ
# @Email   : jiaqia@qknode.com
# @Software: PyCharm
from whosellm.capabilities import ModelCapabilities
from whosellm.models.base import ModelFamily
from whosellm.models.config import ModelFamilyConfig, SpecificModelConfig
from whosellm.provider import Provider

# ============================================================================
# GPT-4o 系列 / GPT-4o Series
# ============================================================================

GPT_4O = ModelFamilyConfig(
    family=ModelFamily.GPT_4O,
    provider=Provider.OPENAI,
    version_default="4.0",
    variant_default="omni",
    variant_priority_default=(6,),  # omni 的优先级 / omni priority
    patterns=[
        "gpt-4o-{variant:variant}-{year:4d}-{month:2d}-{day:2d}",
        "gpt-4o-{year:4d}-{month:2d}-{day:2d}",  # 日期模式优先
        "gpt-4o-{variant:variant}",
        "gpt-4o",
    ],
    capabilities=ModelCapabilities(
        supports_vision=True,
        supports_streaming=True,
        supports_function_calling=True,
        supports_structured_outputs=True,
        supports_json_outputs=True,
        supports_fine_tuning=True,
        supports_distillation=True,
        supports_predicted_outputs=True,
        max_tokens=16384,
        context_window=128000,
    ),
    specific_models={
        "gpt-4o-audio-preview": SpecificModelConfig(
            version_default="4.0",
            variant_default="audio-preview",
            variant_priority=(0,),  # preview 的优先级 / preview priority
            capabilities=ModelCapabilities(
                supports_vision=True,
                supports_streaming=True,
                supports_function_calling=True,
                supports_structured_outputs=False,
                supports_json_outputs=False,
                supports_fine_tuning=False,
                supports_distillation=False,
                supports_predicted_outputs=False,
                max_tokens=16384,
                context_window=128000,
            ),
            patterns=[
                "gpt-4o-audio-preview-{year:4d}-{month:2d}-{day:2d}",
                "gpt-4o-audio-preview",
            ],
        ),
        "gpt-4o-mini": SpecificModelConfig(
            version_default="4.0",
            variant_default="mini",
            variant_priority=(0,),  # mini 的优先级 / mini priority
            capabilities=ModelCapabilities(
                supports_vision=True,
                supports_streaming=True,
                supports_function_calling=True,
                supports_structured_outputs=True,
                supports_json_outputs=True,
                supports_fine_tuning=True,
                supports_predicted_outputs=True,
                max_tokens=16384,
                context_window=128000,
            ),
            patterns=[
                "gpt-4o-mini-{year:4d}-{month:2d}-{day:2d}",
                "gpt-4o-mini",
            ],
        ),
        "gpt-4o-mini-audio-preview": SpecificModelConfig(
            version_default="4.0",
            variant_default="mini-audio-preview",
            variant_priority=(0,),  # mini-preview 的优先级 / mini-preview priority
            capabilities=ModelCapabilities(
                supports_vision=True,
                supports_streaming=True,
                supports_function_calling=True,
                supports_structured_outputs=False,
                supports_json_outputs=False,
                supports_fine_tuning=False,
                supports_distillation=False,
                supports_predicted_outputs=False,
                max_tokens=16384,
                context_window=128000,
            ),
            patterns=[
                "gpt-4o-mini-audio-preview-{year:4d}-{month:2d}-{day:2d}",
                "gpt-4o-mini-audio-preview",
            ],
        ),
        "gpt-4o-mini-realtime-preview": SpecificModelConfig(
            version_default="4.0",
            variant_default="mini-realtime-preview",
            variant_priority=(0,),  # mini-preview 的优先级 / mini-preview priority
            capabilities=ModelCapabilities(
                supports_vision=True,
                supports_streaming=False,
                supports_function_calling=True,
                supports_structured_outputs=False,
                supports_json_outputs=False,
                supports_fine_tuning=False,
                supports_distillation=False,
                supports_predicted_outputs=False,
                max_tokens=4096,
                context_window=16000,
            ),
            patterns=[
                "gpt-4o-mini-realtime-preview-{year:4d}-{month:2d}-{day:2d}",
                "gpt-4o-mini-realtime-preview",
            ],
        ),
    },
)
