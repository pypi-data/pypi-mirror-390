"""
型号优先级配置测试 / Variant priority configuration tests
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from whosellm import LLMeta
from whosellm.models.base import ModelFamily, infer_variant_priority
from whosellm.models.registry import get_family_config

if TYPE_CHECKING:
    from whosellm.models.config import ModelFamilyConfig

MODEL_VARIANT_SAMPLES: dict[ModelFamily, dict[str, list[str]]] = {
    ModelFamily.GPT_4O: {
        "mini": ["gpt-4o-mini"],
        "mini-audio-preview": ["gpt-4o-mini-audio-preview"],
        "mini-realtime-preview": ["gpt-4o-mini-realtime-preview"],
        "audio-preview": ["gpt-4o-audio-preview"],
        "flash": ["gpt-4o-flash"],
        "preview": ["gpt-4o-preview"],
        "base": ["gpt-4o-base"],
        "turbo": ["gpt-4o-turbo"],
        "plus": ["gpt-4o-plus"],
        "pro": ["gpt-4o-pro"],
        "ultra": ["gpt-4o-ultra"],
        "omni": ["gpt-4o"],
    },
    ModelFamily.GPT_4: {
        "base": ["gpt-4"],
    },
    ModelFamily.GPT_3_5: {
        "turbo": ["gpt-3.5-turbo"],
    },
    ModelFamily.GPT_4_1: {
        "mini": ["gpt-4.1-mini"],
        "nano": ["gpt-4.1-nano"],
        "base": ["gpt-4.1"],
        "turbo": ["gpt-4.1-turbo"],
        "plus": ["gpt-4.1-plus"],
        "pro": ["gpt-4.1-pro"],
        "ultra": ["gpt-4.1-ultra"],
        "omni": ["gpt-4.1-omni"],
    },
    ModelFamily.GPT_5: {
        "mini": ["gpt-5-mini"],
        "nano": ["gpt-5-nano"],
        "base": ["gpt-5"],
        "turbo": ["gpt-5-turbo"],
        "plus": ["gpt-5-plus"],
        "pro": ["gpt-5-pro"],
        "ultra": ["gpt-5-ultra"],
        "omni": ["gpt-5-omni"],
    },
    ModelFamily.O1: {
        "mini": ["o1-mini"],
        "flash": ["o1-flash"],
        "base": ["o1"],
        "turbo": ["o1-turbo"],
        "plus": ["o1-plus"],
        "pro": ["o1-pro"],
        "ultra": ["o1-ultra"],
        "omni": ["o1-omni"],
    },
    ModelFamily.O3: {
        "mini": ["o3-mini"],
        "base": ["o3"],
        "turbo": ["o3-turbo"],
        "plus": ["o3-plus"],
        "pro": ["o3-pro"],
        "deep-research": ["o3-deep-research"],
    },
    ModelFamily.O4: {
        "mini": ["o4-mini"],
        "mini-deep-research": ["o4-mini-deep-research"],
        "base": ["o4-base"],
        "turbo": ["o4-turbo"],
        "plus": ["o4-plus"],
        "pro": ["o4-pro"],
        "ultra": ["o4-ultra"],
        "omni": ["o4-omni"],
        "deep-research": ["o4-deep-research"],
    },
    ModelFamily.GLM_VISION: {
        "vision-flash": ["glm-4v-flash"],
        "preview": ["glm-4v-preview"],
        "base": ["glm-4v", "glm-4.5v"],
        "vision-plus": ["glm-4v-plus", "glm-4v-plus-0111"],
    },
    ModelFamily.GLM_TEXT: {
        "mini": ["glm-4-mini"],
        "flash": ["glm-4-flash", "glm-4.5-flash"],
        "preview": ["glm-4-preview"],
        "air": ["glm-4.5-air"],
        "airx": ["glm-4.5-airx"],
        "base": ["glm-4", "glm-4.5", "glm-4.6"],
        "x": ["glm-4.5-x"],
        "turbo": ["glm-4-turbo"],
        "plus": ["glm-4-plus"],
        "pro": ["glm-4-pro"],
        "ultra": ["glm-4-ultra"],
    },
    ModelFamily.GLM_3: {
        "mini": ["glm-3-mini"],
        "flash": ["glm-3-flash"],
        "base": ["glm-3"],
        "turbo": ["glm-3-turbo"],
        "plus": ["glm-3-plus"],
        "pro": ["glm-3-pro"],
    },
    ModelFamily.QWEN: {
        "mini": ["qwen3-mini"],
        "flash": ["qwen3-flash"],
        "preview": ["qwen3-preview"],
        "base": ["qwen3-base"],
        "turbo": ["qwen3-turbo"],
        "plus": ["qwen3-plus"],
        "pro": ["qwen3-pro"],
        "ultra": ["qwen3-ultra"],
        "omni": ["qwen3-omni"],
    },
    ModelFamily.CLAUDE: {
        "sonnet": [
            "claude-sonnet-4-5",
            "claude-sonnet-4-5-20250929",
            "claude-sonnet-4-5@20250929",
            "claude-3-7-sonnet-latest",
        ],
        "opus": [
            "claude-opus-4-1",
            "claude-opus-4-1-20250805",
            "claude-opus-4-1@20250805",
        ],
        "haiku": [
            "claude-haiku-4-5",
            "claude-haiku-4-5-20251001",
            "claude-haiku-4-5@20251001",
        ],
    },
    ModelFamily.ERNIE: {
        "mini": ["ernie-mini"],
        "flash": ["ernie-flash"],
        "preview": ["ernie-preview"],
        "base": ["ernie"],
        "turbo": ["ernie-turbo"],
        "plus": ["ernie-plus"],
        "pro": ["ernie-pro"],
        "ultra": ["ernie-ultra"],
        "omni": ["ernie-omni"],
    },
    ModelFamily.HUNYUAN: {
        "mini": ["hunyuan-mini"],
        "flash": ["hunyuan-flash"],
        "preview": ["hunyuan-preview"],
        "base": ["hunyuan"],
        "turbo": ["hunyuan-turbo"],
        "plus": ["hunyuan-plus"],
        "pro": ["hunyuan-pro"],
        "ultra": ["hunyuan-ultra"],
        "omni": ["hunyuan-omni"],
    },
    ModelFamily.MOONSHOT: {
        "mini": ["moonshot-mini"],
        "flash": ["moonshot-flash"],
        "preview": ["moonshot-preview"],
        "base": ["moonshot"],
        "turbo": ["moonshot-turbo"],
        "plus": ["moonshot-plus"],
        "pro": ["moonshot-pro"],
        "ultra": ["moonshot-ultra"],
        "omni": ["moonshot-omni"],
    },
    ModelFamily.DEEPSEEK: {
        "chat": ["deepseek-chat", "deepseek-chat-beta", "deepseek-chat-v3.2-exp"],
        "reasoner": ["deepseek-reasoner"],
    },
    ModelFamily.ABAB: {
        "mini": ["abab-mini"],
        "flash": ["abab-flash"],
        "preview": ["abab-preview"],
        "base": ["abab"],
        "turbo": ["abab-turbo"],
        "plus": ["abab-plus"],
        "pro": ["abab-pro"],
        "ultra": ["abab-ultra"],
        "omni": ["abab-omni"],
    },
}

PARAM_CASES = [
    (family, variant, sample)
    for family, mapping in MODEL_VARIANT_SAMPLES.items()
    for variant, samples in mapping.items()
    for sample in samples
]


def _resolve_expected_priority(
    sample_name: str,
    model_variant: str,
    family_config: ModelFamilyConfig,
) -> tuple[int, ...]:
    sample_lower = sample_name.lower()
    spec_config = family_config.specific_models.get(sample_lower)
    if spec_config and spec_config.variant_priority is not None:
        return spec_config.variant_priority

    # 尝试使用 specific_models 的子模式匹配样例名称，以获取显式 variant_priority
    import parse  # type: ignore[import-untyped]

    for config in family_config.specific_models.values():
        if not config.patterns or config.variant_priority is None:
            continue

        for sub_pattern in config.patterns:
            result = parse.parse(sub_pattern, sample_lower)
            if result is not None:
                return config.variant_priority

    if model_variant == family_config.variant_default and family_config.variant_priority_default is not None:
        return family_config.variant_priority_default

    return infer_variant_priority(model_variant)


@pytest.mark.parametrize("family, variant, sample_name", PARAM_CASES)
def test_variant_priority_alignment(family: ModelFamily, variant: str, sample_name: str) -> None:
    model = LLMeta(sample_name)

    assert model.family == family, f"'{sample_name}' 应该解析为家族 '{family.value}'，实际为 '{model.family.value}'"
    assert model.variant == variant, f"'{sample_name}' 解析出的型号应为 '{variant}'，实际为 '{model.variant}'"

    family_config = get_family_config(family)
    assert family_config is not None, f"家族 '{family.value}' 没有注册配置"

    expected_priority = _resolve_expected_priority(sample_name, model.variant, family_config)
    assert model._variant_priority == expected_priority, (
        "型号优先级不匹配: "
        f"family={family.value}, variant={model.variant}, "
        f"expected={expected_priority}, actual={model._variant_priority}"
    )
