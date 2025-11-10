# filename: test_deepseek_tencent.py
# @Time    : 2025/11/9 16:58
# @Author  : Cascade AI
"""
腾讯云 DeepSeek 模型家族测试 / Tencent Cloud DeepSeek model family tests
"""

from whosellm.models.base import ModelFamily
from whosellm.models.registry import get_specific_model_config, match_model_pattern
from whosellm.provider import Provider


def test_tencent_deepseek_v3_0324() -> None:
    """测试腾讯云 DeepSeek-V3-0324 模型 / Test Tencent DeepSeek-V3-0324 model"""
    config = get_specific_model_config("deepseek-v3-0324")

    assert config is not None
    version, variant, capabilities = config
    assert version == "v3-0324"
    assert variant == "v3-0324"
    assert capabilities is not None
    assert capabilities.supports_function_calling is True
    assert capabilities.supports_streaming is True
    assert capabilities.max_tokens == 16000
    assert capabilities.context_window == 128000
    assert capabilities.supports_thinking is False


def test_tencent_deepseek_v3() -> None:
    """测试腾讯云 DeepSeek-V3 模型 / Test Tencent DeepSeek-V3 model"""
    config = get_specific_model_config("deepseek-v3")

    assert config is not None
    version, variant, capabilities = config
    assert version == "v3"
    assert variant == "v3"
    assert capabilities is not None
    assert capabilities.supports_function_calling is True
    assert capabilities.max_tokens == 16000
    assert capabilities.context_window == 64000


def test_tencent_deepseek_r1() -> None:
    """测试腾讯云 DeepSeek-R1 模型 / Test Tencent DeepSeek-R1 model"""
    config = get_specific_model_config("deepseek-r1")

    assert config is not None
    version, variant, capabilities = config
    assert version == "r1"
    assert variant == "r1"
    assert capabilities is not None
    assert capabilities.supports_thinking is True
    assert capabilities.supports_function_calling is True
    assert capabilities.max_tokens == 16000
    assert capabilities.context_window == 96000


def test_tencent_deepseek_r1_0528() -> None:
    """测试腾讯云 DeepSeek-R1-0528 模型 / Test Tencent DeepSeek-R1-0528 model"""
    config = get_specific_model_config("deepseek-r1-0528")

    assert config is not None
    version, variant, capabilities = config
    assert version == "r1-0528"
    assert variant == "r1-0528"
    assert capabilities is not None
    assert capabilities.supports_thinking is True
    assert capabilities.context_window == 128000


def test_tencent_deepseek_v3_1() -> None:
    """测试腾讯云 DeepSeek-V3.1 模型 / Test Tencent DeepSeek-V3.1 model"""
    config = get_specific_model_config("deepseek-v3.1")

    assert config is not None
    version, variant, capabilities = config
    assert version == "v3.1"
    assert variant == "v3.1"
    assert capabilities is not None
    assert capabilities.supports_thinking is True
    assert capabilities.max_tokens == 32000
    assert capabilities.context_window == 128000


def test_tencent_deepseek_v3_1_terminus() -> None:
    """测试腾讯云 DeepSeek-V3.1-Terminus 模型 / Test Tencent DeepSeek-V3.1-Terminus model"""
    config = get_specific_model_config("deepseek-v3.1-terminus")

    assert config is not None
    version, variant, capabilities = config
    assert version == "v3.1-terminus"
    assert variant == "v3.1-terminus"
    assert capabilities is not None
    assert capabilities.supports_thinking is True
    assert capabilities.max_tokens == 32000


def test_tencent_deepseek_v3_2_exp() -> None:
    """测试腾讯云 DeepSeek-V3.2-Exp 模型 / Test Tencent DeepSeek-V3.2-Exp model"""
    config = get_specific_model_config("deepseek-v3.2-exp")

    assert config is not None
    version, variant, capabilities = config
    assert version == "v3.2-exp"
    assert variant == "v3.2-exp"
    assert capabilities is not None
    assert capabilities.supports_thinking is True
    assert capabilities.max_tokens == 64000
    assert capabilities.context_window == 128000


def test_tencent_deepseek_pattern_matching() -> None:
    """测试腾讯云 DeepSeek 模式匹配 / Test Tencent DeepSeek pattern matching"""
    # 测试 V3 系列
    matched_v3 = match_model_pattern("deepseek-v3")
    assert matched_v3 is not None
    assert matched_v3["family"] == ModelFamily.DEEPSEEK
    assert matched_v3["variant"] == "v3"
    assert matched_v3["_from_specific_model"] == "deepseek-v3"

    # 测试 R1 系列
    matched_r1 = match_model_pattern("deepseek-r1")
    assert matched_r1 is not None
    assert matched_r1["family"] == ModelFamily.DEEPSEEK
    assert matched_r1["variant"] == "r1"
    assert matched_r1["capabilities"].supports_thinking is True

    # 测试 V3.1 系列
    matched_v31 = match_model_pattern("deepseek-v3.1")
    assert matched_v31 is not None
    assert matched_v31["variant"] == "v3.1"


def test_tencent_deepseek_provider_prefix() -> None:
    """测试使用 Provider 前缀访问腾讯云 DeepSeek / Test accessing Tencent DeepSeek with provider prefix"""
    from whosellm import LLMeta

    model = LLMeta("tencent::deepseek-v3")
    assert model.provider == Provider.TENCENT
    assert model.family == ModelFamily.DEEPSEEK
    assert model.version == "v3"
    assert model.variant == "base"


def test_tencent_deepseek_no_collision_with_official() -> None:
    """验证腾讯云 DeepSeek 不会与官方 DeepSeek 冲突 / Verify no collision between Tencent and official DeepSeek"""
    from whosellm import LLMeta

    # 官方 DeepSeek
    official_chat = LLMeta("deepseek::deepseek-chat")
    assert official_chat.provider == Provider.DEEPSEEK
    assert official_chat.variant == "chat"

    # 腾讯云 DeepSeek
    tencent_v3 = LLMeta("tencent::deepseek-v3")
    assert tencent_v3.provider == Provider.TENCENT
    assert tencent_v3.version == "v3"
    assert tencent_v3.variant == "base"

    # 不同的能力配置
    assert official_chat.capabilities.max_tokens == 8000
    assert tencent_v3.capabilities.max_tokens == 16000


def test_tencent_deepseek_invalid_model_names() -> None:
    """验证腾讯云不支持的 DeepSeek 模型名称会被识别为 UNKNOWN / Validate unsupported Tencent model names are recognized as UNKNOWN"""
    from whosellm import LLMeta

    # 腾讯云不支持 deepseek-chat 命名方式
    # 腾讯云使用 deepseek-v3, deepseek-r1 等版本号命名，不使用 chat/reasoner 等官方 variant
    model = LLMeta("tencent::deepseek-chat")

    # 当使用 Provider 前缀时，Provider 会被保留，但 family 会是 UNKNOWN
    # 即使 deepseek-chat 已经被注册到全局注册表，也不会影响 tencent:: 前缀的匹配
    assert model.family == ModelFamily.UNKNOWN
    assert model.provider == Provider.TENCENT
    assert model.variant == ""  # 无法匹配到任何 variant
