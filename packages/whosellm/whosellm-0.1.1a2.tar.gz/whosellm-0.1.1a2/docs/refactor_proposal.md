# 模型家族配置重构方案 / Model Family Configuration Refactoring Proposal

## 🎯 目标 / Goals

1. **统一配置** - 每个模型家族的所有信息集中在一个配置类中
2. **按提供商组织** - 降低单个文件的复杂度，便于维护
3. **自动生成索引** - 从配置自动生成查询所需的数据结构
4. **易于扩展** - 添加新家族只需创建配置，无需修改多处

## 📁 新的文件结构

```
llmeta/models/
├── base.py                    # 核心枚举和数据类
├── config.py                  # 模型家族配置类
├── registry.py                # 统一注册表和查询接口
├── families/                  # 模型家族配置目录（按提供商组织）
│   ├── __init__.py           # 自动导入所有配置
│   ├── openai.py             # OpenAI 所有模型家族
│   ├── anthropic.py          # Anthropic 所有模型家族
│   ├── zhipu.py              # 智谱 所有模型家族
│   ├── alibaba.py            # 阿里 所有模型家族
│   ├── deepseek.py           # DeepSeek 所有模型家族
│   └── ...
└── __init__.py
```

## 💡 核心设计

### 1. 配置类定义 (`config.py`)

```python
# -*- coding: utf-8 -*-
# filename: config.py
# @Time    : 2025/11/7 17:32
# @Author  : JQQ
# @Email   : jqq1716@gmail.com
# @Software: PyCharm
"""
模型家族配置类 / Model family configuration class
"""

from dataclasses import dataclass, field
from whosellm.models.base import ModelFamily
from whosellm.provider import Provider
from whosellm.capabilities import ModelCapabilities


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
    patterns: list[str]

    # 默认值 / Defaults
    version_default: str = "1.0"

    # 默认能力 / Default capabilities
    capabilities: ModelCapabilities = field(default_factory = ModelCapabilities)

    # 预注册的特定模型（可选） / Pre-registered specific models (optional)
    # 格式: {model_name: (version, variant, custom_capabilities)}
    specific_models: dict[str, tuple[str, str, ModelCapabilities | None]] = field(default_factory = dict)

    def __post_init__(self):
        """注册到全局注册表 / Register to global registry"""
        from whosellm.models.registry import register_family_config
        register_family_config(self)
```

### 2. 统一注册表 (`registry.py`)

