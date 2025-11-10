# filename: base.py
# @Time    : 2025/11/7 13:56
# @Author  : JQQ
# @Email   : jqq1716@gmail.com
# @Software: PyCharm
"""
模型信息基础类 / Model information base class
"""

import re
from dataclasses import dataclass
from datetime import date
from enum import Enum

from whosellm.capabilities import ModelCapabilities
from whosellm.models.dynamic_enum import DynamicEnumMeta
from whosellm.provider import Provider


class ModelFamily(str, Enum, metaclass=DynamicEnumMeta):
    """
    模型家族枚举 / Model family enum

    支持动态添加新成员，第三方用户可以在运行时扩展
    Supports dynamically adding new members, third-party users can extend at runtime

    同一个模型家族可能有多个Provider提供
    Same model family may be provided by multiple providers

    Example:
        >>> # 动态添加新的模型家族 / Dynamically add new model family
        >>> ModelFamily.add_member("GEMINI", "gemini")
        >>> ModelFamily.add_member("LLAMA_3", "llama-3")
    """

    # OpenAI 家族 / OpenAI family
    GPT_5 = "gpt-5"
    GPT_4_1 = "gpt-4.1"
    GPT_4O = "gpt-4o"
    GPT_4 = "gpt-4"
    GPT_3_5 = "gpt-3.5"
    O1 = "o1"
    O3 = "o3"
    O4 = "o4"

    CLAUDE = "claude"

    # 智谱 AI 家族 / Zhipu AI family
    GLM_TEXT = "glm-text"  # 统一的GLM文本模型家族 / Unified GLM text model family
    GLM_VISION = "glm-vision"  # 统一的GLM视觉模型家族 / Unified GLM vision model family
    GLM_3 = "glm-3"
    COGVIEW_4 = "cogview-4"
    COGVIDEOX_3 = "cogvideox-3"
    COGVIDEOX_2 = "cogvideox-2"

    # 保留旧枚举作为别名，用于向后兼容 / Keep old enums as aliases for backward compatibility
    GLM_4 = "glm-text"  # 别名 -> GLM_TEXT
    GLM_45 = "glm-text"  # 别名 -> GLM_TEXT
    GLM_46 = "glm-text"  # 别名 -> GLM_TEXT
    GLM_4V = "glm-vision"  # 别名 -> GLM_VISION
    GLM_45V = "glm-vision"  # 别名 -> GLM_VISION

    # Vidu 家族 / Vidu family
    VIDU_Q1 = "viduq1"
    VIDU_2 = "vidu2"

    # 阿里云 家族 / Alibaba family
    QWEN = "qwen"

    # 百度 家族 / Baidu family
    ERNIE = "ernie"

    # 腾讯 家族 / Tencent family
    HUNYUAN = "hunyuan"

    # 月之暗面 家族 / Moonshot family
    MOONSHOT = "moonshot"

    # DeepSeek 家族 / DeepSeek family
    DEEPSEEK = "deepseek"

    # MiniMax 家族 / MiniMax family
    ABAB = "abab"

    UNKNOWN = "unknown"


@dataclass
class ModelInfo:
    """
    模型信息 / Model information
    """

    provider: Provider
    family: ModelFamily
    version: str
    variant: str
    capabilities: ModelCapabilities
    version_tuple: tuple[int, ...]
    # 型号优先级元组，用于同版本不同型号的比较 / Variant priority tuple for comparing different variants of the same version
    variant_priority: tuple[int, ...] = (0,)
    # 发布日期，用于同版本同型号的比较 / Release date for comparing same version and variant
    release_date: date | None = None


# 格式: {"model_name": ModelInfo} 或 {"Provider::ModelName": ModelInfo}
# Format: {"model_name": ModelInfo} or {"Provider::ModelName": ModelInfo}
MODEL_REGISTRY: dict[str, ModelInfo] = {}


# 注意：以下函数已迁移到 registry.py，这里保留是为了向后兼容
# Note: The following functions have been moved to registry.py, kept here for backward compatibility
def get_family_default_provider(family: ModelFamily) -> Provider | None:
    """
    获取模型家族的默认Provider / Get default provider for model family

    Args:
        family: 模型家族 / Model family

    Returns:
        Provider | None: 默认Provider或None / Default provider or None
    """
    from whosellm.models.registry import get_default_provider

    return get_default_provider(family)


# 注意：FAMILY_DEFAULT_CAPABILITIES 已迁移到 families/ 配置文件中
# Note: FAMILY_DEFAULT_CAPABILITIES has been migrated to families/ config files
# 现在通过 registry.get_default_capabilities() 获取
# Now use registry.get_default_capabilities() to get capabilities


