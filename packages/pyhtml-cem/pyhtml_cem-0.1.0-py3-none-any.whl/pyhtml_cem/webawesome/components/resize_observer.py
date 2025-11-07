"""
wa-resize-observer component.
"""

from typing import Literal
from pyhtml import Tag
from pyhtml.__types import ChildrenType, AttributeType


class resize_observer(Tag):
    """
    wa-resize-observer web component.

    Args:
        *children: Child elements and text content
        disabled: Disables the observer.
        **attributes: Additional HTML attributes

    Slots:
        : One or more elements to watch for resizing.
    """
    def __init__(
        self,
        *children: ChildrenType,
        disabled: bool | None = None,
        **attributes: AttributeType,
    ) -> None:
        # Build attributes dict, filtering out None values
        attributes = attributes.copy()
        attributes.update({
            'disabled': disabled,
        })
        # Filter out None values and False booleans, convert numbers to strings
        attributes = {
            k: str(v) if isinstance(v, (int, float)) and not isinstance(v, bool) else v
            for k, v in attributes.items()
            if v is not None and v is not False
        }
        super().__init__(*children, **attributes)

    def _get_tag_name(self) -> str:
        return "wa-resize-observer"


__all__ = [
    "resize_observer",
]