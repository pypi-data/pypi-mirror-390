# filename: alibaba.py
# @Time    : 2025/11/7 17:35
# @Author  : JQQ
# @Email   : jqq1716@gmail.com
# @Software: PyCharm
"""
阿里巴巴模型家族配置 / Alibaba model family configurations
"""

from whosellm.capabilities import ModelCapabilities
from whosellm.models.base import ModelFamily
from whosellm.models.config import ModelFamilyConfig, SpecificModelConfig
from whosellm.provider import Provider

# ============================================================================
# Qwen 系列 / Qwen Series
# ============================================================================

QWEN = ModelFamilyConfig(
    family=ModelFamily.QWEN,
    provider=Provider.ALIBABA,
    version_default="1.0",
    variant_priority_default=(1,),  # base 的优先级 / base priority
    patterns=[
        "qwen{version:d}-{variant:variant}-{year:4d}-{month:2d}-{day:2d}",
        "qwen{version:d}-{variant:variant}",
        "qwen-{variant:variant}-{year:4d}-{month:2d}-{day:2d}",
        "qwen-{variant:variant}",
    ],
    capabilities=ModelCapabilities(
        supports_function_calling=True,
        supports_streaming=True,
        supports_vision=True,
        max_tokens=8192,
        context_window=32000,
    ),
    specific_models={
        "qwen3-max": SpecificModelConfig(
            version_default="3",
            variant_default="max",
            capabilities=ModelCapabilities(
                supports_function_calling=True,
                supports_streaming=True,
                supports_structured_outputs=True,
                max_tokens=32000,
                context_window=256000,
            ),
            patterns=[
                "qwen3-max-{year:4d}-{month:2d}-{day:2d}",
                "qwen3-max",
            ],
        ),
        "qwen3-max-preview": SpecificModelConfig(
            version_default="3",
            variant_default="max-preview",
            capabilities=ModelCapabilities(
                supports_thinking=True,
                supports_function_calling=True,
                supports_streaming=True,
                supports_structured_outputs=True,
                max_tokens=64000,
                context_window=256000,
            ),
            patterns=[
                "qwen3-max-preview-{year:4d}-{month:2d}-{day:2d}",
                "qwen3-max-preview",
            ],
        ),
        "qwen3-coder-plus": SpecificModelConfig(
            version_default="3",
            variant_default="coder-plus",
            capabilities=ModelCapabilities(
                supports_function_calling=True,
                supports_structured_outputs=True,
                supports_streaming=True,
                supports_fine_tuning=True,
                max_tokens=64000,
                context_window=1_000_000,
            ),
            patterns=[
                "qwen3-coder-plus-{year:4d}-{month:2d}-{day:2d}",
                "qwen3-coder-plus",
            ],
        ),
        "qwen-image-plus": SpecificModelConfig(
            version_default="1.0",
            variant_default="image-plus",
            capabilities=ModelCapabilities(
                supports_streaming=False,
                supports_structured_outputs=False,
                supports_function_calling=False,
                supports_vision=True,
                supports_image_base64=True,
                supported_image_mime_type=[
                    "image/png",
                    "image/jpeg",
                    "image/webp",
                ],
                max_tokens=None,
                context_window=None,
            ),
            patterns=[
                "qwen-image-plus-{year:4d}-{month:2d}-{day:2d}",
                "qwen-image-plus",
            ],
        ),
        "qwen-image": SpecificModelConfig(
            version_default="1.0",
            variant_default="image",
            capabilities=ModelCapabilities(
                supports_streaming=False,
                supports_structured_outputs=False,
                supports_function_calling=False,
                supports_vision=True,
                supports_image_base64=True,
                supported_image_mime_type=[
                    "image/png",
                    "image/jpeg",
                    "image/webp",
                ],
                max_tokens=None,
                context_window=None,
            ),
            patterns=[
                "qwen-image-{year:4d}-{month:2d}-{day:2d}",
                "qwen-image",
            ],
        ),
        "qwen3-vl-plus": SpecificModelConfig(
            version_default="3",
            variant_default="vl-plus",
            capabilities=ModelCapabilities(
                supports_thinking=True,
                supports_vision=True,
                supports_video=True,
                supports_function_calling=True,
                supports_streaming=True,
                supports_structured_outputs=True,
                max_tokens=32000,
                context_window=256000,
            ),
            patterns=[
                "qwen3-vl-plus-{year:4d}-{month:2d}-{day:2d}",
                "qwen3-vl-plus",
            ],
        ),
        "qwen3-vl-235b-a22b-thinking": SpecificModelConfig(
            version_default="3",
            variant_default="vl-235b-a22b-thinking",
            capabilities=ModelCapabilities(
                supports_thinking=True,
                supports_vision=True,
                supports_video=True,
                supports_function_calling=True,
                supports_streaming=True,
                supports_structured_outputs=True,
                max_tokens=32000,
                context_window=128000,
            ),
            patterns=[
                "qwen3-vl-235b-a22b-thinking-{year:4d}-{month:2d}-{day:2d}",
                "qwen3-vl-235b-a22b-thinking",
            ],
        ),
        "qwen3-vl-32b-thinking": SpecificModelConfig(
            version_default="3",
            variant_default="vl-32b-thinking",
            capabilities=ModelCapabilities(
                supports_thinking=True,
                supports_vision=True,
                supports_video=True,
                supports_function_calling=True,
                supports_streaming=True,
                supports_structured_outputs=True,
                max_tokens=32000,
                context_window=128000,
            ),
            patterns=[
                "qwen3-vl-32b-thinking-{year:4d}-{month:2d}-{day:2d}",
                "qwen3-vl-32b-thinking",
            ],
        ),
        "qwen3-vl-32b-instruct": SpecificModelConfig(
            version_default="3",
            variant_default="vl-32b-instruct",
            capabilities=ModelCapabilities(
                supports_vision=True,
                supports_video=True,
                supports_function_calling=True,
                supports_streaming=True,
                supports_structured_outputs=True,
                max_tokens=32000,
                context_window=128000,
            ),
            patterns=[
                "qwen3-vl-32b-instruct-{year:4d}-{month:2d}-{day:2d}",
                "qwen3-vl-32b-instruct",
            ],
        ),
        "qwen3-vl-flash": SpecificModelConfig(
            version_default="3",
            variant_default="vl-flash",
            capabilities=ModelCapabilities(
                supports_thinking=True,
                supports_vision=True,
                supports_video=True,
                supports_function_calling=True,
                supports_streaming=True,
                supports_structured_outputs=True,
                max_tokens=32000,
                context_window=256000,
            ),
            patterns=[
                "qwen3-vl-flash-{year:4d}-{month:2d}-{day:2d}",
                "qwen3-vl-flash",
            ],
        ),
        "qwen3-vl-30b-a3b-instruct": SpecificModelConfig(
            version_default="3",
            variant_default="vl-30b-a3b-instruct",
            capabilities=ModelCapabilities(
                supports_vision=True,
                supports_video=True,
                supports_function_calling=True,
                supports_streaming=True,
                supports_structured_outputs=True,
                max_tokens=32000,
                context_window=128000,
            ),
            patterns=[
                "qwen3-vl-30b-a3b-instruct-{year:4d}-{month:2d}-{day:2d}",
                "qwen3-vl-30b-a3b-instruct",
            ],
        ),
        "qwen3-vl-8b-thinking": SpecificModelConfig(
            version_default="3",
            variant_default="vl-8b-thinking",
            capabilities=ModelCapabilities(
                supports_thinking=True,
                supports_vision=True,
                supports_video=True,
                supports_function_calling=True,
                supports_streaming=True,
                supports_structured_outputs=True,
                max_tokens=32000,
                context_window=128000,
            ),
            patterns=[
                "qwen3-vl-8b-thinking-{year:4d}-{month:2d}-{day:2d}",
                "qwen3-vl-8b-thinking",
            ],
        ),
        "qwen3-vl-8b-instruct": SpecificModelConfig(
            version_default="3",
            variant_default="vl-8b-instruct",
            capabilities=ModelCapabilities(
                supports_vision=True,
                supports_video=True,
                supports_function_calling=True,
                supports_streaming=True,
                supports_structured_outputs=True,
                max_tokens=32000,
                context_window=128000,
            ),
            patterns=[
                "qwen3-vl-8b-instruct-{year:4d}-{month:2d}-{day:2d}",
                "qwen3-vl-8b-instruct",
            ],
        ),
    },
)