def register_model(model_name: str, info: ModelInfo) -> None:
    """
    注册模型信息 / Register model information

    Args:
        model_name: 模型名称（小写） / Model name (lowercase)
        info: 模型信息 / Model information
    """
    MODEL_REGISTRY[model_name.lower()] = info


def parse_version(version_str: str) -> tuple[int, ...]:
    """
    解析版本字符串为元组 / Parse version string to tuple

    Args:
        version_str: 版本字符串，如 "4.0", "3.5" / Version string like "4.0", "3.5"

    Returns:
        tuple: 版本元组，至少包含两个部分 / Version tuple with at least two parts
    """
    if not version_str:
        return 0, 0

    parts = []
    for part in version_str.split("."):
        try:
            parts.append(int(part))
        except ValueError:
            # 如果包含非数字字符，尝试提取数字部分
            # If contains non-numeric characters, try to extract numeric part
            numeric = "".join(c for c in part if c.isdigit())
            if numeric:
                parts.append(int(numeric))
            else:
                parts.append(0)

    # 确保至少有两个部分，避免 (4,) 和 (4, 0) 比较时的歧义
    # Ensure at least two parts to avoid ambiguity when comparing (4,) and (4, 0)
    while len(parts) < 2:
        parts.append(0)

    return tuple(parts)


def parse_date_from_model_name(model_name: str) -> date | None:
    """
    从模型名称中解析日期 / Parse date from model name

    使用 parse 库进行模式匹配，避免使用正则表达式
    Use parse library for pattern matching, avoiding regular expressions

    支持的格式 / Supported formats:
    - YYYY-MM-DD (如 2024-04-09)
    - MMDD (如 0409, 假设为2024年)

    Args:
        model_name: 模型名称 / Model name

    Returns:
        date | None: 解析的日期或None / Parsed date or None
    """
    from whosellm.models.patterns import parse_date_from_match
    from whosellm.models.registry import match_model_pattern

    # 优先使用模式匹配 / Prioritize pattern matching
    matched = match_model_pattern(model_name)
    if matched:
        parsed_date = parse_date_from_match(matched)
        if parsed_date:
            return parsed_date

    return None


def parse_model_name(model_name: str) -> tuple[Provider | None, str]:
    """
    解析模型名称，支持 Provider::ModelName 语法 / Parse model name, supporting Provider::ModelName syntax

    Args:
        model_name: 模型名称，可能包含provider前缀 / Model name, may include provider prefix

    Returns:
        tuple: (指定的Provider或None, 实际模型名称) / (specified Provider or None, actual model name)
    """
    if "::" in model_name:
        # 解析 Provider::ModelName 格式 / Parse Provider::ModelName format
        parts = model_name.split("::", 1)
        provider_str = parts[0].strip()
        actual_name = parts[1].strip()

        # 尝试匹配Provider / Try to match Provider
        try:
            provider = Provider(provider_str.lower())
            return provider, actual_name
        except ValueError:
            # 如果Provider不存在，忽略前缀 / If Provider doesn't exist, ignore prefix
            return None, actual_name

    return None, model_name


def infer_model_family(model_name: str) -> ModelFamily:
    """
    从模型名称推断模型家族 / Infer model family from model name

    使用模式匹配进行推断 / Use pattern matching for inference

    Args:
        model_name: 模型名称 / Model name

    Returns:
        ModelFamily: 模型家族 / Model family
    """
    from whosellm.models.registry import match_model_pattern

    matched = match_model_pattern(model_name)
    if matched and "family" in matched:
        family = matched["family"]
        if isinstance(family, ModelFamily):
            return family

    return ModelFamily.UNKNOWN


