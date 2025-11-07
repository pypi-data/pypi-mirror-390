"""
wa-popover component.
"""

from typing import Literal
from pyhtml import Tag
from pyhtml.__types import ChildrenType, AttributeType


class popover(Tag):
    """
    wa-popover web component.

    Args:
        *children: Child elements and text content
        placement: The preferred placement of the popover. Note that the actual placement may vary as needed to keep the popover
            inside of the viewport.
        open: Shows or hides the popover.
        distance: The distance in pixels from which to offset the popover away from its target.
        skidding: The distance in pixels from which to offset the popover along its target.
        for_: The ID of the popover's anchor element. This must be an interactive/focusable element such as a button.
        without_arrow: Removes the arrow from the popover.
        **attributes: Additional HTML attributes

    Slots:
        : The popover's content. Interactive elements such as buttons and links are supported.
    """
    def __init__(
        self,
        *children: ChildrenType,
        placement: Literal["top", "top-start", "top-end", "right", "right-start", "right-end", "bottom", "bottom-start", "bottom-end", "left", "left-start", "left-end"] | None = None,
        open: bool | None = None,
        distance: int | float | None = None,
        skidding: int | float | None = None,
        for_: str | bool | None = None,
        without_arrow: bool | None = None,
        **attributes: AttributeType,
    ) -> None:
        # Build attributes dict, filtering out None values
        attributes = attributes.copy()
        attributes.update({
            'placement': placement,
            'open': open,
            'distance': distance,
            'skidding': skidding,
            'for_': for_,
            'without_arrow': without_arrow,
        })
        # Filter out None values and False booleans, convert numbers to strings
        attributes = {
            k: str(v) if isinstance(v, (int, float)) and not isinstance(v, bool) else v
            for k, v in attributes.items()
            if v is not None and v is not False
        }
        super().__init__(*children, **attributes)

    def _get_tag_name(self) -> str:
        return "wa-popover"


__all__ = [
    "popover",
]