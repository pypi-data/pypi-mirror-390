# filename: openai_gpt_4.py
# @Time    : 2025/11/8 13:31
# @Author  : JQQ
# @Email   : jiaqia@qknode.com
# @Software: PyCharm
from whosellm.capabilities import ModelCapabilities
from whosellm.models.base import ModelFamily
from whosellm.models.config import ModelFamilyConfig
from whosellm.provider import Provider

# ============================================================================
# GPT-4 系列 / GPT-4 Series
# ============================================================================

GPT_4 = ModelFamilyConfig(
    family=ModelFamily.GPT_4,
    provider=Provider.OPENAI,
    version_default="4.0",
    variant_priority_default=(1,),  # base 的优先级 / base priority
    patterns=[
        "gpt-4-{mmdd:4d}",  # gpt-4-0613
        "gpt-4",  # gpt-4 (base)
    ],
    capabilities=ModelCapabilities(
        supports_function_calling=True,
        supports_streaming=True,
        supports_structured_outputs=False,
        supports_json_outputs=True,
        max_tokens=8192,
        context_window=128000,
    ),
)
