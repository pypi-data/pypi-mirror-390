# filename: test_o4.py
# @Time    : 2025/11/7 16:56
# @Author  : JQQ
# @Email   : jqq1716@gmail.com
# @Software: PyCharm
"""
O4 模型家族测试 / O4 model family tests
"""

from whosellm.models.base import ModelFamily
from whosellm.models.registry import get_default_capabilities, get_specific_model_config, match_model_pattern


def test_o4_family_defaults():
    """验证 O4 家族默认能力 / Validate O4 family default capabilities"""
    capabilities = get_default_capabilities(ModelFamily.O4)

    assert capabilities.supports_streaming is True
    assert capabilities.supports_function_calling is True
    assert capabilities.supports_structured_outputs is True
    assert capabilities.supports_fine_tuning is True
    assert capabilities.supports_distillation is False
    assert capabilities.supports_predicted_outputs is False


def _assert_specific(
    name: str,
    variant: str,
    *,
    streaming: bool,
    function_calling: bool,
    structured_outputs: bool,
    fine_tuning: bool,
) -> None:
    config = get_specific_model_config(name)

    assert config is not None
    version, cfg_variant, capabilities = config
    assert version == "4.0"
    assert cfg_variant == variant
    assert capabilities is not None
    assert capabilities.supports_streaming is streaming
    assert capabilities.supports_function_calling is function_calling
    assert capabilities.supports_structured_outputs is structured_outputs
    assert capabilities.supports_fine_tuning is fine_tuning
    assert capabilities.supports_distillation is False
    assert capabilities.supports_predicted_outputs is False


def test_o4_mini_capabilities():
    """验证 o4-mini 模型能力 / Validate o4-mini capabilities"""
    _assert_specific(
        "o4-mini",
        "mini",
        streaming=True,
        function_calling=True,
        structured_outputs=True,
        fine_tuning=True,
    )


def test_o4_mini_pattern_with_date():
    """验证带日期的 o4-mini 模式匹配 / Validate dated o4-mini pattern"""
    matched = match_model_pattern("o4-mini-2025-04-16")

    assert matched is not None
    assert matched["family"] == ModelFamily.O4
    assert matched["variant"] == "mini"
    assert matched["_from_specific_model"] == "o4-mini"


def test_o4_mini_deep_research_capabilities():
    """验证 o4-mini-deep-research 模型能力 / Validate o4-mini-deep-research capabilities"""
    _assert_specific(
        "o4-mini-deep-research",
        "mini-deep-research",
        streaming=True,
        function_calling=False,
        structured_outputs=False,
        fine_tuning=False,
    )


def test_o4_mini_deep_research_pattern_with_date():
    """验证带日期的 o4-mini-deep-research 模式匹配 / Validate dated o4-mini-deep-research pattern"""
    matched = match_model_pattern("o4-mini-deep-research-2025-06-26")

    assert matched is not None
    assert matched["family"] == ModelFamily.O4
    assert matched["variant"] == "mini-deep-research"
    assert matched["_from_specific_model"] == "o4-mini-deep-research"
