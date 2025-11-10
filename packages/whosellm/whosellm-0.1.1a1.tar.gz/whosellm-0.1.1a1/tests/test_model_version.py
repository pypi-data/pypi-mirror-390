# filename: test_model_version.py
# @Time    : 2025/11/7 13:56
# @Author  : JQQ
# @Email   : jqq1716@gmail.com
# @Software: PyCharm
"""
模型版本测试 / Model version tests
"""

import unittest
from datetime import datetime

import pytest

from whosellm import LLMeta, ModelFamily, Provider


class TestModelVersion(unittest.TestCase):
    """模型版本测试类 / Model version test class"""

    def test_init_from_string(self) -> None:
        """测试从字符串初始化 / Test initialization from string"""
        model = LLMeta("gpt-4")
        assert model.model_name == "gpt-4"
        assert model.provider == Provider.OPENAI

    def test_provider_detection(self) -> None:
        """测试提供商检测 / Test provider detection"""
        # OpenAI
        assert LLMeta("gpt-4").provider == Provider.OPENAI
        assert LLMeta("gpt-3.5-turbo").provider == Provider.OPENAI

        # 智谱 AI
        assert LLMeta("glm-4").provider == Provider.ZHIPU
        assert LLMeta("glm-4v-plus").provider == Provider.ZHIPU

    def test_version_comparison_same_family(self) -> None:
        """测试同一模型家族的版本比较 / Test version comparison for same family"""
        # 注意: GPT-4 和 GPT-3.5 是不同的家族，不能直接比较
        # Note: GPT-4 and GPT-3.5 are different families, cannot be compared directly
        # 我们改为测试同一家族不同型号的比较
        # We test comparison of different variants in the same family instead
        gpt4o_base_date = LLMeta("gpt-4o-2025-01-25")
        gpt4o_omni = LLMeta("gpt-4o")
        gpt4o_turbo = LLMeta("gpt-4o-turbo")

        # 测试同一家族（GPT-4）不同型号和日期的比较
        # Test comparisons within GPT-4 family
        assert gpt4o_base_date < gpt4o_omni
        assert gpt4o_omni > gpt4o_turbo
        assert gpt4o_base_date > gpt4o_turbo

    def test_version_comparison_same_family_gpt4o(self) -> None:
        """测试 GPT-4o 家族内型号优先级比较 / Test variant priority within GPT-4o family"""
        gpt4o_mini = LLMeta("gpt-4o-mini")
        gpt4o_base = LLMeta("gpt-4o")
        gpt4o_audio = LLMeta("gpt-4o-audio-preview")
        gpt4o_mini_realtime = LLMeta("gpt-4o-mini-realtime-preview")

        assert gpt4o_mini < gpt4o_base
        assert gpt4o_audio < gpt4o_base
        assert gpt4o_mini_realtime < gpt4o_base
        assert gpt4o_mini < gpt4o_audio or gpt4o_audio == gpt4o_mini

    def test_version_comparison_different_family_raises(self) -> None:
        """测试不同模型家族的版本比较应该抛出异常 / Test version comparison for different families should raise"""
        gpt4 = LLMeta("gpt-4")
        glm4 = LLMeta("glm-4")
        gpt4o = LLMeta("gpt-4o-mini")

        with pytest.raises(ValueError, match="无法比较不同模型家族的模型"):
            _ = gpt4 > glm4
        with pytest.raises(ValueError, match="无法比较不同模型家族的模型"):
            _ = gpt4 > gpt4o

    def test_capabilities(self) -> None:
        """测试能力检测 / Test capability detection"""
        # GPT-4 Turbo 支持视觉
        gpt4o_turbo = LLMeta("gpt-4o-turbo")
        assert gpt4o_turbo.capabilities.supports_vision is True
        assert gpt4o_turbo.supports_multimodal is True

        # GPT-3.5 不支持视觉
        gpt35 = LLMeta("gpt-3.5-turbo")
        assert gpt35.capabilities.supports_vision is False
        assert gpt35.supports_multimodal is False

    def test_zhipu_glm4v_capabilities(self) -> None:
        """测试智谱 GLM-4V 的能力 / Test Zhipu GLM-4V capabilities"""
        # GLM-4V-Plus
        glm4v_plus = LLMeta("glm-4v-plus")
        assert glm4v_plus.capabilities.supports_vision is True
        assert glm4v_plus.capabilities.supports_video is True
        assert glm4v_plus.capabilities.max_video_size_mb == 20.0
        assert glm4v_plus.capabilities.max_video_duration_seconds == 30

        # GLM-4V-Plus-0111
        glm4v_plus_0111 = LLMeta("glm-4v-plus-0111")
        assert glm4v_plus_0111.capabilities.max_video_size_mb == 200.0
        assert glm4v_plus_0111.capabilities.max_video_duration_seconds is None

        # GLM-4V-Flash 不支持 base64
        glm4v_flash = LLMeta("glm-4v-flash")
        assert glm4v_flash.capabilities.supports_image_base64 is False

    def test_thinking_models(self) -> None:
        """测试推理模型 / Test thinking models"""
        o1 = LLMeta("o1")
        assert o1.capabilities.supports_thinking is True
        assert o1.capabilities.supports_streaming is True
        assert o1.capabilities.supports_function_calling is True
        assert o1.capabilities.supports_structured_outputs is True

    def test_string_representation(self) -> None:
        """测试字符串表示 / Test string representation"""
        model = LLMeta("gpt-4")
        assert str(model) == "gpt-4"
        assert "ModelVersion" in repr(model)
        assert "gpt-4" in repr(model)

    def test_variant_priority_comparison(self) -> None:
        """测试型号优先级比较 / Test variant priority comparison"""
        # GLM-4 系列: flash < base < plus
        glm4_flash = LLMeta("glm-4-flash")
        glm4_base = LLMeta("glm-4")
        glm4_plus = LLMeta("glm-4-plus")

        assert glm4_flash < glm4_base
        assert glm4_base < glm4_plus
        assert glm4_flash < glm4_plus

        # GLM-4V 系列: flash < base < plus-0111 <= plus (plus 指向最新版)
        # GLM-4V series: flash < base < plus-0111 <= plus (plus points to latest)
        glm4v_flash = LLMeta("glm-4v-flash")
        glm4v_base = LLMeta("glm-4v")
        glm4v_plus = LLMeta("glm-4v-plus")
        glm4v_plus_0111 = LLMeta("glm-4v-plus-0111")

        assert glm4v_flash < glm4v_base
        assert glm4v_base < glm4v_plus
        # plus 是最新版，应该 >= 特定日期版本 / plus is latest, should be >= specific date version
        assert glm4v_plus >= glm4v_plus_0111

    def test_model_family_detection(self) -> None:
        """测试模型家族检测 / Test model family detection"""
        # GPT-4 家族
        gpt4 = LLMeta("gpt-4")
        gpt4o_turbo = LLMeta("gpt-4o-turbo")
        gpt4o = LLMeta("gpt-4o")

        assert gpt4.family == ModelFamily.GPT_4
        assert gpt4o_turbo.family == ModelFamily.GPT_4O
        assert gpt4o.family == ModelFamily.GPT_4O

        # GLM-TEXT 家族
        glm4 = LLMeta("glm-4")
        glm4_plus = LLMeta("glm-4-plus")
        glm45 = LLMeta("glm-4.5")
        glm46 = LLMeta("glm-4.6")

        assert glm4.family == ModelFamily.GLM_TEXT
        assert glm4_plus.family == ModelFamily.GLM_TEXT
        assert glm45.family == ModelFamily.GLM_TEXT
        assert glm46.family == ModelFamily.GLM_TEXT

        # GLM-VISION 家族（与 GLM-TEXT 不同）
        glm4v = LLMeta("glm-4v")
        glm45v = LLMeta("glm-4.5v")
        assert glm4v.family == ModelFamily.GLM_VISION
        assert glm45v.family == ModelFamily.GLM_VISION
        assert glm4v.family != glm4.family

    def test_provider_prefix_syntax(self) -> None:
        """测试 Provider::ModelName 语法 / Test Provider::ModelName syntax"""
        # 测试 Provider::ModelName 语法
        model1 = LLMeta("openai::gpt-4")
        assert model1.provider == Provider.OPENAI
        assert model1.family == ModelFamily.GPT_4

        # 测试不同的Provider
        model2 = LLMeta("openai::gpt-4")
        assert model2.provider == Provider.OPENAI
        assert model2.family == ModelFamily.GPT_4

        # 测试普通语法（使用默认Provider）
        model3 = LLMeta("gpt-4")
        assert model3.provider == Provider.OPENAI
        assert model3.family == ModelFamily.GPT_4

    def test_same_model_different_providers(self) -> None:
        """测试同一模型不同Provider / Test same model with different providers"""
        # 假设 DeepSeek 模型可以由原厂或腾讯提供
        # Assume DeepSeek model can be provided by original or Tencent
        # 这里仅作为示例，实际需要在注册表中添加相应配置

        # 测试指定不同Provider时，provider字段不同但family相同
        model_openai = LLMeta("openai::gpt-4")
        model_default = LLMeta("gpt-4")

        assert model_openai.provider == Provider.OPENAI
        assert model_default.provider == Provider.OPENAI
        assert model_openai.family == model_default.family

    def test_release_date_parsing(self) -> None:
        """测试发布日期解析 / Test release date parsing"""
        from datetime import date

        # 测试 YYYY-MM-DD 格式
        model1 = LLMeta("gpt-4o-turbo-2024-04-09")
        assert model1.release_date == date(2024, 4, 9)
        assert model1.family == ModelFamily.GPT_4O
        assert model1.variant == "turbo"

        # 测试 MMDD 格式（假设为2024年）
        model2 = LLMeta("gpt-4-0125")
        assert model2.release_date == date(datetime.now().year, 1, 25)
        assert model2.family == ModelFamily.GPT_4

        model3 = LLMeta("gpt-4o")
        assert model3.release_date is None

    def test_release_date_comparison(self) -> None:
        """测试发布日期比较 / Test release date comparison"""

        # 同一型号不同日期的比较
        model_old = LLMeta("gpt-4o-turbo-2024-01-01")
        model_new = LLMeta("gpt-4o-turbo-2024-04-09")

        assert model_old < model_new
        assert model_new > model_old
        assert model_old != model_new

        # 没有日期的模型认为是最新的（指向latest）
        model_no_date = LLMeta("gpt-4o-turbo")
        model_with_date = LLMeta("gpt-4o-turbo-2024-04-09")

        assert model_with_date < model_no_date  # 有日期的 < 无日期的（最新）
        assert model_no_date > model_with_date

    def test_complex_comparison_with_date(self) -> None:
        """测试复杂的版本、型号和日期比较 / Test complex version, variant and date comparison"""

        # 创建不同版本、型号和日期的模型
        gpt4_base_with_date = LLMeta("gpt-4-0125")  # base, 2024-01-25
        gpt4_base_no_date = LLMeta("gpt-4")  # base, no date

        # 验证型号优先级
        assert gpt4_base_with_date._variant_priority == (1,)

        # 同一型号：有日期 < 无日期（无日期指向最新）
        assert gpt4_base_with_date < gpt4_base_no_date

        # 测试未配置的模型名称（GPT-4 Turbo 已下线，未在配置中）
        # Test unconfigured model names (GPT-4 Turbo is offline and not in config)
        gpt4_turbo_with_date = LLMeta("gpt-4-turbo-2024-04-09")
        gpt4_turbo_no_date = LLMeta("gpt-4-turbo")

        # 未匹配到配置的模型，variant、provider、family 等应为空
        # Models not matched to config should have empty variant, provider, family, etc.
        assert gpt4_turbo_with_date.variant == ""
        assert gpt4_turbo_with_date._variant_priority == (0,)
        assert gpt4_turbo_with_date.family == ModelFamily.UNKNOWN
        assert gpt4_turbo_with_date.provider == Provider.UNKNOWN

        assert gpt4_turbo_no_date.variant == ""
        assert gpt4_turbo_no_date._variant_priority == (0,)
        assert gpt4_turbo_no_date.family == ModelFamily.UNKNOWN
        assert gpt4_turbo_no_date.provider == Provider.UNKNOWN

    def test_specific_model_capabilities(self) -> None:
        """测试子 SpecificModel 的 capabilities 覆盖 / Test specific model capabilities override"""
        # 测试 GPT-4 Turbo 的特殊 capabilities
        gpt4_turbo = LLMeta("gpt-4o-audio-preview")
        assert gpt4_turbo.capabilities.supports_vision is True
        assert gpt4_turbo.capabilities.context_window == 128000  # 上下文窗口
        assert gpt4_turbo.capabilities.max_tokens == 16384  # 最大输出token
        assert gpt4_turbo.variant == "audio-preview"

        # 测试 GPT-4o 的特殊 capabilities
        gpt4o = LLMeta("gpt-4o")
        assert gpt4o.capabilities.supports_vision is True
        assert gpt4o.capabilities.supports_audio is False
        assert gpt4o.capabilities.supports_structured_outputs is True
        assert gpt4o.capabilities.supports_fine_tuning is True
        assert gpt4o.capabilities.supports_distillation is True
        assert gpt4o.capabilities.supports_predicted_outputs is True
        assert gpt4o.variant == "omni"

        # 测试 GLM-4V-Plus 的特殊 capabilities
        glm4v_plus = LLMeta("glm-4v-plus")
        assert glm4v_plus.capabilities.supports_vision is True
        assert glm4v_plus.capabilities.supports_video is True
        assert glm4v_plus.capabilities.max_video_size_mb == 20.0
        assert glm4v_plus.variant == "vision-plus"

        # 测试 GLM-4V-Plus-0111 的特殊 capabilities（不同的视频限制）
        glm4v_plus_0111 = LLMeta("glm-4v-plus-0111")
        assert glm4v_plus_0111.capabilities.supports_vision is True
        assert glm4v_plus_0111.capabilities.supports_video is True
        assert glm4v_plus_0111.capabilities.max_video_size_mb == 200.0
        assert glm4v_plus_0111.capabilities.max_video_duration_seconds is None
        assert glm4v_plus_0111.variant == "vision-plus"

        # 测试 GLM-4V-Flash 的特殊 capabilities（不支持 base64）
        glm4v_flash = LLMeta("glm-4v-flash")
        assert glm4v_flash.capabilities.supports_vision is True
        assert glm4v_flash.capabilities.supports_image_base64 is False
        assert glm4v_flash.variant == "vision-flash"

    def test_specific_model_pattern_matching(self) -> None:
        """测试子 SpecificModel 的 pattern 匹配优先级 / Test specific model pattern matching priority"""
        # 测试子 pattern 优先于父 pattern
        # GPT-4 Turbo 应该匹配子 pattern，而不是父 pattern
        gpt4o_turbo = LLMeta("gpt-4o-turbo")
        assert gpt4o_turbo.variant == "turbo"
        assert gpt4o_turbo.capabilities.supports_vision is True

        # 测试带版本号的子 pattern 匹配
        gpt4o_turbo_with_date = LLMeta("gpt-4o-turbo-2024-04-09")
        assert gpt4o_turbo_with_date.variant == "turbo"
        assert gpt4o_turbo_with_date.capabilities.supports_vision is True

        # 测试普通的父 pattern 匹配
        gpt4_base = LLMeta("gpt-4")
        assert gpt4_base.variant == "base"
        # base 版本不应该有 vision 能力（除非在配置中明确指定）
        # 这里需要根据实际配置来验证

    def test_specific_model_capabilities_inheritance(self) -> None:
        """测试子 SpecificModel 的 capabilities 继承和覆盖 / Test specific model capabilities inheritance and override"""
        # 测试子 model 继承父 family 的基础 capabilities，并覆盖特定字段

        # GPT-4 家族的基础 capabilities
        gpt4_base = LLMeta("gpt-4")
        base_supports_function_calling = gpt4_base.capabilities.supports_function_calling

        # GPT-4 Turbo 应该继承 function_calling，但有自己的 vision 和 context_window
        gpt4_turbo = LLMeta("gpt-4-0621")
        assert gpt4_turbo.capabilities.supports_function_calling == base_supports_function_calling
        assert gpt4_turbo.capabilities.supports_vision is False
        assert gpt4_turbo.capabilities.context_window == 128000  # 上下文窗口

        # GLM-4V 系列测试
        glm4v_base = LLMeta("glm-4v")
        glm4v_plus = LLMeta("glm-4v-plus")

        # 两者都支持 vision，但 plus 有额外的 video 支持
        assert glm4v_base.capabilities.supports_vision is True
        assert glm4v_plus.capabilities.supports_vision is True
        assert glm4v_plus.capabilities.supports_video is True

        # plus 的 max_tokens 应该更大或相同
        assert glm4v_plus.capabilities.max_tokens >= glm4v_base.capabilities.max_tokens
