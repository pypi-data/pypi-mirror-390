# filename: test_deepseek.py
# @Time    : 2025/11/9 16:08
# @Author  : Cascade AI
"""
DeepSeek 模型家族测试 / DeepSeek model family tests
"""

from whosellm.models.base import ModelFamily
from whosellm.models.registry import get_specific_model_config
from whosellm.provider import Provider


def test_deepseek_default_capabilities() -> None:
    """验证 DeepSeek 官方家族默认能力 / Validate DeepSeek official family default capabilities"""
    from whosellm import LLMeta

    # 使用官方 Provider 前缀确保获取官方配置
    model = LLMeta("deepseek::deepseek-chat")
    capabilities = model.capabilities

    assert capabilities.supports_streaming is True
    assert capabilities.supports_function_calling is True
    assert capabilities.max_tokens == 8000
    assert capabilities.context_window == 128000
    assert capabilities.supports_thinking is False


def test_deepseek_chat_specific_model() -> None:
    """验证 deepseek-chat 特定模型配置 / Validate deepseek-chat specific configuration"""
    config = get_specific_model_config("deepseek-chat")

    assert config is not None
    version, variant, capabilities = config
    assert version == "1.0"
    assert variant == "chat"
    assert capabilities is not None
    assert capabilities.supports_function_calling is True
    assert capabilities.supports_streaming is True
    assert capabilities.max_tokens == 8000
    assert capabilities.context_window == 128000


def test_deepseek_chat_pattern_matching() -> None:
    """验证 deepseek-chat 模式匹配 / Validate deepseek-chat pattern matching"""
    from whosellm import LLMeta

    for name in ["deepseek-chat", "deepseek-chat-beta", "deepseek-chat-v3.2-exp"]:
        # 使用 Provider 前缀确保匹配官方配置
        model = LLMeta(f"deepseek::{name}")

        assert model.family == ModelFamily.DEEPSEEK
        assert model.variant == "chat"
        assert model.version == "1.0"
        assert model.provider == Provider.DEEPSEEK


def test_deepseek_reasoner_specific_model() -> None:
    """验证 deepseek-reasoner 特定模型配置 / Validate deepseek-reasoner specific configuration"""
    config = get_specific_model_config("deepseek-reasoner")

    assert config is not None
    version, variant, capabilities = config
    assert version == "1.0"
    assert variant == "reasoner"
    assert capabilities is not None
    assert capabilities.supports_thinking is True


def test_deepseek_base_pattern_without_variant() -> None:
    """验证无型号名称时的默认匹配 / Validate default match without explicit variant"""
    from whosellm import LLMeta

    # 使用 Provider 前缀确保匹配官方配置
    # DeepSeek 官方只支持 chat 和 reasoner，默认使用 chat
    model = LLMeta("deepseek::deepseek-chat")

    assert model.family == ModelFamily.DEEPSEEK
    assert model.variant == "chat"
    assert model.version == "1.0"
    assert model.capabilities.supports_function_calling is True


def test_deepseek_reasoner_does_not_use_chat_capabilities() -> None:
    """验证 reasoner 不会意外继承 chat 的函数调用能力 / Ensure reasoner capabilities override family defaults"""
    from whosellm import LLMeta

    model = LLMeta("deepseek::deepseek-reasoner")

    assert model.variant == "reasoner"
    assert model.capabilities.supports_function_calling is True
    assert model.capabilities.supports_thinking is True


def test_deepseek_official_invalid_model_names() -> None:
    """验证 DeepSeek 官方不支持的模型名称会被识别为 UNKNOWN / Validate unsupported official model names are recognized as UNKNOWN"""
    from whosellm import LLMeta

    # DeepSeek 官方不提供 deepseek-v3.2-exp 这样的命名方式
    # 官方只支持 deepseek-chat-{suffix} 和 deepseek-reasoner-{suffix}
    model = LLMeta("deepseek::deepseek-v3.2-exp")

    # 当使用 Provider 前缀时，Provider 会被保留，但 family 会是 UNKNOWN
    assert model.family == ModelFamily.UNKNOWN
    assert model.provider == Provider.DEEPSEEK
    assert model.variant == ""  # 无法匹配到任何 variant
