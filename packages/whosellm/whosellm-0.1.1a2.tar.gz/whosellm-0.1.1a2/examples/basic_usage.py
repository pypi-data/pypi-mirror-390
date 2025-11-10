# filename: basic_usage.py
# @Time    : 2025/11/7 13:56
# @Author  : JQQ
# @Email   : jqq1716@gmail.com
# @Software: PyCharm
"""
基础使用示例 / Basic usage examples
"""

from whosellm import LLMeta


def main() -> None:
    """主函数 / Main function"""
    print("=== LLMeta 基础使用示例 / Basic Usage Examples ===\n")

    # 1. 初始化模型 / Initialize models
    print("1. 初始化模型 / Initialize models")
    gpt4 = LLMeta("gpt-4")
    gpt35 = LLMeta("gpt-3.5-turbo")
    glm4v = LLMeta("glm-4v-plus")

    print(f"  - {gpt4}")
    print(f"  - {gpt35}")
    print(f"  - {glm4v}\n")

    # 2. 版本比较 / Version comparison
    print("2. 版本比较 / Version comparison")
    print(f"  - GPT-4 > GPT-3.5: {gpt4 > gpt35}")
    print(f"  - GPT-4 == GPT-3.5: {gpt4 == gpt35}\n")

    # 3. 能力检查 / Capability check
    print("3. 能力检查 / Capability check")
    print(f"  - GPT-4 支持视觉 / supports vision: {gpt4.capabilities.supports_vision}")
    print(f"  - GPT-4 Turbo 支持视觉 / supports vision: {LLMeta('gpt-4-turbo').capabilities.supports_vision}")
    print(f"  - GLM-4V-Plus 支持视觉 / supports vision: {glm4v.capabilities.supports_vision}")
    print(f"  - GLM-4V-Plus 支持视频 / supports video: {glm4v.capabilities.supports_video}")
    print(f"  - GLM-4V-Plus 视频大小限制 / video size limit: {glm4v.capabilities.max_video_size_mb}MB")
    print(f"  - GLM-4V-Plus 视频时长限制 / video duration limit: {glm4v.capabilities.max_video_duration_seconds}s\n")

    # 4. 推理模型 / Reasoning models
    print("4. 推理模型 / Reasoning models")
    o1 = LLMeta("o1")
    print(f"  - O1 支持思考模式 / supports thinking: {o1.capabilities.supports_thinking}")
    print(f"  - O1 支持流式输出 / supports streaming: {o1.capabilities.supports_streaming}\n")

    # 5. 多模态检查 / Multimodal check
    print("5. 多模态检查 / Multimodal check")
    print(f"  - GPT-4 支持多模态 / supports multimodal: {gpt4.supports_multimodal}")
    print(f"  - GPT-4 Turbo 支持多模态 / supports multimodal: {LLMeta('gpt-4-turbo').supports_multimodal}")
    print(f"  - GLM-4V-Plus 支持多模态 / supports multimodal: {glm4v.supports_multimodal}\n")

    # 6. 提供商信息 / Provider information
    print("6. 提供商信息 / Provider information")
    print(f"  - GPT-4 提供商 / provider: {gpt4.provider}")
    print(f"  - GLM-4V 提供商 / provider: {glm4v.provider}\n")


if __name__ == "__main__":
    main()
