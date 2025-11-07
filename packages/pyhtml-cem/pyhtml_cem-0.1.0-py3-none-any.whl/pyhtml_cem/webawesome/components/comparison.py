"""
wa-comparison component.
"""

from typing import Literal
from pyhtml import Tag
from pyhtml.__types import ChildrenType, AttributeType


class comparison(Tag):
    """
    wa-comparison web component.

    Args:
        *children: Child elements and text content
        position: The position of the divider as a percentage.
        **attributes: Additional HTML attributes

    Slots:
        before: The before content, often an `<img>` or `<svg>` element.
        after: The after content, often an `<img>` or `<svg>` element.
        handle: The icon used inside the handle.
    """
    def __init__(
        self,
        *children: ChildrenType,
        position: int | float | None = None,
        **attributes: AttributeType,
    ) -> None:
        # Build attributes dict, filtering out None values
        attributes = attributes.copy()
        attributes.update({
            'position': position,
        })
        # Filter out None values and False booleans, convert numbers to strings
        attributes = {
            k: str(v) if isinstance(v, (int, float)) and not isinstance(v, bool) else v
            for k, v in attributes.items()
            if v is not None and v is not False
        }
        super().__init__(*children, **attributes)

    def _get_tag_name(self) -> str:
        return "wa-comparison"


__all__ = [
    "comparison",
]