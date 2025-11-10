# LLMeta

一个统一的大语言模型版本和能力管理库 / A unified LLM model version and capability management library

## 背景 / Background

今天又是被模型名字支配的一天：同一个模型家族被叫做 `pro`、`plus`、`flash`、`turbo`，还要兼容厂商的“周年纪念版 0111”。想知道它到底能不能看图、能不能撑 200M 的视频，只能狂翻文档。**LLMeta** 就是给这群被命名轰炸的开发者准备的避难所：我们尝试统一这些膨胀的名字、聚合能力信息，让你不必再猜。

- **命名没有规律**：`gpt-4o-mini`、`glm-4v-plus-0111`、`deepseek-chat`… 你永远猜不到下一个名字会长什么样。
- **能力各说各话**：上下文长度、视觉/音频/视频支持、上传大小限制，分散在不同公告里。
- **需求只增不减**：业务想快速切换模型，开发者只能手动踩坑。

我们希望把这些信息塞进同一个入口，一次性告诉你“它是谁、它能做什么、它有哪些限制”。

## 特性 / Features

1. **简单初始化** - 仅需要一个字符串即可完成模型配置的初始化
2. **模型家族管理** - 区分模型家族（ModelFamily）和提供商（Provider），同一模型家族可能由多个Provider提供
3. **型号优先级比较** - 支持同一家族下不同型号的智能比较（如 gpt-4o-mini < gpt-4 < gpt-4-turbo < gpt-4o）
4. **Provider指定** - 支持 `Provider::ModelName` 语法来指定特定的Provider
5. **能力范围说明** - 提供模型能力范围说明：
   - 是否支持 thinking（reasoning）模式
   - 是否支持图片
   - 是否支持音频
   - 是否支持视频
   - 是否支持 PDF
   - 各类资源的大小和格式限制
6. **参数验证** - 针对具体模型，提供请求参数验证的可选实现，基于 VRL 脚本语言自动整改参数

## 安装 / Installation

```bash
# 使用 uv
uv add whosellm

# 使用 pip
pip install whosellm
```

## 快速开始 / Quick Start

### 基础用法 / Basic Usage

```python
from whosellm import LLMeta

# 初始化模型版本
model = LLMeta("glm-4v-plus")

print(model.provider)                  # Provider.ZHIPU
print(model.family)                    # ModelFamily.GLM_VISION
print(model.capabilities.supports_vision)  # True
print(model.capabilities.max_video_size_mb)  # 20.0

# 参数验证（当前版本尚未实现）
validated_params = model.validate_params(your_params)
```

### 非法名称也不会炸 / Lenient on Unknown Names

我们不想打断你的流程，即便名称不在我们的数据库里也能返回一个「未知模型占位符」。

```python
from whosellm import LLMeta, ModelFamily, Provider

mystery = LLMeta("mystery-dragon-9000")
print(mystery.provider)  # Provider.UNKNOWN
print(mystery.family)    # ModelFamily.UNKNOWN
```

你仍然可以继续工作，例如根据 `UNKNOWN` 来触发降级逻辑，或者回头补充配置。

### 型号优先级比较 / Variant Priority Comparison

```python
from whosellm import LLMeta

# GPT-4 系列型号比较: mini < base < turbo < omni
gpt4o_mini = LLMeta("gpt-4o-mini")
gpt4_base = LLMeta("gpt-4")
gpt4_turbo = LLMeta("gpt-4-turbo")
gpt4o = LLMeta("gpt-4o")

print(gpt4o_mini < gpt4_base)  # True
print(gpt4_base < gpt4_turbo)  # True
print(gpt4_turbo < gpt4o)  # True

# GLM-4V 系列型号比较: flash < base < plus < plus-0111
glm4v_flash = LLMeta("glm-4v-flash")
glm4v_plus = LLMeta("glm-4v-plus")
glm4v_plus_0111 = LLMeta("glm-4v-plus-0111")

print(glm4v_flash < glm4v_plus)  # True
print(glm4v_plus < glm4v_plus_0111)  # True
```

## 自助编写模型配置 / Bring Your Own Config

模型实在太多，我们的默认配置肯定有遗漏。如果 `LLMeta("new-cool-model-pro")` 返回了 `UNKNOWN`，可以像下面这样写一段配置直接扩充注册表：

