"""
Base classes and enums for the Domo entity system.

This module provides foundational classes and enhanced enums that serve as
the building blocks for all Domo entities and relationships.
"""

import abc
from dataclasses import dataclass, fields
from enum import Enum
from typing import Any, Callable, ClassVar, Optional

from ..utils.convert import convert_snake_to_pascal


class DomoEnumMixin:
    """Enhanced Enum mixin with case-insensitive lookup and default value support.

    This mixin provides case-insensitive string matching and falls back to a default
    value when no match is found. All subclasses should define a 'default' member.

    Example:
        >>> class Status(DomoEnumMixin, Enum):
        ...     ACTIVE = "active"
        ...     INACTIVE = "inactive"
        ...     default = "UNKNOWN"
        >>> Status.get("ACTIVE")  # Case insensitive
        <Status.ACTIVE: 'active'>
        >>> Status.get("invalid")
        <Status.default: 'UNKNOWN'>
    """

    @classmethod
    def get(cls, value):
        """Get enum member by case-insensitive string lookup.

        Args:
            value: String value to look up (case-insensitive)

        Returns:
            Enum member if found, otherwise the default member
        """
        if not isinstance(value, str):
            return getattr(cls, "default", None)

        # cls should be an Enum subclass at runtime
        for member in cls:  # type: ignore
            if member.name.lower() == value.lower():
                return member

        return getattr(cls, "default", None)

    @classmethod
    def _missing_(cls, value):
        """Handle missing enum values with case-insensitive fallback.

        Args:
            value: The value that wasn't found

        Returns:
            Enum member if case-insensitive match found, otherwise default
        """
        if isinstance(value, str):
            value_lower = value.lower()
            # cls should be an Enum subclass at runtime
            for member in cls:  # type: ignore
                if (
                    hasattr(member, "name")
                    and isinstance(member.name, str)
                    and member.name.lower() == value_lower
                ):
                    return member

        return getattr(cls, "default", None)


class DomoEnum(DomoEnumMixin, Enum):
    default = "UNKNOWN"


@dataclass
class DomoBase(abc.ABC):
    """Abstract base class for all Domo objects.

    This class serves as the foundation for all Domo entities and managers,
    providing a common interface and ensuring consistent implementation
    across the inheritance hierarchy.

    Property Serialization Extension:
        Subclasses may declare a tuple ``__serialize_properties__`` containing
        property (or attribute) names that should be appended to the default
        dataclass field serialization performed by :meth:`to_dict`.

        Example::

            from typing import ClassVar

            @dataclass
            class MyEntity(DomoBase):
                id: str
                value: int
                __serialize_properties__: ClassVar[tuple] = ("display_url",)

                @property
                def display_url(self) -> str:  # will be included automatically
                    return f"https://example.com/{self.id}"

            MyEntity(id="123", value=5).to_dict()
            # {'id': '123', 'value': 5, 'displayUrl': 'https://example.com/123'}

            MyEntity(id="123", value=5).to_dict(return_snake_case=True)
            # {'id': '123', 'value': 5, 'display_url': 'https://example.com/123'}

        Notes:
            * Only fields with ``repr=True`` and non-None values are emitted.
            * Properties listed in ``__serialize_properties__`` are always included (even if None).
            * Properties that raise exceptions are skipped safely.
            * Dataclass fields take precedence over property names with the same identifier.
            * Use ``return_snake_case=True`` to get snake_case keys instead of camelCase.
    """

    __serialize_properties__: ClassVar[tuple[str, ...]] = ()

    def to_dict(
        self, override_fn: Optional[Callable] = None, return_snake_case: bool = False
    ) -> dict:
        """Convert dataclass to dictionary with camelCase or snake_case keys, excluding fields with repr=False.

        Args:
            override_fn: Optional callable that receives ``self`` and returns the final dictionary.
                        Bypasses default behavior entirely.
            return_snake_case: If True, return keys in snake_case. If False (default), return camelCase.

        Returns:
            dict: Dictionary with camelCase (default) or snake_case keys and corresponding values.
        """
        if override_fn:
            return override_fn(self)

        # Start with dataclass fields (only include fields with repr=True)
        result: dict[str, Any] = {}
        for fld in fields(self):
            if fld.repr and getattr(self, fld.name) is not None:
                key = (
                    fld.name if return_snake_case else convert_snake_to_pascal(fld.name)
                )
                result[key] = getattr(self, fld.name)

        # Append whitelisted properties / attributes
        if getattr(self, "__serialize_properties__", None):
            for prop_name in self.__serialize_properties__:  # type: ignore[attr-defined]
                # Skip if it's already a dataclass field
                if any(f.name == prop_name for f in fields(self)):
                    continue
                try:
                    value = getattr(self, prop_name)
                    # Include properties even if None to ensure consistent DataFrame columns
                    key = (
                        prop_name
                        if return_snake_case
                        else convert_snake_to_pascal(prop_name)
                    )
                    result[key] = value
                except (
                    Exception
                ):  # pragma: no cover - defensive; skip failing properties
                    continue

        return result


__all__ = [
    "DomoEnum",
    "DomoEnumMixin",
    "DomoBase",
]
