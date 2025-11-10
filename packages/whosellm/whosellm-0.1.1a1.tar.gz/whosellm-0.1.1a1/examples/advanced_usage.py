# filename: advanced_usage.py
# @Time    : 2025/11/7 15:19
# @Author  : JQQ
# @Email   : jqq1716@gmail.com
# @Software: PyCharm
"""
高级用法示例 / Advanced usage examples

展示型号优先级比较和Provider指定功能
Demonstrates variant priority comparison and Provider specification features
"""

from whosellm import LLMeta


def demo_variant_priority():
    """
    演示型号优先级比较 / Demonstrate variant priority comparison
    """
    print("=" * 60)
    print("型号优先级比较示例 / Variant Priority Comparison Examples")
    print("=" * 60)

    # GPT-4 系列型号比较 / GPT-4 series variant comparison
    print("\n1. GPT-4 系列型号比较 (mini < base < turbo < omni):")
    gpt4o_mini = LLMeta("gpt-4o-mini")
    gpt4_base = LLMeta("gpt-4")
    gpt4_turbo = LLMeta("gpt-4-turbo")
    gpt4o = LLMeta("gpt-4o")

    print(f"   {gpt4o_mini.model_name} < {gpt4_base.model_name}: {gpt4o_mini < gpt4_base}")
    print(f"   {gpt4_base.model_name} < {gpt4_turbo.model_name}: {gpt4_base < gpt4_turbo}")
    print(f"   {gpt4_turbo.model_name} < {gpt4o.model_name}: {gpt4_turbo < gpt4o}")

    # GLM-4 系列型号比较 / GLM-4 series variant comparison
    print("\n2. GLM-4 系列型号比较 (flash < base < plus):")
    glm4_flash = LLMeta("glm-4-flash")
    glm4_base = LLMeta("glm-4")
    glm4_plus = LLMeta("glm-4-plus")

    print(f"   {glm4_flash.model_name} < {glm4_base.model_name}: {glm4_flash < glm4_base}")
    print(f"   {glm4_base.model_name} < {glm4_plus.model_name}: {glm4_base < glm4_plus}")

    # GLM-4V 系列型号比较 / GLM-4V series variant comparison
    print("\n3. GLM-4V 系列型号比较 (flash < base < plus < plus-0111):")
    glm4v_flash = LLMeta("glm-4v-flash")
    glm4v_base = LLMeta("glm-4v")
    glm4v_plus = LLMeta("glm-4v-plus")
    glm4v_plus_0111 = LLMeta("glm-4v-plus-0111")

    print(f"   {glm4v_flash.model_name} < {glm4v_base.model_name}: {glm4v_flash < glm4v_base}")
    print(f"   {glm4v_base.model_name} < {glm4v_plus.model_name}: {glm4v_base < glm4v_plus}")
    print(f"   {glm4v_plus.model_name} < {glm4v_plus_0111.model_name}: {glm4v_plus < glm4v_plus_0111}")

    # 展示能力差异 / Show capability differences
    print("\n4. GLM-4V 不同型号的能力差异:")
    print(f"   {glm4v_plus.model_name}:")
    print(f"      - 最大视频大小: {glm4v_plus.capabilities.max_video_size_mb}MB")
    print(f"      - 最大视频时长: {glm4v_plus.capabilities.max_video_duration_seconds}秒")
    print(f"   {glm4v_plus_0111.model_name}:")
    print(f"      - 最大视频大小: {glm4v_plus_0111.capabilities.max_video_size_mb}MB")
    print(f"      - 最大视频时长: {glm4v_plus_0111.capabilities.max_video_duration_seconds}")


def demo_model_family():
    """
    演示模型家族概念 / Demonstrate model family concept
    """
    print("\n" + "=" * 60)
    print("模型家族概念示例 / Model Family Concept Examples")
    print("=" * 60)

    # 同一家族的不同型号 / Different variants in the same family
    print("\n1. 同一家族的不同型号:")
    gpt4 = LLMeta("gpt-4")
    gpt4_turbo = LLMeta("gpt-4-turbo")
    gpt4o = LLMeta("gpt-4o")

    print(f"   {gpt4.model_name}: family={gpt4.family}, provider={gpt4.provider}")
    print(f"   {gpt4_turbo.model_name}: family={gpt4_turbo.family}, provider={gpt4_turbo.provider}")
    print(f"   {gpt4o.model_name}: family={gpt4o.family}, provider={gpt4o.provider}")
    print(f"   它们属于同一家族: {gpt4.family == gpt4_turbo.family == gpt4o.family}")

    # 不同家族无法比较 / Different families cannot be compared
    print("\n2. 不同家族的模型无法比较:")
    gpt4 = LLMeta("gpt-4")
    glm4 = LLMeta("glm-4")

    print(f"   {gpt4.model_name}: family={gpt4.family}")
    print(f"   {glm4.model_name}: family={glm4.family}")
    print("   尝试比较会抛出异常...")

    try:
        _ = gpt4 > glm4
    except ValueError as e:
        print(f"   ✓ 捕获到预期的异常: {str(e).split('/')[0].strip()}")


