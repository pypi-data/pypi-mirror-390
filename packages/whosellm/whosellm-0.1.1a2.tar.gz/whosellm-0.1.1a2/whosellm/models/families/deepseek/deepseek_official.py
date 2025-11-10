# filename: deepseek_official.py
# @Time    : 2025/11/9 15:57
# @Author  : Cascade AI
"""
DeepSeek 官方模型家族配置 / DeepSeek official model family configuration

包含 deepseek-chat 与 deepseek-reasoner 模型
Includes deepseek-chat and deepseek-reasoner models
"""

from whosellm.capabilities import ModelCapabilities
from whosellm.models.base import ModelFamily
from whosellm.models.config import ModelFamilyConfig, SpecificModelConfig
from whosellm.provider import Provider

DEEPSEEK = ModelFamilyConfig(
    family=ModelFamily.DEEPSEEK,
    provider=Provider.DEEPSEEK,
    version_default="1.0",
    variant_default="base",
    variant_priority_default=(1,),
    patterns=[
        "deepseek-chat-{suffix}",
        "deepseek-chat",
        "deepseek-reasoner-{suffix}",
        "deepseek-reasoner",
    ],
    capabilities=ModelCapabilities(
        supports_function_calling=True,
        supports_streaming=True,
        max_tokens=8000,
        context_window=128000,
    ),
    specific_models={
        "deepseek-chat": SpecificModelConfig(
            version_default="1.0",
            variant_default="chat",
            capabilities=ModelCapabilities(
                supports_function_calling=True,
                supports_streaming=True,
                max_tokens=8000,
                context_window=128000,
            ),
            variant_priority=(1,),
            patterns=[
                "deepseek-chat-{suffix}",
                "deepseek-chat",
            ],
        ),
        "deepseek-reasoner": SpecificModelConfig(
            version_default="1.0",
            variant_default="reasoner",
            capabilities=ModelCapabilities(
                supports_thinking=True,
                supports_streaming=True,
                # DS Reasoner模型原生是不支持工具调用的，但是官方做了优化，如果向R1模型发起带有Tools调用的请求，会自动路由至Chat模型。
                # 因此在这里标记为支持FunctionCall
                supports_function_calling=True,
                max_tokens=64000,
                context_window=128000,
            ),
            variant_priority=(2,),
            patterns=[
                "deepseek-reasoner-{suffix}",
                "deepseek-reasoner",
            ],
        ),
    },
)
