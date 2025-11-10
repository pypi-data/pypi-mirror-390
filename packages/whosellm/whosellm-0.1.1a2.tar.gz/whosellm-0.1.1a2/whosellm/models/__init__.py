# filename: __init__.py
# @Time    : 2025/11/7 17:40
# @Author  : JQQ
# @Email   : jqq1716@gmail.com
"""
模型信息注册表 / Model information registry
"""

# 导入家族配置以触发自动注册 / Import family configs to trigger auto-registration
from whosellm.models import families

# 导入核心函数 / Import core functions
from whosellm.models.base import (
    ModelInfo,
    auto_register_model,
    get_model_info,
    infer_model_family,
    register_model,
)

__all__ = [
    "ModelInfo",
    "auto_register_model",
    "families",
    "get_model_info",
    "infer_model_family",
    "register_model",
]