def demo_provider_specification():
    """
    演示Provider指定功能 / Demonstrate Provider specification feature
    """
    print("\n" + "=" * 60)
    print("Provider 指定功能示例 / Provider Specification Examples")
    print("=" * 60)

    # 使用默认Provider / Use default Provider
    print("\n1. 使用默认Provider:")
    model1 = LLMeta("gpt-4")
    print(f"   模型: {model1.model_name}")
    print(f"   Provider: {model1.provider}")
    print(f"   Family: {model1.family}")

    # 使用 Provider::ModelName 语法 / Use Provider::ModelName syntax
    print("\n2. 使用 Provider::ModelName 语法:")
    model2 = LLMeta("openai::gpt-4")
    print(f"   模型: {model2.model_name}")
    print(f"   Provider: {model2.provider}")
    print(f"   Family: {model2.family}")

    # 使用 Provider::ModelName 语法指定不同的Provider / Use Provider::ModelName syntax with different provider
    print("\n3. 使用 Provider::ModelName 语法指定不同的Provider:")
    model3 = LLMeta("Tencent::deepseek-chat")
    print(f"   模型: {model3.model_name}")
    print(f"   Provider: {model3.provider}")
    print(f"   Family: {model3.family}")

    # 验证默认Provider和显式指定的等价性 / Verify equivalence between default and explicit provider
    print("\n4. 验证默认Provider和显式指定的等价性:")
    print(f"   model1.family == model2.family: {model1.family == model2.family}")
    print(f"   model1.provider == model2.provider: {model1.provider == model2.provider}")
    print("   注意: model3 使用了不同的Provider (Tencent)")


def demo_practical_usage():
    """
    演示实际应用场景 / Demonstrate practical usage scenarios
    """
    print("\n" + "=" * 60)
    print("实际应用场景示例 / Practical Usage Scenarios")
    print("=" * 60)

    # 场景1: 根据预算选择合适的模型 / Scenario 1: Choose model based on budget
    print("\n场景1: 根据预算选择合适的模型")
    print("假设价格: mini < base < turbo < omni")

    available_models = [
        LLMeta("gpt-4o-mini"),
        LLMeta("gpt-4"),
        LLMeta("gpt-4-turbo"),
        LLMeta("gpt-4o"),
    ]

    # 按价格排序（从低到高） / Sort by price (low to high)
    sorted_models = sorted(available_models)
    print("\n按价格排序的模型列表:")
    for i, model in enumerate(sorted_models, 1):
        print(f"   {i}. {model.model_name} (variant_priority: {model._variant_priority})")

    # 场景2: 选择满足能力要求的最便宜模型 / Scenario 2: Choose cheapest model meeting requirements
    print("\n场景2: 选择支持视觉的最便宜模型")
    vision_models = [m for m in available_models if m.capabilities.supports_vision]
    if vision_models:
        cheapest_vision = min(vision_models)
        print(f"   推荐模型: {cheapest_vision.model_name}")
        print(f"   支持视觉: {cheapest_vision.capabilities.supports_vision}")
        print(f"   上下文窗口: {cheapest_vision.capabilities.context_window}")

    # 场景3: 检查模型升级路径 / Scenario 3: Check model upgrade path
    print("\n场景3: 检查模型升级路径")
    current_model = LLMeta("glm-4v-plus")
    new_model = LLMeta("glm-4v-plus-0111")

    print(f"   当前模型: {current_model.model_name}")
    print(f"   新模型: {new_model.model_name}")
    print(f"   是否为升级: {new_model > current_model}")
    print("   能力提升:")
    print(
        f"      - 视频大小限制: {current_model.capabilities.max_video_size_mb}MB → {new_model.capabilities.max_video_size_mb}MB"
    )
    print(
        f"      - 视频时长限制: {current_model.capabilities.max_video_duration_seconds}秒 → {new_model.capabilities.max_video_duration_seconds}"
    )


if __name__ == "__main__":
    demo_variant_priority()
    demo_model_family()
    demo_provider_specification()
    demo_practical_usage()

    print("\n" + "=" * 60)
    print("示例运行完成！/ Examples completed!")
    print("=" * 60)
