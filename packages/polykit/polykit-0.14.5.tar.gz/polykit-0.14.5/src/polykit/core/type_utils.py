from __future__ import annotations

from typing import Any, TypeAliasType, TypeGuard


def get_args(type_obj: Any) -> tuple[Any, ...]:
    """Get type arguments from any type object, handling type aliases automatically."""
    from typing import get_args as typing_get_args

    if isinstance(type_obj, TypeAliasType):
        return typing_get_args(type_obj.__value__)
    return typing_get_args(type_obj)


def is_literal(value: Any, literal_type: Any) -> TypeGuard[Any]:
    """Verify if a value is of a specific Literal type."""
    return value in get_args(literal_type)
