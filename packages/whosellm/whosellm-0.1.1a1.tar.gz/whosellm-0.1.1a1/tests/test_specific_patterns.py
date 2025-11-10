#!/usr/bin/env python3
"""
测试 specific_models 的子 patterns 功能
Test specific_models sub-patterns functionality
"""

# 导入所有模型家族配置以触发注册
# Import all model family configurations to trigger registration
import pytest

from whosellm.capabilities import ModelCapabilities
from whosellm.models.base import ModelFamily
from whosellm.models.config import ModelFamilyConfig, SpecificModelConfig
from whosellm.models.registry import get_specific_model_config, match_model_pattern
from whosellm.provider import Provider


def test_basic_functionality():
    """测试基本功能 / Test basic functionality"""
    print("=" * 80)
    print("测试 1: 基本功能测试 / Test 1: Basic Functionality")
    print("=" * 80)

    # 动态添加 Mock Provider 和 ModelFamily 以避免冲突
    Provider.add_member("MOCK_PROVIDER_1", "mock-provider-1")
    ModelFamily.add_member("MOCK_FAMILY_1", "mock-family-1")

    # 创建一个测试配置
    ModelFamilyConfig(
        family=ModelFamily.MOCK_FAMILY_1,
        provider=Provider.MOCK_PROVIDER_1,
        version_default="4.0",
        patterns=[
            "test-{variant:variant}-{version}",
            "test-{variant:variant}",
            "test",
        ],
        capabilities=ModelCapabilities(
            supports_function_calling=True,
            max_tokens=8192,
        ),
        specific_models={
            "test-special": SpecificModelConfig(
                version_default="4.5",
                variant_default="special",
                capabilities=ModelCapabilities(
                    supports_vision=True,
                    max_tokens=16384,
                ),
                patterns=[
                    "test-special-{version}",
                    "test-special",
                ],
            ),
        },
    )

    # 测试子 pattern 匹配
    print("\n1. 测试子 pattern 匹配 'test-special':")
    result = match_model_pattern("test-special")
    print(f"   匹配结果: {result}")
    assert result is not None, "应该匹配成功"
    assert result["variant"] == "special", f"variant 应该是 'special'，实际是 {result['variant']}"
    assert result["version"] == "4.5", f"version 应该是 '4.5'，实际是 {result['version']}"
    print("   ✓ 通过")

    # 测试子 pattern 匹配带版本
    print("\n2. 测试子 pattern 匹配 'test-special-5.0':")
    result = match_model_pattern("test-special-5.0")
    print(f"   匹配结果: {result}")
    assert result is not None, "应该匹配成功"
    assert result["variant"] == "special", f"variant 应该是 'special'，实际是 {result['variant']}"
    print("   ✓ 通过")

    # 测试父 pattern 匹配
    print("\n3. 测试父 pattern 匹配 'test-normal':")
    result = match_model_pattern("test-normal")
    print(f"   匹配结果: {result}")
    assert result is not None, "应该匹配成功"
    assert result["variant"] == "normal", f"variant 应该是 'normal'，实际是 {result['variant']}"
    print("   ✓ 通过")

    # 测试 get_specific_model_config
    print("\n4. 测试 get_specific_model_config 'test-special':")
    config = get_specific_model_config("test-special")
    print(f"   配置: {config}")
    assert config is not None, "应该找到配置"
    version, variant, capabilities = config
    assert version == "4.5", f"version 应该是 '4.5'，实际是 {version}"
    assert variant == "special", f"variant 应该是 'special'，实际是 {variant:variant}"
    assert capabilities.supports_vision is True, "应该支持 vision"
    print("   ✓ 通过")

    print("\n✅ 测试 1 全部通过！\n")