```python
# -*- coding: utf-8 -*-
# filename: registry.py
# @Time    : 2025/11/7 17:32
# @Author  : JQQ
# @Email   : jqq1716@gmail.com
# @Software: PyCharm
"""
统一模型注册表 / Unified model registry
"""

from typing import Any
from whosellm.models.base import ModelFamily, ModelInfo
from whosellm.models.config import ModelFamilyConfig
from whosellm.provider import Provider
from whosellm.capabilities import ModelCapabilities

# 核心注册表：所有模型家族配置 / Core registry: all model family configs
_FAMILY_CONFIGS: dict[ModelFamily, ModelFamilyConfig] = {}

# 缓存：模型名称 -> ModelInfo / Cache: model_name -> ModelInfo
_MODEL_CACHE: dict[str, ModelInfo] = {}


def register_family_config(config: ModelFamilyConfig) -> None:
    """
    注册模型家族配置 / Register model family configuration
    
    Args:
        config: 模型家族配置 / Model family configuration
    """
    _FAMILY_CONFIGS[config.family] = config


def get_family_config(family: ModelFamily) -> ModelFamilyConfig | None:
    """
    获取模型家族配置 / Get model family configuration
    
    Args:
        family: 模型家族 / Model family
        
    Returns:
        ModelFamilyConfig | None: 配置或None / Config or None
    """
    return _FAMILY_CONFIGS.get(family)


def get_default_provider(family: ModelFamily) -> Provider | None:
    """
    获取模型家族的默认Provider / Get default provider for model family
    
    Args:
        family: 模型家族 / Model family
        
    Returns:
        Provider | None: 默认Provider或None / Default provider or None
    """
    config = _FAMILY_CONFIGS.get(family)
    return config.provider if config else None


def get_default_capabilities(family: ModelFamily) -> ModelCapabilities:
    """
    获取模型家族的默认能力 / Get default capabilities for model family
    
    Args:
        family: 模型家族 / Model family
        
    Returns:
        ModelCapabilities: 默认能力 / Default capabilities
    """
    config = _FAMILY_CONFIGS.get(family)
    return config.capabilities if config else ModelCapabilities()


def get_all_patterns() -> list[tuple[ModelFamily, Provider, list[str], str]]:
    """
    获取所有命名模式 / Get all naming patterns
    
    Returns:
        list: [(family, provider, patterns, version_default), ...]
    """
    return [
        (config.family, config.provider, config.patterns, config.version_default)
        for config in _FAMILY_CONFIGS.values()
    ]


def match_model_pattern(model_name: str) -> dict[str, Any] | None:
    """
    匹配模型名称到模式 / Match model name to pattern
    
    Args:
        model_name: 模型名称 / Model name
        
    Returns:
        dict | None: 匹配结果或None / Match result or None
    """
    import parse

    model_lower = model_name.lower()

    # 遍历所有家族配置 / Iterate all family configs
    for config in _FAMILY_CONFIGS.values():
        for pattern in config.patterns:
            result = parse.parse(pattern, model_lower)
            if result:
                # 转换为字典并添加默认值 / Convert to dict and add defaults
                matched: dict[str, Any] = dict(result.named)
                if not matched.get("version"):
                    matched["version"] = config.version_default
                matched["family"] = config.family
                matched["provider"] = config.provider
                return matched

    return None


def list_all_families() -> list[ModelFamily]:
    """
    列出所有已注册的模型家族 / List all registered model families
    
    Returns:
        list[ModelFamily]: 模型家族列表 / List of model families
    """
    return list(_FAMILY_CONFIGS.keys())


def get_family_info(family: ModelFamily) -> dict[str, Any]:
    """
    获取模型家族的完整信息 / Get complete information for model family
    
    Args:
        family: 模型家族 / Model family
        
    Returns:
        dict: 家族信息 / Family information
    """
    config = _FAMILY_CONFIGS.get(family)
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
```

### 3. 提供商配置文件示例 (`families/openai.py`)

```python
# -*- coding: utf-8 -*-
# filename: openai.py
# @Time    : 2025/11/7 17:32
# @Author  : JQQ
# @Email   : jqq1716@gmail.com
# @Software: PyCharm
"""
OpenAI 模型家族配置 / OpenAI model family configurations
"""

from whosellm.models.base import ModelFamily
from whosellm.models.config import ModelFamilyConfig
from whosellm.provider import Provider
from whosellm.capabilities import ModelCapabilities

# ============================================================================
# GPT-4 系列 / GPT-4 Series
# ============================================================================

GPT_4 = ModelFamilyConfig(
    family = ModelFamily.GPT_4,
    provider = Provider.OPENAI,
    version_default = "4.0",

    patterns = [
        "gpt-4o-{variant:variant}-{year:4d}-{month:2d}-{day:2d}",  # gpt-4o-mini-2024-07-18
        "gpt-4o-{variant:variant}",  # gpt-4o-mini
        "gpt-4-{variant:variant}-{year:4d}-{month:2d}-{day:2d}",  # gpt-4-turbo-2024-04-09
        "gpt-4-{variant:variant}-{mmdd:4d}",  # gpt-4-0125-preview
        "gpt-4-{variant:variant}",  # gpt-4-turbo, gpt-4-plus
        "gpt-4o",  # gpt-4o (base)
        "gpt-4",  # gpt-4 (base)
    ],

    capabilities = ModelCapabilities(
        supports_function_calling = True,
        supports_streaming = True,
        max_tokens = 8192,
        context_window = 128000,
    ),

    # 可选：预注册特定模型 / Optional: pre-register specific models
    specific_models = {
        "gpt-4o": ("4.0", "base", None),  # 使用默认能力
        "gpt-4o-mini": ("4.0", "mini", ModelCapabilities(
            supports_function_calling = True,
            supports_streaming = True,
            max_tokens = 16384,
            context_window = 128000,
        )),
    },
)

# ============================================================================
# GPT-3.5 系列 / GPT-3.5 Series
# ============================================================================

GPT_3_5 = ModelFamilyConfig(
    family = ModelFamily.GPT_3_5,
    provider = Provider.OPENAI,
    version_default = "3.5",

    patterns = [
        "gpt-3.5-{variant:variant}-{year:4d}-{month:2d}-{day:2d}",
        "gpt-3.5-{variant:variant}",
        "gpt-3.5",
    ],

    capabilities = ModelCapabilities(
        supports_function_calling = True,
        supports_streaming = True,
        max_tokens = 4096,
        context_window = 16385,
    ),
)

# ============================================================================
# O1 系列 / O1 Series
# ============================================================================

O1 = ModelFamilyConfig(
    family = ModelFamily.O1,
    provider = Provider.OPENAI,
    version_default = "1.0",

    patterns = [
        "o1-{variant:variant}-{year:4d}-{month:2d}-{day:2d}",
        "o1-{variant:variant}",
        "o1",
    ],

    capabilities = ModelCapabilities(
        supports_thinking = True,  # O1 支持推理
        supports_function_calling = False,
        supports_streaming = False,
        max_tokens = 100000,
        context_window = 200000,
    ),
)

# ============================================================================
# O3 系列 / O3 Series
# ============================================================================

O3 = ModelFamilyConfig(
    family = ModelFamily.O3,
    provider = Provider.OPENAI,
    version_default = "3.0",

    patterns = [
        "o3-{variant:variant}-{year:4d}-{month:2d}-{day:2d}",
        "o3-{variant:variant}",
        "o3",
    ],

    capabilities = ModelCapabilities(
        supports_thinking = True,
        supports_function_calling = False,
        supports_streaming = False,
        max_tokens = 100000,
        context_window = 200000,
    ),
)
```

