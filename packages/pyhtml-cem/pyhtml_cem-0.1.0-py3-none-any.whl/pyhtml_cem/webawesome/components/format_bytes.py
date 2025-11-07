"""
wa-format-bytes component.
"""

from typing import Literal
from pyhtml import Tag
from pyhtml.__types import ChildrenType, AttributeType


class format_bytes(Tag):
    """
    wa-format-bytes web component.

    Args:
        *children: Child elements and text content
        value: The number to format in bytes.
        unit: The type of unit to display.
        display: Determines how to display the result, e.g. "100 bytes", "100 b", or "100b".
        **attributes: Additional HTML attributes
    """
    def __init__(
        self,
        *children: ChildrenType,
        value: int | float | None = None,
        unit: Literal["byte", "bit"] | None = None,
        display: Literal["long", "short", "narrow"] | None = None,
        **attributes: AttributeType,
    ) -> None:
        # Build attributes dict, filtering out None values
        attributes = attributes.copy()
        attributes.update({
            'value': value,
            'unit': unit,
            'display': display,
        })
        # Filter out None values and False booleans, convert numbers to strings
        attributes = {
            k: str(v) if isinstance(v, (int, float)) and not isinstance(v, bool) else v
            for k, v in attributes.items()
            if v is not None and v is not False
        }
        super().__init__(*children, **attributes)

    def _get_tag_name(self) -> str:
        return "wa-format-bytes"


__all__ = [
    "format_bytes",
]