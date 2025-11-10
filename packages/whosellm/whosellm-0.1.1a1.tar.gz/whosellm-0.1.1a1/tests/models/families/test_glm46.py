# filename: test_glm46.py
# @Time    : 2025/11/7 16:56
# @Author  : JQQ
# @Email   : jqq1716@gmail.com
# @Software: PyCharm
"""GLM-4.6 模型家族测试 / GLM-4.6 model family tests."""

from datetime import date

from whosellm.models.base import ModelFamily, parse_date_from_model_name
from whosellm.models.registry import get_default_capabilities, match_model_pattern


def test_glm46_default_capabilities() -> None:
    """验证 GLM-4.6 家族默认能力 / Validate GLM-4.6 family default capabilities"""
    capabilities = get_default_capabilities(ModelFamily.GLM_TEXT)

    assert capabilities.supports_thinking is True
    assert capabilities.supports_function_calling is True
    assert capabilities.supports_streaming is True
    assert capabilities.supports_structured_outputs is True
    assert capabilities.max_tokens == 128000
    assert capabilities.context_window == 200000


def test_glm46_base_model_pattern() -> None:
    """验证基础 GLM-4.6 模型匹配 / Validate base GLM-4.6 model pattern"""
    matched = match_model_pattern("glm-4.6")

    assert matched is not None
    assert matched["family"] == ModelFamily.GLM_TEXT
    assert matched["provider"].value == "zhipu"
    assert matched["variant"] == "base"
    assert matched["version"] == "4.6"
    assert matched["capabilities"].supports_thinking is True


def test_glm46_with_mmdd_suffix() -> None:
    """验证带日期后缀的基础模式 / Validate base pattern with MMDD suffix"""
    model_name = "glm-4.6-0815"
    matched = match_model_pattern(model_name)

    assert matched is not None
    assert matched["family"] == ModelFamily.GLM_TEXT
    assert matched["variant"] == "base"
    assert matched["version"] == "4.6"

    parsed_date = parse_date_from_model_name(model_name)
    assert parsed_date is not None
    assert parsed_date.month == 8
    assert parsed_date.day == 15


def test_glm46_variant_with_mmdd_suffix() -> None:
    """验证带变体与日期的匹配优先级 / Validate variant + MMDD pattern priority"""
    model_name = "glm-4.6-plus-0110"
    matched = match_model_pattern(model_name)

    assert matched is not None
    assert matched["family"] == ModelFamily.GLM_TEXT
    assert matched["variant"] == "plus"
    assert matched["version"] == "4.6"
    assert matched.get("_from_specific_model") is None
    assert matched["variant_priority"] is None


def test_glm46_variant_with_full_date() -> None:
    """验证带完整日期的变体模式 / Validate variant + YYYY-MM-DD pattern"""
    model_name = "glm-4.6-pro-2025-11-08"
    matched = match_model_pattern(model_name)

    assert matched is not None
    assert matched["family"] == ModelFamily.GLM_TEXT
    assert matched["variant"] == "pro"
    assert matched["version"] == "4.6"

    parsed_date = parse_date_from_model_name(model_name)
    assert parsed_date == date(2025, 11, 8)
