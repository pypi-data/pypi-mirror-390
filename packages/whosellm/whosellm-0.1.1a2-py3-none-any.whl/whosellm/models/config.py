# filename: config.py
# @Time    : 2025/11/7 17:35
# @Author  : JQQ
# @Email   : jqq1716@gmail.com
# @Software: PyCharm
"""
模型家族配置类 / Model family configuration class

集中管理模型家族的所有配置信息，包括命名模式、默认能力等
Centrally manage all configuration for model families, including naming patterns, default capabilities, etc.
"""

from dataclasses import dataclass, field

from whosellm.capabilities import ModelCapabilities
from whosellm.models.base import ModelFamily
from whosellm.models.patterns import parse_pattern
from whosellm.provider import Provider


@dataclass
class SpecificModelConfig:
    """
    特定模型配置 / Specific model configuration

    用于预注册特定模型的详细配置
    Used for pre-registering detailed configuration for specific models
    """

    # 模型版本 / Model version
    version_default: str

    # 模型变体 / Model variant
    variant_default: str

    # 自定义能力（可选） / Custom capabilities (optional)
    capabilities: ModelCapabilities | None = None

    # 子命名模式（可选） / Sub-patterns (optional)
    # 必须是父 patterns 的子集 / Must be a subset of parent patterns
    patterns: list[str] = field(default_factory=list)

    # 型号优先级（可选） / Variant priority (optional)
    # 如果未指定，将使用 infer_variant_priority 推断
    # If not specified, will be inferred using infer_variant_priority
    variant_priority: tuple[int, ...] | None = None


@dataclass
class ModelFamilyConfig:
    """
    模型家族配置 / Model family configuration

    集中管理一个模型家族的所有配置信息
    Centrally manage all configuration for a model family
    """

    # 基本信息 / Basic information
    family: ModelFamily
    provider: Provider

    # 命名模式 / Naming patterns
    # 按优先级排序，更具体的在前 / Ordered by priority, more specific first
    patterns: list[str] = field(default_factory=list)

    # 默认值 / Defaults
    version_default: str = "1.0"
    variant_default: str = field(default="base")
    # 默认型号优先级（可选） / Default variant priority (optional)
    # 如果未指定，将使用 infer_variant_priority 推断
    # If not specified, will be inferred using infer_variant_priority
    variant_priority_default: tuple[int, ...] | None = None

    # 默认能力 / Default capabilities
    capabilities: ModelCapabilities = field(default_factory=ModelCapabilities)

    # 预注册的特定模型（可选） / Pre-registered specific models (optional)
    # 格式: {model_name: SpecificModelConfig}
    # Format: {model_name: SpecificModelConfig}
    specific_models: dict[str, SpecificModelConfig] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """注册到全局注册表并验证配置 / Register to global registry and validate configuration"""
        self._validate_specific_models()

        from whosellm.models.registry import register_family_config

        register_family_config(self)

    def _validate_specific_models(self) -> None:
        """
        验证 specific_models 的子 patterns 必须匹配父 patterns
        Validate that sub-patterns in specific_models must match parent patterns
        """
        for model_name, config in self.specific_models.items():
            if not config.patterns:
                continue

            # 检查每个子 pattern 是否能匹配至少一个父 pattern
            # Check if each sub-pattern can match at least one parent pattern
            for sub_pattern in config.patterns:
                is_valid = False
                for parent_pattern in self.patterns:
                    # 尝试用子 pattern 解析一个符合父 pattern 的示例
                    # Try to parse an example that conforms to parent pattern using sub-pattern
                    if self._is_pattern_subset(sub_pattern, parent_pattern):
                        is_valid = True
                        break

                if not is_valid:
                    msg = (
                        f"Sub-pattern '{sub_pattern}' in specific_model '{model_name}' "
                        f"does not match any parent patterns: {self.patterns}"
                    )
                    raise ValueError(msg)

    def _is_pattern_subset(self, sub_pattern: str, parent_pattern: str) -> bool:
        """
        检查子 pattern 是否是父 pattern 的子集
        Check if sub-pattern is a subset of parent pattern

        子 pattern 必须能够被父 pattern 匹配
        Sub-pattern must be matchable by parent pattern
        """
        # 生成一个符合子 pattern 的示例字符串
        # Generate an example string that conforms to sub-pattern
        example = self._generate_pattern_example(sub_pattern)
        if not example:
            return False

        # 检查这个示例是否能被父 pattern 匹配
        # Check if this example can be matched by parent pattern
        result = parse_pattern(parent_pattern, example)
        return result is not None

    def _generate_pattern_example(self, pattern: str) -> str:
        """
        从 pattern 生成一个示例字符串
        Generate an example string from pattern

        Args:
            pattern: 命名模式 / Naming pattern

        Returns:
            str: 示例字符串 / Example string
        """
        # 根据占位符类型返回更贴合的示例值，确保 parse 校验通过
        # Return example values respecting placeholder type hints to keep parse validation working
        import re

        def _placeholder_replacer(match: re.Match[str]) -> str:
            placeholder = match.group(0)[1:-1]
            if ":" in placeholder:
                _, type_spec = placeholder.split(":", 1)
                type_spec = type_spec.strip()
            else:
                type_spec = ""

            if type_spec.endswith("d"):
                width_str = type_spec[:-1].strip()
                width = int(width_str) if width_str.isdigit() else 1
                return "1".rjust(max(width, 1), "0")

            return "test"

        return re.sub(r"\{[^}]+\}", _placeholder_replacer, pattern)
