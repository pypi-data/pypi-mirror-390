"""GLM-4.5 文本模型元数据测试 / Metadata tests for GLM-4.5 series."""

from datetime import date

from whosellm import LLMeta, ModelFamily, Provider


def test_glm45_base_capabilities() -> None:
    """验证 GLM-4.5 默认型号的能力配置。"""
    model = LLMeta("glm-4.5")

    assert model.provider == Provider.ZHIPU
    assert model.family == ModelFamily.GLM_TEXT
    assert model.variant == "base"

    capabilities = model.capabilities
    assert capabilities.supports_thinking is True
    assert capabilities.supports_function_calling is True
    assert capabilities.supports_structured_outputs is True
    assert capabilities.supports_streaming is True
    assert capabilities.supports_vision is False
    assert capabilities.supports_video is False
    assert capabilities.max_tokens == 96000
    assert capabilities.context_window == 128000


def test_glm45_variant_priority_order() -> None:
    """确认不同变体的优先级顺序符合产品定位。"""
    flash = LLMeta("glm-4.5-flash")
    air = LLMeta("glm-4.5-air")
    airx = LLMeta("glm-4.5-airx")
    base = LLMeta("glm-4.5")
    x = LLMeta("glm-4.5-x")

    assert flash.variant == "flash"
    assert air.variant == "air"
    assert airx.variant == "airx"
    assert base.variant == "base"
    assert x.variant == "x"

    assert flash < air < airx < base < x


def test_glm45_release_date_parsing() -> None:
    """确保带日期后缀的模型能够正确解析发布日期。"""
    model = LLMeta("glm-4.5-air-2025-11-08")

    assert model.family == ModelFamily.GLM_TEXT
    assert model.variant == "air"
    assert model.release_date == date(2025, 11, 8)


def test_glm46_capabilities() -> None:
    """验证 GLM-4.6 默认能力满足官方描述。"""
    model = LLMeta("glm-4.6")

    assert model.provider == Provider.ZHIPU
    assert model.family == ModelFamily.GLM_TEXT
    assert model.variant == "base"

    capabilities = model.capabilities
    assert capabilities.supports_thinking is True
    assert capabilities.supports_function_calling is True
    assert capabilities.supports_structured_outputs is True
    assert capabilities.supports_streaming is True
    assert capabilities.supports_vision is False
    assert capabilities.supports_video is False
    assert capabilities.context_window == 200000
    assert capabilities.max_tokens == 128000


def test_glm46_version_upgrade_over_glm45() -> None:
    """确认 GLM-4.6 相较 GLM-4.5 视为更高版本。"""
    glm45 = LLMeta("glm-4.5")
    glm46 = LLMeta("glm-4.6")

    assert glm45 < glm46


def test_glm46_release_date_parsing() -> None:
    """确保 GLM-4.6 带日期后缀能解析发布日期。"""
    model = LLMeta("glm-4.6-2025-11-08")

    assert model.family == ModelFamily.GLM_TEXT
    assert model.variant == "base"
    assert model.release_date == date(2025, 11, 8)
