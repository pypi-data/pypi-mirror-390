"""
wa-scroller component.
"""

from typing import Literal
from pyhtml import Tag
from pyhtml.__types import ChildrenType, AttributeType


class scroller(Tag):
    """
    wa-scroller web component.

    Args:
        *children: Child elements and text content
        orientation: The scroller's orientation.
        without_scrollbar: Removes the visible scrollbar.
        without_shadow: Removes the shadows.
        **attributes: Additional HTML attributes

    Slots:
        : The content to show inside the scroller.
    """
    def __init__(
        self,
        *children: ChildrenType,
        orientation: Literal["horizontal", "vertical"] | None = None,
        without_scrollbar: bool | None = None,
        without_shadow: bool | None = None,
        **attributes: AttributeType,
    ) -> None:
        # Build attributes dict, filtering out None values
        attributes = attributes.copy()
        attributes.update({
            'orientation': orientation,
            'without_scrollbar': without_scrollbar,
            'without_shadow': without_shadow,
        })
        # Filter out None values and False booleans, convert numbers to strings
        attributes = {
            k: str(v) if isinstance(v, (int, float)) and not isinstance(v, bool) else v
            for k, v in attributes.items()
            if v is not None and v is not False
        }
        super().__init__(*children, **attributes)

    def _get_tag_name(self) -> str:
        return "wa-scroller"


__all__ = [
    "scroller",
]