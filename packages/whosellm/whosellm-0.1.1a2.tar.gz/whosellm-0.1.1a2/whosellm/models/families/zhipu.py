# filename: zhipu.py
# @Time    : 2025/11/7 17:35
# @Author  : JQQ
# @Email   : jqq1716@gmail.com
# @Software: PyCharm
"""
智谱 AI 模型家族配置 / Zhipu AI model family configurations
"""

from whosellm.capabilities import ModelCapabilities
from whosellm.models.base import ModelFamily
from whosellm.models.config import ModelFamilyConfig, SpecificModelConfig
from whosellm.provider import Provider

# ============================================================================
# GLM-3 系列 / GLM-3 Series
# 注意：必须在 GLM_TEXT 之前定义，避免被 glm-{version} 通配符匹配
# Note: Must be defined before GLM_TEXT to avoid being matched by glm-{version} wildcard
# ============================================================================

GLM_3 = ModelFamilyConfig(
    family=ModelFamily.GLM_3,
    provider=Provider.ZHIPU,
    version_default="3.0",
    variant_priority_default=(1,),  # base 的优先级 / base priority
    patterns=[
        "glm-3-{variant:variant}",
        "glm-3",
    ],
    capabilities=ModelCapabilities(
        supports_function_calling=True,
        supports_streaming=True,
        max_tokens=8192,
        context_window=32000,
    ),
)

# ============================================================================
# GLM-Vision 系列（统一的视觉模型家族） / GLM-Vision Series (Unified Vision Model Family)
# 包含 GLM-4V, GLM-4.5V 等所有视觉模型 / Includes GLM-4V, GLM-4.5V and all vision models
# ============================================================================

GLM_VISION = ModelFamilyConfig(
    family=ModelFamily.GLM_VISION,
    provider=Provider.ZHIPU,
    version_default="4.5",
    variant_priority_default=(1,),  # base 的优先级 / base priority
    patterns=[
        # 通用 GLM-{version}V patterns，支持 4v, 4.5v 等
        # Generic GLM-{version}V patterns, supports 4v, 4.5v, etc.
        "glm-{version}v-{variant:variant}-{year:4d}-{month:2d}-{day:2d}",
        "glm-{version}v-{variant:variant}-{mmdd:4d}",
        "glm-{version}v-{variant:variant}",
        "glm-{version}v-{year:4d}-{month:2d}-{day:2d}",
        "glm-{version}v-{mmdd:4d}",
        "glm-{version}v",
    ],
    capabilities=ModelCapabilities(
        supports_thinking=True,
        supports_vision=True,
        supports_video=True,
        supports_pdf=True,
        supports_streaming=True,
        max_tokens=8192,
        context_window=64000,
    ),
    # 特定模型的精确配置 / Precise configuration for specific models
    specific_models={
        # GLM-4V 系列特定模型
        "glm-4v-plus-0111": SpecificModelConfig(
            version_default="4.0",
            variant_default="vision-plus",
            variant_priority=(3,),  # plus 的优先级 / plus priority
            capabilities=ModelCapabilities(
                supports_vision=True,
                supports_video=True,
                supports_streaming=True,
                max_tokens=8192,
                context_window=8192,
                max_image_size_mb=5.0,
                max_image_pixels=(6000, 6000),
                supports_image_base64=True,
                max_video_size_mb=200.0,  # 更大的视频限制
                max_video_duration_seconds=None,  # 无时长限制
            ),
            patterns=[
                "glm-4v-plus-0111",
            ],
        ),
        "glm-4v-plus": SpecificModelConfig(
            version_default="4.0",
            variant_default="vision-plus",
            variant_priority=(3,),  # plus 的优先级 / plus priority
            capabilities=ModelCapabilities(
                supports_vision=True,
                supports_video=True,  # plus 支持视频
                supports_streaming=True,
                max_tokens=8192,
                context_window=8192,
                max_image_size_mb=5.0,
                max_image_pixels=(6000, 6000),
                supports_image_base64=True,
                max_video_size_mb=20.0,
                max_video_duration_seconds=30,
            ),
            patterns=[
                "glm-4v-plus-{mmdd:4d}",
                "glm-4v-plus",
            ],
        ),
        "glm-4v-flash": SpecificModelConfig(
            version_default="4.0",
            variant_default="vision-flash",
            variant_priority=(0,),  # flash 的优先级 / flash priority
            capabilities=ModelCapabilities(
                supports_vision=True,
                supports_streaming=True,
                max_tokens=8192,
                context_window=8192,
                max_image_size_mb=5.0,
                max_image_pixels=(6000, 6000),
                supports_image_base64=False,  # flash 不支持 base64
            ),
        ),
        "glm-4v": SpecificModelConfig(
            version_default="4.0",
            variant_default="base",
            variant_priority=(1,),
            capabilities=ModelCapabilities(
                supports_vision=True,
                supports_function_calling=True,
                supports_streaming=True,
                max_tokens=8192,
                context_window=128000,
                max_image_size_mb=10.0,
                max_image_pixels=(4096, 4096),
            ),
        ),
    },
)

# ============================================================================
# GLM-Text 系列（统一的文本模型家族） / GLM-Text Series (Unified Text Model Family)
# 包含 GLM-4, GLM-4.5, GLM-4.6 等所有文本模型 / Includes GLM-4, GLM-4.5, GLM-4.6 and all text models
# ============================================================================

