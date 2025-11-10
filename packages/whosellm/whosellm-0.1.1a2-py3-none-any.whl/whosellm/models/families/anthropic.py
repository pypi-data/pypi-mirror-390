# filename: anthropic.py
# @Time    : 2025/11/7 17:35
# @Author  : JQQ
# @Email   : jqq1716@gmail.com
# @Software: PyCharm
"""
Anthropic 模型家族配置 / Anthropic model family configurations
"""

from whosellm.capabilities import ModelCapabilities
from whosellm.models.base import ModelFamily
from whosellm.models.config import ModelFamilyConfig, SpecificModelConfig
from whosellm.provider import Provider

# ==========================================================================
# Claude 系列 / Claude Series
# ==========================================================================

CLAUDE = ModelFamilyConfig(
    family=ModelFamily.CLAUDE,
    provider=Provider.ANTHROPIC,
    version_default="4.5",
    variant_default="sonnet",
    variant_priority_default=(3,),  # sonnet 的默认优先级 / default priority for sonnet
    patterns=[
        "claude-{variant:variant}-{major:d}-{minor:d}@{snapshot:8d}",
        "claude-{variant:variant}-{major:d}-{minor:d}-{snapshot:8d}",
        "claude-{variant:variant}-{major:d}-{minor:d}",
        "claude-{variant:variant}-{major:d}-{snapshot:8d}",
        "claude-{variant:variant}-{major:d}",
        "claude-{major:d}-{minor:d}-{variant:variant}-{snapshot:8d}",
        "claude-{major:d}-{minor:d}-{variant:variant}",
        "claude-{major:d}-{variant:variant}-{snapshot:8d}",
        "claude-{major:d}-{variant:variant}",
    ],
    capabilities=ModelCapabilities(
        supports_vision=True,
        supports_thinking=True,
        supports_function_calling=True,
        supports_streaming=True,
        max_tokens=64000,
        context_window=200000,
    ),
    specific_models={
        "claude-sonnet-4-5": SpecificModelConfig(
            version_default="4.5",
            variant_default="sonnet",
            variant_priority=(3,),
            capabilities=ModelCapabilities(
                supports_vision=True,
                supports_thinking=True,
                supports_function_calling=True,
                supports_streaming=True,
                max_tokens=64000,
                context_window=200000,
            ),
            patterns=[
                "claude-sonnet-4-5-{snapshot:8d}",
                "claude-sonnet-4-5",
                "claude-sonnet-4-5@{snapshot:8d}",
            ],
        ),
        "claude-haiku-4-5": SpecificModelConfig(
            version_default="4.5",
            variant_default="haiku",
            variant_priority=(0,),
            capabilities=ModelCapabilities(
                supports_vision=True,
                supports_thinking=True,
                supports_function_calling=True,
                supports_streaming=True,
                max_tokens=64000,
                context_window=200000,
            ),
            patterns=[
                "claude-haiku-4-5-{snapshot:8d}",
                "claude-haiku-4-5",
                "claude-haiku-4-5@{snapshot:8d}",
            ],
        ),
        "claude-opus-4-1": SpecificModelConfig(
            version_default="4.1",
            variant_default="opus",
            variant_priority=(5,),
            capabilities=ModelCapabilities(
                supports_vision=True,
                supports_thinking=True,
                supports_function_calling=True,
                supports_streaming=True,
                max_tokens=32000,
                context_window=200000,
            ),
            patterns=[
                "claude-opus-4-1-{snapshot:8d}",
                "claude-opus-4-1",
                "claude-opus-4-1@{snapshot:8d}",
            ],
        ),
        "claude-sonnet-4-0": SpecificModelConfig(
            version_default="4.0",
            variant_default="sonnet",
            variant_priority=(3,),
            capabilities=ModelCapabilities(
                supports_vision=True,
                supports_thinking=True,
                supports_function_calling=True,
                supports_streaming=True,
                max_tokens=64000,
                context_window=200000,
            ),
            patterns=[
                "claude-sonnet-4-{snapshot:8d}",
                "claude-sonnet-4-0",
                "claude-sonnet-4-0@{snapshot:8d}",
            ],
        ),
        "claude-3-7-sonnet": SpecificModelConfig(
            version_default="3.7",
            variant_default="sonnet",
            variant_priority=(3,),
            capabilities=ModelCapabilities(
                supports_vision=True,
                supports_thinking=True,
                supports_function_calling=True,
                supports_streaming=True,
                max_tokens=64000,
                context_window=200000,
            ),
            patterns=[
                "claude-3-7-sonnet-{snapshot:8d}",
                "claude-3-7-sonnet-latest",
                "claude-3-7-sonnet",
            ],
        ),
        "claude-opus-4-0": SpecificModelConfig(
            version_default="4.0",
            variant_default="opus",
            variant_priority=(5,),
            capabilities=ModelCapabilities(
                supports_vision=True,
                supports_thinking=True,
                supports_function_calling=True,
                supports_streaming=True,
                max_tokens=32000,
                context_window=200000,
            ),
            patterns=[
                "claude-opus-4-{snapshot:8d}",
                "claude-opus-4-0",
                "claude-opus-4-0@{snapshot:8d}",
            ],
        ),
        "claude-3-5-haiku": SpecificModelConfig(
            version_default="3.5",
            variant_default="haiku",
            variant_priority=(0,),
            capabilities=ModelCapabilities(
                supports_vision=True,
                supports_thinking=False,
                supports_function_calling=True,
                supports_streaming=True,
                max_tokens=8000,
                context_window=200000,
            ),
            patterns=[
                "claude-3-5-haiku-{snapshot:8d}",
                "claude-3-5-haiku-latest",
                "claude-3-5-haiku",
            ],
        ),
        "claude-3-haiku": SpecificModelConfig(
            version_default="3.0",
            variant_default="haiku",
            variant_priority=(0,),
            capabilities=ModelCapabilities(
                supports_vision=True,
                supports_thinking=False,
                supports_function_calling=True,
                supports_streaming=True,
                max_tokens=4000,
                context_window=200000,
            ),
            patterns=[
                "claude-3-haiku-{snapshot:8d}",
            ],
        ),
    },
)
