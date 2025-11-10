# filename: openai_gpt_3_5.py
# @Time    : 2025/11/8 13:32
# @Author  : JQQ
# @Email   : jiaqia@qknode.com
# @Software: PyCharm
from whosellm.capabilities import ModelCapabilities
from whosellm.models.base import ModelFamily
from whosellm.models.config import ModelFamilyConfig, SpecificModelConfig
from whosellm.provider import Provider

# ======================================================== ====================
# GPT-3.5 系列 / GPT-3.5 Series


GPT_3_5 = ModelFamilyConfig(
    family=ModelFamily.GPT_3_5,
    provider=Provider.OPENAI,
    version_default="3.5",
    variant_default="turbo",
    variant_priority_default=(2,),  # turbo 的优先级 / turbo priority
    patterns=[
        "gpt-3.5-turbo-{year:4d}-{month:2d}-{day:2d}",
        "gpt-3.5-turbo-{snapshot}",
        "gpt-3.5-turbo",
    ],
    capabilities=ModelCapabilities(
        supports_streaming=False,
        supports_function_calling=False,
        supports_structured_outputs=False,
        supports_json_outputs=True,
        supports_fine_tuning=True,
        max_tokens=4096,
        context_window=16385,
    ),
    specific_models={
        "gpt-3.5-turbo": SpecificModelConfig(
            version_default="3.5",
            variant_default="turbo",
            variant_priority=(2,),
            capabilities=ModelCapabilities(
                supports_streaming=False,
                supports_function_calling=False,
                supports_structured_outputs=False,
                supports_json_outputs=True,
                supports_fine_tuning=True,
                max_tokens=4096,
                context_window=16385,
            ),
            patterns=[
                "gpt-3.5-turbo-{year:4d}-{month:2d}-{day:2d}",
                "gpt-3.5-turbo-{snapshot}",
                "gpt-3.5-turbo",
            ],
        ),
        "gpt-3.5-turbo-0125": SpecificModelConfig(
            version_default="3.5",
            variant_default="turbo",
            variant_priority=(2,),
            capabilities=ModelCapabilities(
                supports_streaming=False,
                supports_function_calling=False,
                supports_structured_outputs=False,
                supports_json_outputs=True,
                supports_fine_tuning=True,
                max_tokens=4096,
                context_window=16385,
            ),
            patterns=["gpt-3.5-turbo-0125"],
        ),
    },
)
