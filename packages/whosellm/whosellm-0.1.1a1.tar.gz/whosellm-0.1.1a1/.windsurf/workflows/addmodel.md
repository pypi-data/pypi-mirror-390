---
description: 添加与修正模型配置
---

目前的模型配置定义参考：

from dataclasses import dataclass, field

import parse  # type: ignore[import-untyped]

from llmeta.capabilities import ModelCapabilities
from llmeta.models.base import ModelFamily
from llmeta.provider import Provider


@dataclass
class SpecificModelConfig:
    """
    特定模型配置 / Specific model configuration

    用于预注册特定模型的详细配置
    Used for pre-registering detailed configuration for specific models
    """

    # 模型版本 / Model version
    version: str

    # 模型变体 / Model variant
    variant: str

    # 自定义能力（可选） / Custom capabilities (optional)
    capabilities: ModelCapabilities | None = None

    # 子命名模式（可选） / Sub-patterns (optional)
    # 必须是父 patterns 的子集 / Must be a subset of parent patterns
    patterns: list[str] = field(default_factory=list)


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
    capabilities: ModelCapabilities = field(default_factory=ModelCapabilities)

    # 预注册的特定模型（可选） / Pre-registered specific models (optional)
    # 格式: {model_name: SpecificModelConfig}
    # Format: {model_name: SpecificModelConfig}
    specific_models: dict[str, SpecificModelConfig] = field(default_factory=dict)

---

目前已经有相应的添加模式在 llmeta/models/families

但目前的配置并不是非常正常，目前的配置数据很多是Mock数据。我会复制给你官网相应的真实配置文档，你根据这个配置文档，来修改当前的Mock数据或者添加新的配置数据。

我给出的文档中会尽可能多出现一些示例模型名称，你需要总结其模式。另外，模型的能力我会给出描述，你需要配置Capabilities。

1. 我每次会提供一个（有时候可能有多个）从官网复制的模型说明，你需要根据提供内容来判断在当前哪个Provider提供丰富对应的配置，如果我提供的模型已经在配置中存在，则检查其capabilities是否正确。需要注意，你可以新建SpecialModels，或者新建模型家族，模型家族的分类有时候不一定非得按品牌来分，比如GPT模型众多，每个版本都形成一个独立家族，而有些品牌模型量比较少，可以一个品牌一个家族，不同版本区分。
2. 完成配置后你需要自检，Patterns不要有冲突，因为匹配模式的时候有顺序，优先SpecialModels，然后按主配置来，SpecialsModels又按顺序尝试，因此要注意避免提前被匹配的情况。
3. 测试用例需要在 tests/ 目录下，映射源代码目录结构。可以参考 @tests/models/families/test_gpt5.py。注意的时候注意写一些空间被错误捕获的Case来验证，因为目前的经验来看，非常容易因为Parsed模板提前捕获导致错误匹配。
4. 每次添加或者修改配置后，会有些之前的测试用例无法通过，因为毕竟修改了配置。你需要在每次修改完配置后运行 uv run poe test。查看无法通过的用例，如果是因为测试数据过时的原因，则修复测试数据，如果是因为配置逻辑问题（比如Patterns顺序，或者SpcialModels顺序造成的），则修复配置