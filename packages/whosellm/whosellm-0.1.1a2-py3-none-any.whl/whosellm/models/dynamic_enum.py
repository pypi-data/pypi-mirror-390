# filename: dynamic_enum.py
# @Time    : 2025/11/7 18:08
# @Author  : JQQ
# @Email   : jqq1716@gmail.com
# @Software: PyCharm
"""
动态枚举支持 / Dynamic enum support

允许在运行时动态添加枚举成员，同时保持类型安全
Allows dynamically adding enum members at runtime while maintaining type safety
"""

from enum import EnumMeta
from typing import Any


class DynamicEnumMeta(EnumMeta):
    """
    动态枚举元类 / Dynamic enum metaclass

    支持在运行时动态添加枚举成员
    Supports dynamically adding enum members at runtime
    """

    def __call__(
        cls,
        value: Any,
        names: Any = None,
        *,
        module: str | None = None,
        qualname: str | None = None,
        type: type | None = None,
        start: int = 1,
        boundary: Any = None,
    ) -> Any:
        """
        重写 __call__ 以支持动态创建枚举成员
        Override __call__ to support dynamic enum member creation

        如果 names 为 None，则视为获取枚举成员；否则视为创建新枚举类
        If names is None, treat as getting enum member; otherwise treat as creating new enum class
        """
        # 如果 names 不为 None，说明是在创建新的枚举类，调用父类方法
        # If names is not None, it's creating a new enum class, call parent method
        if names is not None:
            return super().__call__(
                value,
                names,
                module=module,
                qualname=qualname,
                type=type,
                start=start,
                boundary=boundary,
            )

        # 如果值已存在，返回现有成员 / If value exists, return existing member
        try:
            return super().__call__(value)
        except ValueError:
            # 如果值不存在且是字符串，动态创建新成员 / If value doesn't exist and is string, create new member
            if isinstance(value, str):
                return cls._create_member(value)
            raise

    def _create_member(cls, name: str) -> Any:
        """
        动态创建枚举成员 / Dynamically create enum member

        Args:
            name: 成员名称和值 / Member name and value

        Returns:
            新创建的枚举成员 / Newly created enum member
        """
        # 将名称转换为大写下划线格式作为枚举名 / Convert name to UPPER_SNAKE_CASE as enum name
        enum_name = name.upper().replace("-", "_")

        # 检查是否已存在 / Check if already exists
        if hasattr(cls, enum_name):
            return getattr(cls, enum_name)

        # 创建新的枚举成员 / Create new enum member
        # 对于 str 枚举，需要使用 str.__new__
        # For str enum, need to use str.__new__
        new_member = str.__new__(cls, name) if issubclass(cls, str) else object.__new__(cls)

        new_member._name_ = enum_name  # type: ignore[attr-defined]
        new_member._value_ = name  # type: ignore[attr-defined]

        # 添加到类中 / Add to class
        setattr(cls, enum_name, new_member)
        cls._member_map_[enum_name] = new_member  # type: ignore[assignment]
        cls._value2member_map_[name] = new_member  # type: ignore[assignment]
        return new_member

    def add_member(cls, name: str, value: str | None = None) -> Any:
        """
        显式添加枚举成员 / Explicitly add enum member

        Args:
            name: 枚举成员名称（大写下划线格式） / Enum member name (UPPER_SNAKE_CASE)
            value: 枚举值（默认为小写连字符格式的name） / Enum value (defaults to lowercase-with-hyphens name)

        Returns:
            新创建的枚举成员 / Newly created enum member

        Example:
            >>> ModelFamily.add_member("GEMINI", "gemini")
            >>> ModelFamily.add_member("LLAMA_3", "llama-3")
        """
        if value is None:
            value = name.lower().replace("_", "-")
        # 检查是否已存在 / Check if already exists
        if hasattr(cls, name):
            return getattr(cls, name)

        # 创建新的枚举成员 / Create new enum member
        # 对于 str 枚举，需要使用 str.__new__
        # For str enum, need to use str.__new__
        new_member = str.__new__(cls, value) if issubclass(cls, str) else object.__new__(cls)

        new_member._name_ = name  # type: ignore[attr-defined]
        new_member._value_ = value  # type: ignore[attr-defined]

        # 添加到类中 / Add to class
        setattr(cls, name, new_member)
        cls._member_map_[name] = new_member  # type: ignore[assignment]
        cls._value2member_map_[value] = new_member  # type: ignore[assignment]
        return None
