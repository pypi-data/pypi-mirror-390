"""GLM-4.5V 模型家族测试 / GLM-4.5V model family tests."""

from datetime import date

from whosellm.models.base import ModelFamily, parse_date_from_model_name
from whosellm.models.registry import get_default_capabilities, match_model_pattern


def test_glm45v_default_capabilities() -> None:
    """验证 GLM-4.5V 家族默认能力 / Validate GLM-4.5V family default capabilities"""
    capabilities = get_default_capabilities(ModelFamily.GLM_VISION)

    assert capabilities.supports_thinking is True
    assert capabilities.supports_vision is True
    assert capabilities.supports_video is True
    assert capabilities.supports_pdf is True
    assert capabilities.supports_streaming is True
    assert capabilities.max_tokens == 8192
    assert capabilities.context_window == 64000


def test_glm45v_base_pattern() -> None:
    """验证基础 GLM-4.5V 模型匹配 / Validate base GLM-4.5V pattern"""
    matched = match_model_pattern("glm-4.5v")

    assert matched is not None
    assert matched["family"] == ModelFamily.GLM_VISION
    assert matched["variant"] == "base"
    assert matched["version"] == "4.5"
    assert matched["capabilities"].supports_vision is True


def test_glm45v_mmdd_pattern() -> None:
    """验证基础模型的 MMDD 后缀模式 / Validate base MMDD suffix pattern"""
    model_name = "glm-4.5v-1201"
    matched = match_model_pattern(model_name)

    assert matched is not None
    assert matched["family"] == ModelFamily.GLM_VISION
    assert matched["variant"] == "base"

    parsed = parse_date_from_model_name(model_name)
    assert parsed is not None
    assert parsed.month == 12
    assert parsed.day == 1


def test_glm45v_variant_full_date_pattern() -> None:
    """验证变体带完整日期的模式 / Validate variant with YYYY-MM-DD pattern"""
    model_name = "glm-4.5v-plus-2025-11-08"
    matched = match_model_pattern(model_name)

    assert matched is not None
    assert matched["family"] == ModelFamily.GLM_VISION
    assert matched["variant"] == "plus"
    assert matched["version"] == "4.5"

    parsed = parse_date_from_model_name(model_name)
    assert parsed == date(2025, 11, 8)