```python
from whosellm import LLMeta, ModelFamily, Provider
from whosellm.capabilities import ModelCapabilities
from whosellm.models.config import ModelFamilyConfig, SpecificModelConfig

# 动态扩展家族与厂商（DynamicEnumMeta 支持）
ModelFamily.add_member("MY_LAB", "my-lab")
Provider.add_member("MY_CORP", "my-corp")

# 注册自己的模型家族
ModelFamilyConfig(
    family = ModelFamily.MY_LAB,
    provider = Provider.MY_CORP,
    patterns = ["my-corp-{version}-{variant}"],
    version_default = "1.0",
    specific_models = {
        "my-corp-1.0-pro": SpecificModelConfig(
            version_default = "1.0",
            variant_default = "pro",
            capabilities = ModelCapabilities(
                supports_vision = True,
                max_video_size_mb = 200,
            ),
        ),
    },
)

print(LLMeta("my-corp-1.0-pro").capabilities.supports_vision)  # True
```

这样就能即时生效，无需 fork 项目。也欢迎把这段配置通过 PR 分享给我们！

### 模型家族与Provider / Model Family and Provider

```python
from whosellm import LLMeta, ModelFamily, Provider

# 检查模型家族
gpt4 = LLMeta("gpt-4")
gpt4_turbo = LLMeta("gpt-4-turbo")

print(gpt4.family == gpt4_turbo.family)  # True (都是 GPT_4 家族)
print(gpt4.family)  # ModelFamily.GPT_4

# 使用 Provider::ModelName 语法指定Provider
model1 = LLMeta("gpt-4")  # 使用默认Provider
model2 = LLMeta("openai::gpt-4")  # 显式指定Provider
model3 = LLMeta("Tencent::deepseek-chat")  # 指定不同的Provider

print(model1.provider)  # Provider.OPENAI
print(model2.provider)  # Provider.OPENAI
print(model3.provider)  # Provider.TENCENT
```

### 实际应用场景 / Practical Usage

```python
from whosellm import LLMeta

# 场景1: 选择支持视觉的最便宜模型
available_models = [
    LLMeta("gpt-4o-mini"),
    LLMeta("gpt-4"),
    LLMeta("gpt-4-turbo"),
    LLMeta("gpt-4o"),
]

vision_models = [m for m in available_models if m.capabilities.supports_vision]
cheapest_vision = min(vision_models)  # 自动选择最便宜的（优先级最低的）
print(f"推荐模型: {cheapest_vision.model_name}")  # gpt-4o-mini

# 场景2: 检查模型升级
current = LLMeta("glm-4v-plus")
new = LLMeta("glm-4v-plus-0111")

if new > current:
    print("这是一个升级版本")
    print(f"视频大小限制提升: {current.capabilities.max_video_size_mb}MB → {new.capabilities.max_video_size_mb}MB")
```

更多示例请参考 [examples/advanced_usage.py](examples/advanced_usage.py)

## 提交 Issue / Request Features

如果你遇到未覆盖的模型家族、想要新的能力字段，或发现文档里有你踩过的坑，欢迎在 Issue 里告诉我们。描述清楚模型名称、厂商、期望的能力字段即可，我们会尽量快地补上（或邀请你一起完成）。

## 贡献指南 / Contribution Guide

- **准备环境**：`uv sync --extra dev --extra test` 或直接执行 `poe dev`。
- **格式化代码**：`poe fmt`（等价于 `poe format`）。
- **代码检查**：提交前执行 `poe lint`，若只想静态检查可使用 `poe check`。
- **类型检查**：`poe typecheck` 或 `poe mypy` 保证静态类型安全。
- **测试全家桶**：`poe test` 跑单元 + 集成测试，`poe test-cov` 查看覆盖率，`poe qa` 一条命令跑完所有质量检查。
- **示例与清理**：`poe example` 运行示例代码，`poe clean` 清理缓存。

版本管理依旧使用 `bump-my-version`：`bump-my-version bump patch|minor|major`。

## 许可证 / License

MIT License - 详见 [LICENSE](LICENSE) 文件

## 作者 / Author

JQQ <jqq1716@gmail.com>
