"""Type stub for wa-tooltip component."""

from typing import Literal
from pyhtml import Tag
from pyhtml.__types import ChildrenType, AttributeType


class tooltip(Tag):
    """
    wa-tooltip web component.

    Args:
        *children: Child elements and text content
        placement: The preferred placement of the tooltip. Note that the actual placement may vary as needed to keep the tooltip
            inside of the viewport.
        disabled: Disables the tooltip so it won't show when triggered.
        distance: The distance in pixels from which to offset the tooltip away from its target.
        open: Indicates whether or not the tooltip is open. You can use this in lieu of the show/hide methods.
        skidding: The distance in pixels from which to offset the tooltip along its target.
        show_delay: The amount of time to wait before showing the tooltip when the user mouses in.
        hide_delay: The amount of time to wait before hiding the tooltip when the user mouses out..
        trigger: Controls how the tooltip is activated. Possible options include `click`, `hover`, `focus`, and `manual`. Multiple
            options can be passed by separating them with a space. When manual is used, the tooltip must be activated
            programmatically.
        without_arrow: Removes the arrow from the tooltip.
        for_: Type: string | null
        **attributes: Additional HTML attributes

    Slots:
        : The tooltip's default slot where any content should live. Interactive content should be avoided.
    """
    def __init__(
        self,
        *children: ChildrenType,
        placement: Literal["top", "top-start", "top-end", "right", "right-start", "right-end", "bottom", "bottom-start", "bottom-end", "left", "left-start", "left-end"] | None = ...,
        disabled: bool | None = ...,
        distance: int | float | None = ...,
        open: bool | None = ...,
        skidding: int | float | None = ...,
        show_delay: int | float | None = ...,
        hide_delay: int | float | None = ...,
        trigger: str | None = ...,
        without_arrow: bool | None = ...,
        for_: str | bool | None = ...,
        **attributes: AttributeType,
    ) -> None: ...

    def _get_tag_name(self) -> str: ...