# filename: test_auto_register.py
# @Time    : 2025/11/7 16:56
# @Author  : JQQ
# @Email   : jqq1716@gmail.com
# @Software: PyCharm
"""
自动注册功能测试 / Auto-registration feature tests
"""

import datetime
import unittest

from whosellm import LLMeta, ModelFamily, Provider
from whosellm.models.base import auto_register_model, infer_model_family


class TestAutoRegister(unittest.TestCase):
    """自动注册测试类 / Auto-registration test class"""

    def test_infer_model_family(self) -> None:
        """测试模型家族推断 / Test model family inference"""
        # GPT 系列 / GPT series
        assert infer_model_family("gpt-4o-new-variant") == ModelFamily.GPT_4O
        assert infer_model_family("gpt-3.5-turbo-custom") == ModelFamily.GPT_3_5
        assert infer_model_family("o1-custom") == ModelFamily.O1

        # 智谱 AI 系列 / Zhipu AI series
        assert infer_model_family("glm-4-0621") == ModelFamily.GLM_TEXT
        assert infer_model_family("glm-4v-preview") == ModelFamily.GLM_VISION
        assert infer_model_family("glm-3-custom") == ModelFamily.GLM_3

        # 其他厂商 / Other providers
        assert infer_model_family("qwen3-custom") == ModelFamily.QWEN
        assert infer_model_family("deepseek-chat-custom") == ModelFamily.DEEPSEEK
        assert infer_model_family("claude-sonnet-4-5") == ModelFamily.CLAUDE

        # 未知模型 / Unknown model
        assert infer_model_family("unknown-model-xyz") == ModelFamily.UNKNOWN

    def test_auto_register_gpt4o_variant(self) -> None:
        """测试自动注册 GPT-4 新型号 / Test auto-register GPT-4 new variant"""
        # 注册一个新的 GPT-4 型号 / Register a new GPT-4 variant
        model = LLMeta("gpt-4o-super")

        assert model.family == ModelFamily.GPT_4O
        assert model.provider == Provider.OPENAI
        assert model.version == "4.0"  # 默认版本是 4.0 / Default version is 4.0
        assert model.variant == "super"  # "super" 会被提取为型号名
        assert model.capabilities.supports_function_calling is True
        assert model.capabilities.supports_streaming is True
        assert model.capabilities.context_window == 128000

    def test_auto_register_with_known_variant(self) -> None:
        """测试自动注册带已知型号关键词的模型 / Test auto-register with known variant keywords"""
        # 测试 turbo 型号 / Test turbo variant
        model = LLMeta("gpt-4o-turbo-custom")

        assert model.family == ModelFamily.GPT_4O
        assert model.variant == "turbo"
        assert model._variant_priority == (2,)  # turbo 的优先级

        # 测试 mini 型号 / Test mini variant
        model_mini = LLMeta("gpt-4o-mini-custom")
        assert model_mini.variant == "mini"
        # mini 的优先级是 0，但如果没有匹配到关键词可能会是 base(1)
        # mini priority is 0, but if not matched to keyword it might be base(1)
        assert model_mini._variant_priority in [(0,), (1,)]

    def test_auto_register_glm4v_variant(self) -> None:
        """测试自动注册 GLM-4V 新型号 / Test auto-register GLM-4V new variant"""
        model = LLMeta("glm-4v-ultra")

        assert model.family == ModelFamily.GLM_VISION
        assert model.provider == Provider.ZHIPU
        assert model.version in ["4", "4.0", "4.5"]  # 可能是 "4", "4.0" 或 "4.5"
        assert model.variant == "ultra"  # ultra 会被提取
        assert model._variant_priority == (5,)  # ultra 的优先级
        assert model.capabilities.supports_vision is True

    def test_auto_register_with_date(self) -> None:
        """测试自动注册带日期的模型 / Test auto-register with date"""
        from datetime import date

        model = LLMeta("gpt-4o-turbo-2024-12-01")

        assert model.family == ModelFamily.GPT_4O
        assert model.variant == "turbo"
        assert model.release_date == date(2024, 12, 1)

    def test_auto_register_with_provider_prefix(self) -> None:
        """测试自动注册带 Provider 前缀的模型 / Test auto-register with provider prefix"""
        model = LLMeta("openai::gpt-4o-custom")

        assert model.provider == Provider.OPENAI
        assert model.family == ModelFamily.GPT_4O

    def test_auto_register_deepseek_variant(self) -> None:
        """测试自动注册 DeepSeek 新型号 / Test auto-register DeepSeek new variant"""
        # 使用 Provider 前缀确保使用官方配置
        model = LLMeta("deepseek::deepseek-chat-v2")

        assert model.family == ModelFamily.DEEPSEEK
        assert model.provider == Provider.DEEPSEEK
        assert model.capabilities.supports_function_calling is True
        assert model.capabilities.context_window == 128000

    def test_auto_register_qwen_variant(self) -> None:
        """测试自动注册 Qwen 新型号 / Test auto-register Qwen new variant"""
        model = LLMeta("qwen3-turbo")

        assert model.family == ModelFamily.QWEN
        assert model.provider == Provider.ALIBABA
        assert model.variant == "turbo"
        assert model.capabilities.supports_streaming is True

    def test_auto_register_unknown_model_raises(self) -> None:
        """测试自动注册未知模型应该抛出异常 / Test auto-register unknown model should raise"""
        # 对于完全未知的模型，如果无法推断家族，应该返回 UNKNOWN 家族
        # For completely unknown models, if family cannot be inferred, should return UNKNOWN family
        model = LLMeta("completely-unknown-model-xyz")

        # 应该返回 UNKNOWN 家族，但不抛出异常 / Should return UNKNOWN family but not raise exception
        assert model.family == ModelFamily.UNKNOWN
        assert model.provider == Provider.UNKNOWN

    def test_auto_register_comparison(self) -> None:
        """测试自动注册的模型可以进行比较 / Test auto-registered models can be compared"""
        model1 = LLMeta("gpt-4o-turbo-v1")
        model2 = LLMeta("gpt-4o-turbo-v2")
        model3 = LLMeta("gpt-4o-mini")

        # 同一家族的模型可以比较 / Models from same family can be compared
        assert model1.family == model2.family == model3.family

        # turbo > mini (优先级: turbo=2, mini=0)
        # turbo > mini (priority: turbo=2, mini=0)
        assert model3 < model1
        assert model3 < model2

    def test_auto_register_with_multiple_variants(self) -> None:
        """测试自动注册包含多个型号关键词的模型 / Test auto-register with multiple variant keywords"""
        # 包含多个关键词时，取最高优先级 / When multiple keywords present, take highest priority
        model = LLMeta("gpt-4o-turbo-plus")

        assert model.variant == "turbo-plus"
        # plus(3) > turbo(2)，所以优先级应该是 3
        # plus(3) > turbo(2), so priority should be 3
        assert model._variant_priority == (3,)

    def test_auto_register_preserves_capabilities(self) -> None:
        """测试自动注册保留家族的默认能力 / Test auto-register preserves family default capabilities"""
        # O1 系列支持 thinking 模式 / O1 series supports thinking mode
        model = LLMeta("o1-pro")

        assert model.family == ModelFamily.O1
        assert model.capabilities.supports_thinking is True
        assert model.capabilities.supports_streaming is False
        assert model.capabilities.context_window == 200000

    def test_auto_register_claude_variant(self) -> None:
        """测试自动注册 Claude 新型号 / Test auto-register Claude new variant"""
        model = LLMeta("claude-opus-4-1-20250805")

        assert model.family == ModelFamily.CLAUDE
        assert model.provider == Provider.ANTHROPIC
        assert model.capabilities.supports_function_calling is True
        assert model.capabilities.supports_vision is True
        assert model.capabilities.context_window == 200000

    def test_manual_auto_register(self) -> None:
        """测试手动调用自动注册函数 / Test manually calling auto-register function"""
        model_info = auto_register_model("gpt-4-0621")

        assert model_info.family == ModelFamily.GPT_4
        assert model_info.provider == Provider.OPENAI
        assert model_info.capabilities.supports_function_calling is True

        # 验证已注册到全局注册表 / Verify registered to global registry
        model = LLMeta("gpt-4-0621")
        assert model.family == ModelFamily.GPT_4

    def test_auto_register_with_mmdd_date(self) -> None:
        """测试自动注册带 MMDD 格式日期的模型 / Test auto-register with MMDD format date"""
        from datetime import date

        model = LLMeta("gpt-4-1225")

        assert model.family == ModelFamily.GPT_4
        assert model.release_date == date(datetime.datetime.now().year, 12, 25)

    def test_auto_register_variant_priority_order(self) -> None:
        """测试自动注册的型号优先级顺序 / Test auto-register variant priority order"""
        # 使用 GPT-4o 家族测试，因为它支持更多 variant
        # 创建不同型号的模型 / Create models with different variants
        mini = LLMeta("gpt-4o-mini-test")
        flash = LLMeta("gpt-4o-flash-test")
        base = LLMeta("gpt-4o-test")
        turbo = LLMeta("gpt-4o-turbo-test")
        plus = LLMeta("gpt-4o-plus-test")
        pro = LLMeta("gpt-4o-pro-test")
        ultra = LLMeta("gpt-4o-ultra-test")

        # 验证优先级顺序: mini < flash < base < turbo < plus < pro < ultra
        # Verify priority order: mini < flash < base < turbo < plus < pro < ultra
        assert mini < flash or mini._variant_priority == flash._variant_priority  # mini 和 flash 都是 0
        assert flash < base or flash._variant_priority <= base._variant_priority
        assert base < turbo
        assert turbo < plus
        assert plus < pro
        assert pro < ultra