### 4. 提供商配置文件示例 (`families/zhipu.py`)

```python
# -*- coding: utf-8 -*-
# filename: zhipu.py
# @Time    : 2025/11/7 17:32
# @Author  : JQQ
# @Email   : jqq1716@gmail.com
# @Software: PyCharm
"""
智谱 AI 模型家族配置 / Zhipu AI model family configurations
"""

from whosellm.models.base import ModelFamily
from whosellm.models.config import ModelFamilyConfig
from whosellm.provider import Provider
from whosellm.capabilities import ModelCapabilities

# ============================================================================
# GLM-4V 系列（视觉模型） / GLM-4V Series (Vision Model)
# ============================================================================

GLM_4V = ModelFamilyConfig(
    family = ModelFamily.GLM_4V,
    provider = Provider.ZHIPU,
    version_default = "4.0",

    patterns = [
        "glm-4v-{variant:variant}-{mmdd:4d}",  # glm-4v-plus-0111
        "glm-4v-{variant:variant}",  # glm-4v-plus, glm-4v-flash
        "glm-4v",  # glm-4v (base)
    ],

    capabilities = ModelCapabilities(
        supports_vision = True,
        supports_function_calling = True,
        supports_streaming = True,
        max_tokens = 8192,
        context_window = 128000,
        max_image_size_mb = 10.0,
        max_image_pixels = (4096, 4096),
    ),
)

# ============================================================================
# GLM-4 系列 / GLM-4 Series
# ============================================================================

GLM_4 = ModelFamilyConfig(
    family = ModelFamily.GLM_4,
    provider = Provider.ZHIPU,
    version_default = "4.0",

    patterns = [
        "glm-4-{variant:variant}-{year:4d}-{month:2d}-{day:2d}",
        "glm-4-{variant:variant}",
        "glm-4",
    ],

    capabilities = ModelCapabilities(
        supports_function_calling = True,
        supports_streaming = True,
        max_tokens = 8192,
        context_window = 128000,
    ),
)

# ============================================================================
# GLM-3 系列 / GLM-3 Series
# ============================================================================

GLM_3 = ModelFamilyConfig(
    family = ModelFamily.GLM_3,
    provider = Provider.ZHIPU,
    version_default = "3.0",

    patterns = [
        "glm-3-{variant:variant}",
        "glm-3",
    ],

    capabilities = ModelCapabilities(
        supports_function_calling = True,
        supports_streaming = True,
        max_tokens = 8192,
        context_window = 32000,
    ),
)
```