def extract_variant_from_name(model_name: str, family: ModelFamily) -> str:
    """
    从模型名称中提取型号 / Extract variant from model name

    Args:
        model_name: 模型名称 / Model name
        family: 模型家族 / Model family

    Returns:
        str: 型号名称 / Variant name
    """
    model_lower = model_name.lower()

    # 移除家族名称前缀 / Remove family name prefix
    family_name = family.value.lower()
    if model_lower.startswith(family_name):
        model_lower = model_lower[len(family_name) :].lstrip("-")

    # 移除日期部分 / Remove date part
    model_lower = re.sub(r"-?\d{4}-\d{2}-\d{2}", "", model_lower)
    model_lower = re.sub(r"-?\d{8}", "", model_lower)
    model_lower = re.sub(r"-\d{4}(?!\d)", "", model_lower)

    # 移除常见的后缀（如 v1, v2, custom, test 等） / Remove common suffixes
    model_lower = re.sub(r"-(v\d+|custom|test|latest|new|experimental)$", "", model_lower)

    # 定义常见的型号关键词（按优先级排序） / Define common variant keywords (ordered by priority)
    variant_keywords = [
        "omni",
        "ultra",
        "pro",
        "plus",
        "turbo",
        "vision",
        "preview",
        "flash",
        "mini",
    ]

    # 查找型号 / Find variant
    found_variants = []
    for keyword in variant_keywords:
        if keyword in model_lower:
            found_variants.append(keyword)

    if found_variants:
        # 按在原字符串中出现的顺序排序 / Sort by order of appearance in original string
        found_variants.sort(key=lambda k: model_lower.index(k))
        return "-".join(found_variants)

    # 如果没有找到关键词，检查是否还有其他内容 / If no keywords found, check if there's other content
    model_lower = model_lower.strip("-")
    if model_lower and model_lower not in ["base", ""]:
        return model_lower

    return "base"


def infer_variant_priority(variant: str) -> tuple[int, ...]:
    """
    根据型号名称推断优先级 / Infer priority from variant name

    通用规则: mini < flash < base < turbo < plus < pro < ultra < omni
    General rule: mini < flash < base < turbo < plus < pro < ultra < omni

    Args:
        variant: 型号名称 / Variant name

    Returns:
        tuple: 优先级元组 / Priority tuple
    """
    # 定义型号优先级映射 / Define variant priority mapping
    priority_map = {
        "mini": 0,
        "flash": 0,
        "base": 1,
        "turbo": 2,
        "plus": 3,
        "pro": 4,
        "ultra": 5,
        "omni": 6,
        "preview": 0,  # preview 通常是早期版本 / preview is usually an early version
    }

    # 如果型号包含多个关键词，取最高优先级 / If variant contains multiple keywords, take highest priority
    variant_lower = variant.lower()
    found_priority = None

    for keyword, priority in priority_map.items():
        if keyword in variant_lower:
            found_priority = priority if found_priority is None else max(found_priority, priority)

    # 如果没有找到匹配的关键词，返回默认优先级 1 (base)
    # If no matching keyword found, return default priority 1 (base)
    return (found_priority if found_priority is not None else 1,)


def auto_register_model(
    model_name: str,
    specified_provider: Provider | None = None,
    capabilities: ModelCapabilities | None = None,
) -> ModelInfo:
    """
    自动注册模型 / Auto-register model

    根据模型名称自动推断模型家族、版本、型号等信息，并从家族继承默认能力
    Automatically infer model family, version, variant, etc. from model name, and inherit default capabilities from family

    Args:
        model_name: 模型名称 / Model name
        specified_provider: 指定的Provider（可选） / Specified provider (optional)
        capabilities: 指定的能力（可选） / Specified capabilities (optional)

    Returns:
        ModelInfo: 模型信息 / Model information

    Raises:
        ValueError: 如果无法推断模型家族且未提供能力 / If cannot infer model family and no capabilities provided
    """
    from whosellm.models.patterns import normalize_variant, parse_date_from_match
    from whosellm.models.registry import match_model_pattern

    # 使用模式匹配解析模型名称 / Use pattern matching to parse model name
    matched = match_model_pattern(model_name, specified_provider)

    if not matched:
        # 无法匹配任何模式 / Cannot match any pattern
        if capabilities is None:
            msg = (
                f"无法自动注册模型 '{model_name}'：无法推断模型家族，且未提供能力配置。"
                f"请手动注册或提供能力配置。 / "
                f"Cannot auto-register model '{model_name}': cannot infer model family and no capabilities provided. "
                f"Please register manually or provide capabilities."
            )
            raise ValueError(msg)

        # 使用默认值 / Use default values
        family = ModelFamily.UNKNOWN
        provider = specified_provider or Provider.UNKNOWN
        version = ""
        variant = "base"
        release_date = None
        variant_priority = None
    else:
        # 从匹配结果中提取信息 / Extract information from match result
        family = matched.get("family", ModelFamily.UNKNOWN)
        provider = specified_provider or matched.get("provider", Provider.UNKNOWN)
        version = str(matched.get("version", ""))
        variant = normalize_variant(matched.get("variant"))
        release_date = parse_date_from_match(matched)
        capabilities = matched.get("capabilities")
        variant_priority = matched.get("variant_priority")

    # 获取或继承能力 / Get or inherit capabilities
    if capabilities:
        model_capabilities = capabilities
    else:
        from whosellm.models.registry import get_default_capabilities

        model_capabilities = get_default_capabilities(family, provider)

    # 获取或推断型号优先级 / Get or infer variant priority
    # 优先使用配置中的 variant_priority，如果没有则推断
    # Prefer variant_priority from config, infer if not available
    if variant_priority is None:
        # 如果配置中没有指定，则根据 variant 推断
        # If not specified in config, infer from variant
        variant_priority = infer_variant_priority(variant)

    # 创建模型信息 / Create model info
    model_info = ModelInfo(
        provider=provider,
        family=family,
        version=version,
        variant=variant,
        capabilities=model_capabilities,
        version_tuple=parse_version(version),
        variant_priority=variant_priority,
        release_date=release_date,
    )

    # 注册到全局注册表 / Register to global registry
    register_model(model_name, model_info)

    return model_info