def test_validation():
    """测试验证逻辑 / Test validation logic"""
    print("=" * 80)
    print("测试 2: 验证逻辑测试 / Test 2: Validation Logic")
    print("=" * 80)

    # 动态添加 Mock Provider 和 ModelFamily 以避免冲突
    Provider.add_member("MOCK_PROVIDER_2", "mock-provider-2")
    ModelFamily.add_member("MOCK_FAMILY_2", "mock-family-2")

    # 测试无效的子 pattern（不匹配父 pattern）
    print("\n1. 测试无效的子 pattern（应该抛出异常）:")
    try:
        ModelFamilyConfig(
            family=ModelFamily.MOCK_FAMILY_2,
            provider=Provider.MOCK_PROVIDER_2,
            version_default="4.0",
            patterns=[
                "test-{variant:variant}",
            ],
            specific_models={
                "invalid": SpecificModelConfig(
                    version_default="1.0",
                    variant_default="invalid",
                    patterns=[
                        "completely-different-{variant:variant}",  # 这个不匹配父 pattern
                    ],
                ),
            },
        )
        print("   ✗ 失败：应该抛出 ValueError")
        pytest.fail("应该抛出 ValueError")
    except ValueError as e:
        print(f"   ✓ 通过：正确抛出异常 - {e}")

    print("\n✅ 测试 2 全部通过！\n")


def test_priority():
    """测试优先级 / Test priority"""
    print("=" * 80)
    print("测试 3: 优先级测试 / Test 3: Priority Test")
    print("=" * 80)

    # 动态添加 Mock Provider 和 ModelFamily 以避免冲突
    Provider.add_member("MOCK_PROVIDER_3", "mock-provider-3")
    ModelFamily.add_member("MOCK_FAMILY_3", "mock-family-3")

    # 创建配置，子 pattern 和父 pattern 都能匹配同一个模型名
    ModelFamilyConfig(
        family=ModelFamily.MOCK_FAMILY_3,
        provider=Provider.MOCK_PROVIDER_3,
        version_default="4.0",
        patterns=[
            "priority-{variant:variant}",
        ],
        capabilities=ModelCapabilities(
            max_tokens=8192,
        ),
        specific_models={
            "priority-special": SpecificModelConfig(
                version_default="5.0",
                variant_default="special-override",
                capabilities=ModelCapabilities(
                    supports_vision=True,
                    max_tokens=16384,
                ),
                patterns=[
                    "priority-{variant:variant}",  # 和父 pattern 一样
                ],
            ),
        },
    )

    print("\n1. 测试 'priority-special' 应该优先匹配子 pattern:")
    result = match_model_pattern("priority-special")
    print(f"   匹配结果: {result}")
    assert result is not None, "应该匹配成功"
    assert result["variant"] == "special-override", f"应该使用子 pattern 的 variant，实际是 {result['variant']}"
    assert result["version"] == "5.0", f"应该使用子 pattern 的 version，实际是 {result['version']}"
    print("   ✓ 通过：子 pattern 优先级更高")

    print("\n✅ 测试 3 全部通过！\n")


def test_existing_models():
    """测试现有模型配置 / Test existing model configurations"""
    print("=" * 80)
    print("测试 4: 现有模型配置测试 / Test 4: Existing Model Configurations")
    print("=" * 80)

    # 测试 OpenAI 模型
    print("\n1. 测试 OpenAI 'gpt-4o-turbo':")
    result = match_model_pattern("gpt-4o-turbo")
    print(f"   匹配结果: {result}")
    assert result is not None, "应该匹配成功"
    print("   ✓ 通过")

    config = get_specific_model_config("gpt-4o-mini")
    print(f"   配置: {config}")
    assert config is not None, "应该找到配置"
    version, variant, capabilities = config
    assert variant == "mini", f"variant 应该是 'mini'，实际是 {variant:variant}"
    assert capabilities.supports_vision is True, "应该支持 vision"
    print("   ✓ 通过")

    # 测试智谱模型
    print("\n2. 测试智谱 'glm-4v-plus':")
    result = match_model_pattern("glm-4v-plus")
    print(f"   匹配结果: {result}")
    assert result is not None, "应该匹配成功"
    print("   ✓ 通过")

    config = get_specific_model_config("glm-4v-plus")
    print(f"   配置: {config}")
    assert config is not None, "应该找到配置"
    version, variant, capabilities = config
    assert version == "4.0", "版本匹配为4.0"
    assert variant == "vision-plus", f"variant 应该是 'vision-plus'，实际是 {variant:variant}"
    assert capabilities.supports_video is True, "应该支持 video"
    print("   ✓ 通过")

    print("\n✅ 测试 4 全部通过！\n")
