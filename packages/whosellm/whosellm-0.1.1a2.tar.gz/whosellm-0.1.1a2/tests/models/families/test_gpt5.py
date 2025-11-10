# filename: test_gpt5.py
# @Time    : 2025/11/7 16:56
# @Author  : JQQ
# @Email   : jqq1716@gmail.com
# @Software: PyCharm
"""
GPT-5 模型家族测试 / GPT-5 model family tests
"""

from datetime import date

import pytest

from whosellm.models.base import ModelFamily
from whosellm.models.registry import get_specific_model_config, match_model_pattern


def test_gpt5_base_model():
    """测试基础GPT-5模型 / Test base GPT-5 model"""
    # 使用match_model_pattern获取模型信息
    matched = match_model_pattern("gpt-5")

    assert matched is not None
    assert matched["family"] == ModelFamily.GPT_5
    assert matched["version"] == "5.0"
    assert matched["variant"] == "base"

    # 验证特定配置
    config = get_specific_model_config("gpt-5-mini")
    assert config is not None
    version, variant, capabilities = config
    assert version == "5.0"
    assert variant == "mini"
    assert capabilities is not None
    assert capabilities.max_tokens == 8192
    assert capabilities.context_window == 128000


def test_gpt5_mini_model():
    """测试GPT-5 mini变体 / Test GPT-5 mini variant"""
    config = get_specific_model_config("gpt-5-mini")
    assert config is not None
    version, variant, capabilities = config
    assert version == "5.0"
    assert variant == "mini"
    assert capabilities.max_tokens == 8192
    assert capabilities.context_window == 128000


def test_gpt5_nano_model():
    """测试GPT-5 nano变体 / Test GPT-5 nano variant"""
    config = get_specific_model_config("gpt-5-nano")
    assert config is not None
    version, variant, capabilities = config
    assert version == "5.0"
    assert variant == "nano"
    assert capabilities.max_tokens == 4096
    assert capabilities.context_window == 64000


def test_gpt5_with_date_suffix():
    """测试带日期后缀的GPT-5模型 / Test GPT-5 model with date suffix"""
    matched = match_model_pattern("gpt-5-mini-2025-08-07")
    assert matched is not None
    assert matched["variant"] == "mini"

    # 检查日期解析
    from whosellm.models.base import parse_date_from_model_name

    parsed_date = parse_date_from_model_name("gpt-5-mini-2025-08-07")
    assert parsed_date == date(2025, 8, 7)


def test_gpt5_pro_model():
    """测试GPT-5 Pro变体 / Test GPT-5 pro variant"""
    config = get_specific_model_config("gpt-5-pro")
    assert config is not None
    version, variant, capabilities = config
    assert version == "5.0"
    assert variant == "pro"
    assert capabilities.max_tokens == 24576
    assert capabilities.context_window == 256000


def test_gpt5_pro_with_date_suffix():
    """测试带日期的GPT-5 Pro模型 / Test GPT-5 pro with date suffix"""
    matched = match_model_pattern("gpt-5-pro-2025-10-06")
    assert matched is not None
    assert matched["variant"] == "pro"

    # 检查日期解析
    from whosellm.models.base import parse_date_from_model_name

    parsed_date = parse_date_from_model_name("gpt-5-pro-2025-10-06")
    assert parsed_date == date(2025, 10, 6)


@pytest.mark.parametrize(
    "model_name,expected_tokens",
    [
        ("gpt-5-mini", 8192),
        ("gpt-5-nano", 4096),
        ("gpt-5-pro", 24576),
        ("gpt-5-mini-2025-08-07", 8192),
        ("gpt-5-pro-2025-10-06", 24576),
    ],
)
def test_gpt5_max_tokens(model_name, expected_tokens):
    """参数化测试GPT-5各型号的max_tokens / Parametrized test for GPT-5 max_tokens"""
    config = get_specific_model_config(model_name)
    if config is None:
        matched = match_model_pattern(model_name)
        config = get_specific_model_config(matched["_from_specific_model"])

    assert config is not None
    assert config[2].max_tokens == expected_tokens
