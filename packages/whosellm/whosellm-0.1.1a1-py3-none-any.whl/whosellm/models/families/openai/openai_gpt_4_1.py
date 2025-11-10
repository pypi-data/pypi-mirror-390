# filename: openai_gpt_4_1.py
# @Time    : 2025/11/8 13:29
# @Author  : JQQ
# @Email   : jiaqia@qknode.com
# @Software: PyCharm
from whosellm.capabilities import ModelCapabilities
from whosellm.models.base import ModelFamily
from whosellm.models.config import ModelFamilyConfig, SpecificModelConfig
from whosellm.provider import Provider

# ============================================================================
# GPT-4.1 系列 / GPT-4.1 Series
# ============================================================================

GPT_4_1 = ModelFamilyConfig(
    family=ModelFamily.GPT_4_1,
    provider=Provider.OPENAI,
    version_default="4.1",
    variant_priority_default=(1,),  # base 的优先级 / base priority
    patterns=[
        "gpt-4.1-{year:4d}-{month:2d}-{day:2d}",
        "gpt-4.1-{variant:variant}-{year:4d}-{month:2d}-{day:2d}",
        "gpt-4.1-{variant:variant}",
        "gpt-4.1-{year:4d}-{month:2d}-{day:2d}",
        "gpt-4.1",
    ],
    capabilities=ModelCapabilities(
        supports_function_calling=True,
        supports_streaming=True,
        supports_structured_outputs=True,
        supports_json_outputs=True,
        supports_fine_tuning=True,
        supports_distillation=True,
        supports_web_search=True,
        supports_file_search=True,
        supports_image_generation=True,
        supports_code_interpreter=True,
        supports_mcp=True,
        max_tokens=32768,
        context_window=1_047_576,
    ),
    specific_models={
        "gpt-4.1-mini": SpecificModelConfig(
            version_default="4.1",
            variant_default="mini",
            variant_priority=(0,),
            capabilities=ModelCapabilities(
                supports_function_calling=True,
                supports_streaming=True,
                supports_structured_outputs=True,
                supports_json_outputs=True,
                supports_fine_tuning=True,
                supports_distillation=False,
                supports_predicted_outputs=True,
                max_tokens=32768,
                context_window=1_047_576,
            ),
            patterns=[
                "gpt-4.1-mini-{year:4d}-{month:2d}-{day:2d}",
                "gpt-4.1-mini",
            ],
        ),
        "gpt-4.1-nano": SpecificModelConfig(
            version_default="4.1",
            variant_default="nano",
            variant_priority=(0,),  # nano 的优先级 (< mini) / nano priority
            capabilities=ModelCapabilities(
                supports_function_calling=True,
                supports_streaming=True,
                supports_structured_outputs=True,
                supports_json_outputs=True,
                supports_fine_tuning=True,
                supports_distillation=False,
                supports_predicted_outputs=True,
                max_tokens=32768,
                context_window=1_047_576,
            ),
            patterns=[
                "gpt-4.1-nano-{year:4d}-{month:2d}-{day:2d}",
                "gpt-4.1-nano",
            ],
        ),
    },
)
