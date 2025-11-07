"""
wa-tooltip component.
"""

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
        placement: Literal["top", "top-start", "top-end", "right", "right-start", "right-end", "bottom", "bottom-start", "bottom-end", "left", "left-start", "left-end"] | None = None,
        disabled: bool | None = None,
        distance: int | float | None = None,
        open: bool | None = None,
        skidding: int | float | None = None,
        show_delay: int | float | None = None,
        hide_delay: int | float | None = None,
        trigger: str | None = None,
        without_arrow: bool | None = None,
        for_: str | bool | None = None,
        **attributes: AttributeType,
    ) -> None:
        # Build attributes dict, filtering out None values
        attributes = attributes.copy()
        attributes.update({
            'placement': placement,
            'disabled': disabled,
            'distance': distance,
            'open': open,
            'skidding': skidding,
            'show_delay': show_delay,
            'hide_delay': hide_delay,
            'trigger': trigger,
            'without_arrow': without_arrow,
            'for_': for_,
        })
        # Filter out None values and False booleans, convert numbers to strings
        attributes = {
            k: str(v) if isinstance(v, (int, float)) and not isinstance(v, bool) else v
            for k, v in attributes.items()
            if v is not None and v is not False
        }
        super().__init__(*children, **attributes)

    def _get_tag_name(self) -> str:
        return "wa-tooltip"


__all__ = [
    "tooltip",
]