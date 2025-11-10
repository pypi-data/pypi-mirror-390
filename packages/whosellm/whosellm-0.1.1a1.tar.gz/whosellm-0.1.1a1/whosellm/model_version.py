# @Time    : 2025/11/7 13:56
# @Author  : JQQ
# @Email   : jqq1716@gmail.com
# @Software: PyCharm
"""
模型版本管理 / Model version management
"""

import functools
from dataclasses import dataclass, field
from datetime import date
from typing import Any

from whosellm.capabilities import ModelCapabilities
from whosellm.models.base import ModelFamily, get_model_info
from whosellm.provider import Provider


@functools.total_ordering
@dataclass
class LLMeta:
    """
    LLM 元数据类 / LLM metadata class

    支持从单个字符串初始化，自动识别提供商、版本和型号
    Supports initialization from a single string, automatically recognizing provider, version, and model
    """

    model_name: str
    provider: Provider = Provider.UNKNOWN
    family: ModelFamily = ModelFamily.UNKNOWN
    version: str = ""
    variant: str = ""
    capabilities: ModelCapabilities = field(default_factory=ModelCapabilities)
    release_date: date | None = None
    _version_tuple: tuple[int, ...] = field(default_factory=tuple, repr=False)
    _variant_priority: tuple[int, ...] = field(default_factory=tuple, repr=False)

    def __post_init__(self) -> None:
        """
        初始化后的处理 / Post-initialization processing

        自动从模型名称解析并填充其他字段
        Automatically parse and populate other fields from model name
        """
        # 从模型名称获取信息 / Get information from model name
        model_info = get_model_info(self.model_name)

        # 如果字段为默认值，则使用解析的值 / Use parsed values if fields are default values
        if self.provider == Provider.UNKNOWN:
            self.provider = model_info.provider
        if self.family == ModelFamily.UNKNOWN:
            self.family = model_info.family
        if not self.version:
            self.version = model_info.version
        if not self.variant:
            self.variant = model_info.variant
        # 检查 capabilities 是否为默认的空对象 / Check if capabilities is default empty object
        if self.capabilities == ModelCapabilities():
            self.capabilities = model_info.capabilities
        if not self.release_date:
            self.release_date = model_info.release_date
        # 设置版本元组和型号优先级用于比较 / Set version tuple and variant priority for comparison
        self._version_tuple = model_info.version_tuple
        self._variant_priority = model_info.variant_priority

    def __str__(self) -> str:
        """字符串表示 / String representation"""
        return self.model_name

    def __repr__(self) -> str:
        """详细表示 / Detailed representation"""
        return f"ModelVersion(model_name='{self.model_name}', provider={self.provider}, version='{self.version}')"

    def __eq__(self, other: object) -> bool:
        """
        相等比较 / Equality comparison

        同一模型家族的模型才能比较，比较版本、型号优先级和日期
        Only models from the same family can be compared, comparing version, variant priority and date
        """
        if not isinstance(other, LLMeta):
            return NotImplemented

        if self.family != other.family:
            return False

        return (
            self._version_tuple == other._version_tuple
            and self._variant_priority == other._variant_priority
            and self.release_date == other.release_date
        )

    def __lt__(self, other: object) -> bool:
        """
        小于比较 / Less than comparison

        同一模型家族的模型才能比较，先比较版本，再比较型号优先级，最后比较日期
        Only models from the same family can be compared, first compare version, then variant priority, finally date
        """
        if not isinstance(other, LLMeta):
            return NotImplemented

        if self.family != other.family:
            raise ValueError(
                f"无法比较不同模型家族的模型: {self.family} vs {other.family} / "
                f"Cannot compare models from different families: {self.family} vs {other.family}",
            )

        # 先比较版本 / First compare version
        if self._version_tuple != other._version_tuple:
            return self._version_tuple < other._version_tuple

        # 版本相同时，比较型号优先级 / When versions are the same, compare variant priority
        if self._variant_priority != other._variant_priority:
            return self._variant_priority < other._variant_priority

        # 型号优先级相同时，比较日期 / When variant priorities are the same, compare date
        # 没有日期的模型认为是最新的（一般指向latest版本） / Models without date are considered newest (usually pointing to latest)
        if self.release_date is None and other.release_date is None:
            return False  # 两者都没有日期，认为相等 / Both have no date, consider equal
        if self.release_date is None:
            return False  # self 没有日期，认为是最新的 / self has no date, consider newest
        if other.release_date is None:
            return True  # other 没有日期，认为是最新的 / other has no date, consider newest

        return self.release_date < other.release_date

    def validate_params(self, params: dict[str, Any]) -> dict[str, Any]:
        """
        验证并调整参数 / Validate and adjust parameters

        使用 VRL 脚本进行参数验证和调整
        Use VRL script for parameter validation and adjustment

        Args:
            params: 原始参数 / Original parameters

        Returns:
            dict: 验证后的参数 / Validated parameters
        """
        # TODO: 实现基于 VRL 的参数验证
        # TODO: Implement VRL-based parameter validation
        return params

    @property
    def supports_multimodal(self) -> bool:
        """
        是否支持多模态 / Whether multimodal is supported

        Returns:
            bool: 支持任意多模态输入即返回True / Returns True if any multimodal input is supported
        """
        return any(
            [
                self.capabilities.supports_vision,
                self.capabilities.supports_audio,
                self.capabilities.supports_video,
                self.capabilities.supports_pdf,
            ],
        )
