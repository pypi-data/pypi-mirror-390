"""Type stub for wa-dropdown component."""

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
        open: bool | None = ...,
        size: Literal["small", "medium", "large"] | None = ...,
        placement: Literal["top", "top-start", "top-end", "bottom", "bottom-start", "bottom-end", "right", "right-start", "right-end", "left", "left-start", "left-end"] | None = ...,
        distance: int | float | None = ...,
        skidding: int | float | None = ...,
        **attributes: AttributeType,
    ) -> None: ...

    def _get_tag_name(self) -> str: ...