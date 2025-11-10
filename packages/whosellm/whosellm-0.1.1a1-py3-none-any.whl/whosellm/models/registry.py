# filename: registry.py
# @Time    : 2025/11/7 17:35
# @Author  : JQQ
# @Email   : jqq1716@gmail.com
# @Software: PyCharm

"""
统一模型注册表 / Unified model registry

提供模型家族配置的注册和查询接口
Provides registration and query interfaces for model family configurations
"""

from typing import TYPE_CHECKING, Any

from whosellm.capabilities import ModelCapabilities
from whosellm.models.base import MODEL_REGISTRY, ModelFamily, ModelInfo, register_model
from whosellm.models.patterns import parse_pattern
from whosellm.provider import Provider

if TYPE_CHECKING:
    from whosellm.models.config import ModelFamilyConfig

# 核心注册表：所有模型家族配置 / Core registry: all model family configs
# 格式: {(family, provider): ModelFamilyConfig}
_FAMILY_CONFIGS: dict[tuple[ModelFamily, Provider], "ModelFamilyConfig"] = {}

# 默认 Provider 映射 / Default provider mapping
_DEFAULT_PROVIDER: dict[ModelFamily, Provider] = {}

# 缓存：模型名称 -> ModelInfo / Cache: model_name -> ModelInfo
_MODEL_CACHE: dict[str, ModelInfo] = {}


def register_family_config(config: "ModelFamilyConfig") -> None:
    """
    注册模型家族配置 / Register model family configuration

    Args:
        config: 模型家族配置 / Model family configuration
    """
    key = (config.family, config.provider)
    _FAMILY_CONFIGS[key] = config

    # 如果该家族还没有默认 Provider，设置第一个注册的为默认
    if config.family not in _DEFAULT_PROVIDER:
        _DEFAULT_PROVIDER[config.family] = config.provider


def get_family_config(family: ModelFamily, provider: Provider | None = None) -> "ModelFamilyConfig | None":
    """
    获取模型家族配置 / Get model family configuration

    Args:
        family: 模型家族 / Model family
        provider: Provider（可选，如果未指定则使用默认） / Provider (optional, use default if not specified)

    Returns:
        ModelFamilyConfig | None: 配置或None / Config or None
    """
    if provider is None:
        provider = _DEFAULT_PROVIDER.get(family)
        if provider is None:
            return None

    return _FAMILY_CONFIGS.get((family, provider))


def get_default_provider(family: ModelFamily) -> Provider | None:
    """
    获取模型家族的默认Provider / Get default provider for model family

    Args:
        family: 模型家族 / Model family

    Returns:
        Provider | None: 默认Provider或None / Default provider or None
    """
    return _DEFAULT_PROVIDER.get(family)


def get_default_capabilities(family: ModelFamily, provider: Provider | None = None) -> ModelCapabilities:
    """
    获取模型家族的默认能力 / Get default capabilities for model family

    Args:
        family: 模型家族 / Model family
        provider: Provider（可选） / Provider (optional)

    Returns:
        ModelCapabilities: 默认能力 / Default capabilities
    """
    config = get_family_config(family, provider)
    return config.capabilities if config else ModelCapabilities()


def get_all_patterns() -> list[tuple[ModelFamily, Provider, list[str], str]]:
    """
    获取所有命名模式 / Get all naming patterns

    Returns:
        list: [(family, provider, patterns, version_default), ...]
    """
    return [
        (config.family, config.provider, config.patterns, config.version_default) for config in _FAMILY_CONFIGS.values()
    ]


def match_model_pattern(model_name: str, provider: Provider | None = None) -> dict[str, Any] | None:
    """
    匹配模型名称到模式 / Match model name to pattern

    优先级：
    1. specific_models 的精确匹配
    2. specific_models 的子 patterns
    3. 家族的父 patterns

    Priority:
    1. Exact match in specific_models
    2. Sub-patterns in specific_models
    3. Parent patterns in family

    Args:
        model_name: 模型名称 / Model name
        provider: 指定 Provider 进行过滤（可选） / Specify provider for filtering (optional)

    Returns:
        dict | None: 匹配结果或None / Match result or None
    """
    model_lower = model_name.lower()
    matched: dict[str, Any]

    # 如果指定了 Provider，只匹配该 Provider 的配置
    # If provider is specified, only match configs from that provider
    configs_to_check = (
        [config for config in _FAMILY_CONFIGS.values() if config.provider == provider]
        if provider
        else list(_FAMILY_CONFIGS.values())
    )

    # 【最高优先级】精确匹配 specific_models 的名称
    # [Highest Priority] Exact match in specific_models
    for config in configs_to_check:
        if model_lower in config.specific_models:
            spec_config = config.specific_models[model_lower]
            return {
                "version": spec_config.version_default,
                "variant": spec_config.variant_default,
                "family": config.family,
                "provider": config.provider,
                "capabilities": spec_config.capabilities,
                "variant_priority": spec_config.variant_priority,
                "_from_specific_model": model_lower,
            }

    # 【次优先级】遍历所有家族配置的 specific_models 的子 patterns
    # [Secondary Priority] Iterate all specific_models sub-patterns in family configs
    for config in configs_to_check:
        for _spec_model_name, spec_config in config.specific_models.items():
            if not spec_config.patterns:
                continue

            for pattern in spec_config.patterns:
                result = parse_pattern(pattern, model_lower)
                if result:
                    # 转换为字典并添加默认值 / Convert to dict and add defaults
                    matched = dict(result.named)
                    if not matched.get("version"):
                        matched["version"] = spec_config.version_default
                    matched["family"] = config.family
                    matched["provider"] = config.provider
                    if not matched.get("variant"):
                        matched["variant"] = spec_config.variant_default
                        # 只有当使用默认 variant 时，才使用 variant_priority_default
                        matched["variant_priority"] = spec_config.variant_priority
                    else:
                        # 如果从 pattern 提取到了 variant，不设置 variant_priority
                        # 让后续逻辑根据 variant 推断
                        matched["variant_priority"] = None
                    matched["capabilities"] = spec_config.capabilities
                    matched["variant_priority"] = spec_config.variant_priority
                    # 标记这是从 specific_model 匹配的 / Mark this as matched from specific_model
                    matched["_from_specific_model"] = _spec_model_name
                    return matched

    # 【最低优先级】遍历所有家族配置的父 patterns
    # [Lowest Priority] Iterate all parent patterns in family configs
    for config in configs_to_check:
        for pattern in config.patterns:
            result = parse_pattern(pattern, model_lower)
            if result:
                # 转换为字典并添加默认值 / Convert to dict and add defaults
                matched = dict(result.named)
                if not matched.get("version"):
                    matched["version"] = config.version_default
                if not matched.get("variant"):
                    matched["variant"] = config.variant_default
                    # 只有当使用默认 variant 时，才使用 variant_priority_default
                    # Only use variant_priority_default when using default variant
                    matched["variant_priority"] = config.variant_priority_default
                else:
                    # 如果从 pattern 提取到了 variant，不设置 variant_priority
                    # 让后续逻辑根据 variant 推断
                    # If variant is extracted from pattern, don't set variant_priority
                    # Let subsequent logic infer from variant
                    matched["variant_priority"] = None
                matched["family"] = config.family
                matched["provider"] = config.provider
                matched["capabilities"] = config.capabilities
                return matched

    return None


