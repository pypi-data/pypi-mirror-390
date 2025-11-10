# filename: test_provider.py
# @Time    : 2025/11/7 13:56
# @Author  : JQQ
# @Email   : jqq1716@gmail.com
# @Software: PyCharm
"""
提供商测试 / Provider tests
"""

import unittest

from whosellm.provider import Provider


class TestProvider(unittest.TestCase):
    """提供商测试类 / Provider test class"""

    def test_from_model_name_openai(self) -> None:
        """测试 OpenAI 模型识别 / Test OpenAI model recognition"""
        assert Provider.from_model_name("gpt-4") == Provider.OPENAI
        assert Provider.from_model_name("gpt-3.5-turbo") == Provider.OPENAI
        assert Provider.from_model_name("o1") == Provider.OPENAI
        assert Provider.from_model_name("o3") == Provider.OPENAI

    def test_from_model_name_anthropic(self) -> None:
        """测试 Anthropic 模型识别 / Test Anthropic model recognition"""
        assert Provider.from_model_name("claude-sonnet-4-5") == Provider.ANTHROPIC
        assert Provider.from_model_name("claude-opus-4-1") == Provider.ANTHROPIC

    def test_from_model_name_zhipu(self) -> None:
        """测试智谱 AI 模型识别 / Test Zhipu AI model recognition"""
        assert Provider.from_model_name("glm-4") == Provider.ZHIPU
        assert Provider.from_model_name("chatglm") == Provider.ZHIPU
        assert Provider.from_model_name("cogview") == Provider.ZHIPU

    def test_from_model_name_alibaba(self) -> None:
        """测试阿里云模型识别 / Test Alibaba model recognition"""
        assert Provider.from_model_name("qwen3-turbo") == Provider.ALIBABA
        assert Provider.from_model_name("qwen3-turbo-2025-09-23") == Provider.ALIBABA

    def test_from_model_name_baidu(self) -> None:
        """测试百度模型识别 / Test Baidu model recognition"""
        assert Provider.from_model_name("ernie-bot") == Provider.BAIDU
        assert Provider.from_model_name("wenxin") == Provider.BAIDU

    def test_from_model_name_unknown(self) -> None:
        """测试未知模型识别 / Test unknown model recognition"""
        assert Provider.from_model_name("unknown-model") == Provider.UNKNOWN
