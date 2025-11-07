"""
wa-dropdown component.
"""

from typing import Literal
from pyhtml import Tag
from pyhtml.__types import ChildrenType, AttributeType


class dropdown(Tag):
    """
    wa-dropdown web component.

    Args:
        *children: Child elements and text content
        open: Opens or closes the dropdown.
        size: The dropdown's size.
        placement: The placement of the dropdown menu in reference to the trigger. The menu will shift to a more optimal location if
            the preferred placement doesn't have enough room.
        distance: The distance of the dropdown menu from its trigger.
        skidding: The offset of the dropdown menu along its trigger.
        **attributes: Additional HTML attributes

    Slots:
        : The dropdown's items, typically `<wa-dropdown-item>` elements.
        trigger: The element that triggers the dropdown, such as a `<wa-button>` or `<button>`.
    """
    def __init__(
        self,
        *children: ChildrenType,
        open: bool | None = None,
        size: Literal["small", "medium", "large"] | None = None,
        placement: Literal["top", "top-start", "top-end", "bottom", "bottom-start", "bottom-end", "right", "right-start", "right-end", "left", "left-start", "left-end"] | None = None,
        distance: int | float | None = None,
        skidding: int | float | None = None,
        **attributes: AttributeType,
    ) -> None:
        # Build attributes dict, filtering out None values
        attributes = attributes.copy()
        attributes.update({
            'open': open,
            'size': size,
            'placement': placement,
            'distance': distance,
            'skidding': skidding,
        })
        # Filter out None values and False booleans, convert numbers to strings
        attributes = {
            k: str(v) if isinstance(v, (int, float)) and not isinstance(v, bool) else v
            for k, v in attributes.items()
            if v is not None and v is not False
        }
        super().__init__(*children, **attributes)

    def _get_tag_name(self) -> str:
        return "wa-dropdown"


__all__ = [
    "dropdown",
]