def list_all_families() -> list[ModelFamily]:
    """
    列出所有已注册的模型家族 / List all registered model families

    Returns:
        list[ModelFamily]: 模型家族列表 / List of model families
    """
    return list({family for family, _ in _FAMILY_CONFIGS})


def get_family_info(family: ModelFamily, provider: Provider | None = None) -> dict[str, Any]:
    """
    获取模型家族的完整信息 / Get complete information for model family

    Args:
        family: 模型家族 / Model family
        provider: Provider（可选） / Provider (optional)

    Returns:
        dict: 家族信息 / Family information
    """
    config = get_family_config(family, provider)
    if not config:
        return {}

    return {
        "family": config.family,
        "provider": config.provider,
        "patterns": config.patterns,
        "version_default": config.version_default,
        "capabilities": config.capabilities,
        "specific_models": list(config.specific_models.keys()),
    }


def get_specific_model_config(model_name: str) -> tuple[str, str, ModelCapabilities | None] | None:
    """
    获取特定模型的配置 / Get configuration for a specific model

    支持两种方式：
    1. 精确匹配 model_name
    2. 通过子 patterns 匹配

    Supports two ways:
    1. Exact match by model_name
    2. Match by sub-patterns

    Args:
        model_name: 模型名称 / Model name

    Returns:
        tuple | None: (version, variant, capabilities) 或 None
    """
    import parse  # type: ignore[import-untyped]

    model_lower = model_name.lower()

    # 方式1：精确匹配 / Method 1: Exact match
    for config in _FAMILY_CONFIGS.values():
        if model_lower in config.specific_models:
            spec_config = config.specific_models[model_lower]
            return spec_config.version_default, spec_config.variant_default, spec_config.capabilities

    # 方式2：通过子 patterns 匹配 / Method 2: Match by sub-patterns
    for config in _FAMILY_CONFIGS.values():
        for _spec_model_name, spec_config in config.specific_models.items():
            if not spec_config.patterns:
                continue

            for pattern in spec_config.patterns:
                result = parse.parse(pattern, model_lower)
                if result:
                    return spec_config.version_default, spec_config.variant_default, spec_config.capabilities

    return None


def register_family(config: "ModelFamilyConfig") -> None:
    """
    动态注册模型家族配置 / Dynamically register model family configuration

    允许用户在运行时添加新的模型家族配置
    Allows users to add new model family configurations at runtime

    Args:
        config: 模型家族配置 / Model family configuration

    Example:
        >>> from whosellm.models.config import ModelFamilyConfig
        >>> from whosellm.models.registry import register_family
        >>> from whosellm.capabilities import ModelCapabilities
        >>>
        >>> # 创建新的模型家族配置 / Create new model family configuration
        >>> gemini_config = ModelFamilyConfig(
        ...     family=ModelFamily.GEMINI,
        ...     provider=Provider.GOOGLE,
        ...     patterns=["gemini-{variant:variant}"],
        ...     capabilities=ModelCapabilities(supports_vision=True),
        ... )
        >>>
        >>> # 动态注册 / Register dynamically
        >>> register_family(gemini_config)
    """
    register_family_config(config)


__all__ = [
    "MODEL_REGISTRY",
    "get_all_patterns",
    "get_default_capabilities",
    "get_default_provider",
    "get_family_config",
    "get_family_info",
    "get_specific_model_config",
    "list_all_families",
    "match_model_pattern",
    "register_family",  # 用户友好的动态注册接口 / User-friendly dynamic registration interface
    "register_family_config",
    "register_model",
]