### 5. 自动导入 (`families/__init__.py`)

```python
# -*- coding: utf-8 -*-
# filename: __init__.py
# @Time    : 2025/11/7 17:32
# @Author  : JQQ
# @Email   : jqq1716@gmail.com
# @Software: PyCharm
"""
自动导入所有模型家族配置 / Auto-import all model family configurations
"""

# 导入所有提供商的配置，触发自动注册
# Import all provider configurations to trigger auto-registration
from whosellm.models.families import (
    openai,
    anthropic,
    zhipu,
    alibaba,
    deepseek,
    # ... 其他提供商
)

__all__ = [
    "openai",
    "anthropic",
    "zhipu",
    "alibaba",
    "deepseek",
]
```

## ✅ 优势 / Advantages

### 1. **配置集中** / Centralized Configuration
- 每个模型家族的所有信息在一个地方
- 添加新家族只需创建一个配置对象

### 2. **按提供商组织** / Organized by Provider
- 每个文件只包含一个提供商的配置
- 文件大小可控，易于维护
- 清晰的职责划分

### 3. **自动生成索引** / Auto-generated Indexes
- 不需要手动维护多个全局字典
- 查询函数从配置自动生成所需数据

### 4. **易于扩展** / Easy to Extend
```python
# 添加新家族只需：
GEMINI = ModelFamilyConfig(
    family=ModelFamily.GEMINI,
    provider=Provider.GOOGLE,
    patterns=["gemini-{variant:variant}"],
    capabilities=ModelCapabilities(...),
)
```

### 5. **类型安全** / Type Safe
- 使用 dataclass，IDE 自动补全
- mypy 类型检查

### 6. **可测试性** / Testability

```python
import whosellm.models.families.openai.openai_gpt_4


def test_gpt4_config():
    from whosellm.models.families.openai.openai_gpt_4 import GPT_4
    assert GPT_4.family == whosellm.models.families.openai.openai_gpt_4.GPT_4
    assert GPT_4.provider == Provider.OPENAI
    assert "gpt-4-{variant:variant}" in GPT_4.patterns
```

## 🔄 迁移步骤 / Migration Steps

### 阶段 1：创建新结构（不破坏现有代码）
1. 创建 `config.py` 和 `registry.py`
2. 创建 `families/` 目录
3. 迁移配置到新文件

### 阶段 2：更新查询接口
1. 修改 `get_model_info()` 使用新的 `registry.match_model_pattern()`
2. 修改 `auto_register_model()` 使用新的查询函数
3. 保持向后兼容

### 阶段 3：清理旧代码
1. 删除旧的全局字典
2. 删除 `patterns.py`（功能已集成到 `registry.py`）
3. 更新测试

## 📊 对比 / Comparison

### 当前方案 / Current Approach
```python
# 需要在 5 个地方添加配置
class ModelFamily(str, Enum):
    GEMINI = "gemini"

FAMILY_DEFAULT_PROVIDER = {..., ModelFamily.GEMINI: Provider.GOOGLE}
FAMILY_DEFAULT_CAPABILITIES = {..., ModelFamily.GEMINI: ModelCapabilities(...)}
MODEL_PATTERNS = [..., ModelPattern(...)]
# 还可能需要在 openai.py 等文件中注册
```

### 新方案 / New Approach
```python
# 只需在一个地方添加配置
# families/google.py
GEMINI = ModelFamilyConfig(
    family=ModelFamily.GEMINI,
    provider=Provider.GOOGLE,
    patterns=["gemini-{variant:variant}"],
    capabilities=ModelCapabilities(...),
)
```

## 🎯 推荐实施 / Recommended Implementation

我建议采用这个方案，因为：

1. **维护成本降低** - 配置集中，修改方便
2. **扩展性好** - 添加新家族非常简单
3. **代码清晰** - 按提供商组织，职责明确
4. **性能无损** - 配置在启动时加载，运行时查询效率相同
5. **向后兼容** - 可以逐步迁移，不破坏现有代码

你觉得这个方案如何？我可以开始实施重构。