GLM_TEXT = ModelFamilyConfig(
    family=ModelFamily.GLM_TEXT,
    provider=Provider.ZHIPU,
    version_default="4.6",
    variant_priority_default=(3,),
    patterns=[
        # 通用 GLM-{version} patterns，支持 4, 4.5, 4.6 等
        # Generic GLM-{version} patterns, supports 4, 4.5, 4.6, etc.
        "glm-{version}-{variant:variant}-{year:4d}-{month:2d}-{day:2d}",
        "glm-{version}-{variant:variant}-{mmdd:4d}",
        "glm-{version}-{variant:variant}",
        "glm-{version}-{year:4d}-{month:2d}-{day:2d}",
        "glm-{version}-{mmdd:4d}",
        "glm-{version}",
        "chatglm",  # 别名 / Alias
    ],
    capabilities=ModelCapabilities(
        supports_thinking=True,
        supports_function_calling=True,
        supports_structured_outputs=True,
        supports_streaming=True,
        max_tokens=128000,
        context_window=200000,
    ),
    specific_models={
        # GLM-4.6 系列特定模型
        "glm-4.6": SpecificModelConfig(
            version_default="4.6",
            variant_default="base",
            variant_priority=(3,),
            capabilities=ModelCapabilities(
                supports_thinking=True,
                supports_function_calling=True,
                supports_streaming=True,
                supports_structured_outputs=True,
                max_tokens=128000,
                context_window=200000,
            ),
        ),
        # GLM-4.5 系列特定模型
        "glm-4.5": SpecificModelConfig(
            version_default="4.5",
            variant_default="base",
            variant_priority=(3,),
            capabilities=ModelCapabilities(
                supports_thinking=True,
                supports_function_calling=True,
                supports_structured_outputs=True,
                supports_streaming=True,
                max_tokens=96000,
                context_window=128000,
            ),
        ),
        "glm-4.5-air": SpecificModelConfig(
            version_default="4.5",
            variant_default="air",
            variant_priority=(1,),
            patterns=[
                "glm-4.5-air-{year:4d}-{month:2d}-{day:2d}",
                "glm-4.5-air-{mmdd:4d}",
                "glm-4.5-air",
            ],
        ),
        "glm-4.5-airx": SpecificModelConfig(
            version_default="4.5",
            variant_default="airx",
            variant_priority=(2,),
            patterns=[
                "glm-4.5-airx-{year:4d}-{month:2d}-{day:2d}",
                "glm-4.5-airx-{mmdd:4d}",
                "glm-4.5-airx",
            ],
        ),
        "glm-4.5-x": SpecificModelConfig(
            version_default="4.5",
            variant_default="x",
            variant_priority=(4,),
            patterns=[
                "glm-4.5-x-{year:4d}-{month:2d}-{day:2d}",
                "glm-4.5-x-{mmdd:4d}",
                "glm-4.5-x",
            ],
        ),
        "glm-4.5-flash": SpecificModelConfig(
            version_default="4.5",
            variant_default="flash",
            variant_priority=(0,),
            patterns=[
                "glm-4.5-flash-{year:4d}-{month:2d}-{day:2d}",
                "glm-4.5-flash-{mmdd:4d}",
                "glm-4.5-flash",
            ],
        ),
        # GLM-4 系列特定模型（需要特殊能力配置的）
        "glm-4": SpecificModelConfig(
            version_default="4.0",
            variant_default="base",
            variant_priority=(1,),
            capabilities=ModelCapabilities(
                supports_function_calling=True,
                supports_streaming=True,
                max_tokens=8192,
                context_window=128000,
            ),
        ),
    },
)
# ============================================================================
# CogView-4 系列 / CogView-4 Series
# ============================================================================

COGVIEW_4 = ModelFamilyConfig(
    family=ModelFamily.COGVIEW_4,
    provider=Provider.ZHIPU,
    version_default="4.0",
    variant_priority_default=(1,),
    patterns=[
        "cogview-4-{yymmdd:6d}",
        "cogview-4-{mmdd:4d}",
        "cogview-4",
        "cogview",
    ],
    capabilities=ModelCapabilities(
        supports_streaming=False,
        supports_structured_outputs=False,
    ),
)

# ============================================================================
# CogVideoX-3 系列 / CogVideoX-3 Series
# ============================================================================

COGVIDEOX_3 = ModelFamilyConfig(
    family=ModelFamily.COGVIDEOX_3,
    provider=Provider.ZHIPU,
    version_default="3.0",
    variant_priority_default=(1,),
    patterns=[
        "cogvideox-3-{variant:variant}",
        "cogvideox-3",
    ],
    capabilities=ModelCapabilities(
        supports_vision=True,
        supports_video=True,
        supports_streaming=False,
        supports_structured_outputs=False,
        max_video_duration_seconds=10,
    ),
)

# ============================================================================
# CogVideoX-2 系列 / CogVideoX-2 Series
# ============================================================================

COGVIDEOX_2 = ModelFamilyConfig(
    family=ModelFamily.COGVIDEOX_2,
    provider=Provider.ZHIPU,
    version_default="2.0",
    variant_priority_default=(1,),
    patterns=[
        "cogvideox-2-{variant:variant}",
        "cogvideox-2",
    ],
    capabilities=ModelCapabilities(
        supports_vision=True,
        supports_video=True,
        supports_streaming=False,
        supports_structured_outputs=False,
    ),
)