def get_model_info(model_name: str, auto_register: bool = True) -> ModelInfo:
    """
    根据模型名称查找模型信息 / Find model information by model name

    支持以下格式: / Supports the following formats:
    1. "gpt-4" - 使用默认Provider / Use default Provider
    2. "openai::gpt-4" - 指定Provider / Specify Provider
    3. "Tencent::deepseek-chat" - 指定Provider / Specify Provider

    查找优先级 / Search priority:
    1. 已注册的精确匹配（带 Provider 前缀）/ Exact match with Provider prefix
    2. 已注册的精确匹配（不带 Provider 前缀）/ Exact match without Provider prefix
    3. 自动注册（使用 match_model_pattern）/ Auto-register (using match_model_pattern)

    Args:
        model_name: 模型名称 / Model name
        auto_register: 是否自动注册未知模型 / Whether to auto-register unknown models

    Returns:
        ModelInfo: 模型信息 / Model information
    """
    # 解析模型名称 / Parse model name
    specified_provider, actual_name = parse_model_name(model_name)
    model_lower = actual_name.lower()

    # 【优先级1】如果指定了Provider，优先查找 "Provider::ModelName" 格式的注册
    # [Priority 1] If Provider is specified, prioritize "Provider::ModelName" format registration
    if specified_provider:
        provider_key = f"{specified_provider.value}::{model_lower}"
        if provider_key in MODEL_REGISTRY:
            return MODEL_REGISTRY[provider_key]

    # 【优先级2】检查注册表中是否有精确匹配 / [Priority 2] Check if there's an exact match in the registry
    if model_lower in MODEL_REGISTRY:
        info = MODEL_REGISTRY[model_lower]
        # 尝试从模型名称解析日期 / Try to parse date from model name
        parsed_date = parse_date_from_model_name(actual_name)

        # 如果指定了Provider且与注册的不同，需要重新进行模式匹配
        # If Provider is specified and different from registered, need to re-match pattern
        if specified_provider and specified_provider != info.provider:
            # 跳过注册表，直接进入自动注册流程以重新匹配正确的 Provider 配置
            # Skip registry, go to auto-registration to re-match correct Provider config
            pass
        elif parsed_date:
            # 只有日期不同，可以复用配置
            # Only date is different, can reuse config
            return ModelInfo(
                provider=info.provider,
                family=info.family,
                version=info.version,
                variant=info.variant,
                capabilities=info.capabilities,
                version_tuple=info.version_tuple,
                variant_priority=info.variant_priority,
                release_date=parsed_date,
            )
        else:
            # 完全匹配，直接返回
            # Exact match, return directly
            return info

    # 【优先级3】如果没有找到且启用自动注册，尝试自动注册
    # [Priority 3] If not found and auto-register enabled, try auto-registration
    # auto_register_model 内部会调用 match_model_pattern 进行模式匹配
    # auto_register_model internally calls match_model_pattern for pattern matching
    if auto_register:
        try:
            return auto_register_model(actual_name, specified_provider)
        except ValueError:
            # 自动注册失败，返回默认信息 / Auto-registration failed, return default information
            pass

    # 【兜底】如果没有找到，返回默认信息 / [Fallback] If not found, return default information
    provider = specified_provider or Provider.from_model_name(actual_name)
    parsed_date = parse_date_from_model_name(actual_name)

    return ModelInfo(
        provider=provider,
        family=ModelFamily.UNKNOWN,
        version="",
        variant="",
        capabilities=ModelCapabilities(),
        version_tuple=(0,),
        variant_priority=(0,),
        release_date=parsed_date,
    )
