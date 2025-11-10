# filename: test_o3.py
# @Time    : 2025/11/7 16:56
# @Author  : JQQ
# @Email   : jqq1716@gmail.com
# @Software: PyCharm
"""
O3 模型家族测试 / O3 model family tests
"""

from whosellm.models.base import ModelFamily
from whosellm.models.registry import get_default_capabilities, get_specific_model_config, match_model_pattern


def test_o3_base_defaults():
    """验证 O3 家族默认能力 / Validate O3 family default capabilities"""
    capabilities = get_default_capabilities(ModelFamily.O3)

    assert capabilities.supports_streaming is True
    assert capabilities.supports_function_calling is True
    assert capabilities.supports_structured_outputs is True
    assert capabilities.supports_fine_tuning is False
    assert capabilities.supports_distillation is False
    assert capabilities.supports_predicted_outputs is False


def _assert_specific_config(
    name: str,
    variant: str,
    *,
    streaming: bool,
    function_calling: bool,
    structured_outputs: bool,
) -> None:
    config = get_specific_model_config(name)

    assert config is not None
    version, cfg_variant, capabilities = config
    assert version == "3.0"
    assert cfg_variant == variant
    assert capabilities is not None
    assert capabilities.supports_streaming is streaming
    assert capabilities.supports_function_calling is function_calling
    assert capabilities.supports_structured_outputs is structured_outputs
    assert capabilities.supports_fine_tuning is False
    assert capabilities.supports_distillation is False
    assert capabilities.supports_predicted_outputs is False


def test_o3_base_specific_model():
    """验证 o3 基础模型能力 / Validate o3 base model capabilities"""
    _assert_specific_config(
        "o3",
        "base",
        streaming=True,
        function_calling=True,
        structured_outputs=True,
    )


def test_o3_base_with_date_pattern():
    """验证带日期的 o3 模型匹配 / Validate dated o3 model pattern"""
    matched = match_model_pattern("o3-2025-04-16")

    assert matched is not None
    assert matched["family"] == ModelFamily.O3
    assert matched["_from_specific_model"] == "o3"
    assert matched["variant"] == "base"


def test_o3_mini_specific_model():
    """验证 o3-mini 模型能力 / Validate o3-mini model capabilities"""
    _assert_specific_config(
        "o3-mini",
        "mini",
        streaming=True,
        function_calling=True,
        structured_outputs=True,
    )


def test_o3_mini_with_date_pattern():
    """验证带日期的 o3-mini 模型匹配 / Validate dated o3-mini model pattern"""
    matched = match_model_pattern("o3-mini-2025-01-31")

    assert matched is not None
    assert matched["family"] == ModelFamily.O3
    assert matched["_from_specific_model"] == "o3-mini"
    assert matched["variant"] == "mini"


def test_o3_pro_specific_model():
    """验证 o3-pro 模型能力 / Validate o3-pro model capabilities"""
    _assert_specific_config(
        "o3-pro",
        "pro",
        streaming=False,
        function_calling=True,
        structured_outputs=True,
    )


def test_o3_pro_with_date_pattern():
    """验证带日期的 o3-pro 模型匹配 / Validate dated o3-pro model pattern"""
    matched = match_model_pattern("o3-pro-2025-06-10")

    assert matched is not None
    assert matched["family"] == ModelFamily.O3
    assert matched["_from_specific_model"] == "o3-pro"
    assert matched["variant"] == "pro"


def test_o3_deep_research_specific_model():
    """验证 o3-deep-research 模型能力 / Validate o3-deep-research model capabilities"""
    _assert_specific_config(
        "o3-deep-research",
        "deep-research",
        streaming=True,
        function_calling=False,
        structured_outputs=False,
    )


def test_o3_deep_research_with_date_pattern():
    """验证带日期的 o3-deep-research 模型匹配 / Validate dated o3-deep-research model pattern"""
    matched = match_model_pattern("o3-deep-research-2025-06-26")

    assert matched is not None
    assert matched["family"] == ModelFamily.O3
    assert matched["_from_specific_model"] == "o3-deep-research"
    assert matched["variant"] == "deep-research"
