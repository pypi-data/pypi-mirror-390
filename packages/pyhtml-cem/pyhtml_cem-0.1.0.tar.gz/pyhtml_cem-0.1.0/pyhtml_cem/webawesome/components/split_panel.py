"""
wa-split-panel component.
"""

from typing import Literal
from pyhtml import Tag
from pyhtml.__types import ChildrenType, AttributeType


class split_panel(Tag):
    """
    wa-split-panel web component.

    Args:
        *children: Child elements and text content
        position: The current position of the divider from the primary panel's edge as a percentage 0-100. Defaults to 50% of the
            container's initial size.
        position_in_pixels: The current position of the divider from the primary panel's edge in pixels.
        orientation: Sets the split panel's orientation.
        disabled: Disables resizing. Note that the position may still change as a result of resizing the host element.
        primary: If no primary panel is designated, both panels will resize proportionally when the host element is resized. If a
            primary panel is designated, it will maintain its size and the other panel will grow or shrink as needed when the
            host element is resized.
        snap: One or more space-separated values at which the divider should snap. Values can be in pixels or percentages, e.g.
            `"100px 50%"`.
        snap_threshold: How close the divider must be to a snap point until snapping occurs.
        **attributes: Additional HTML attributes

    Slots:
        start: Content to place in the start panel.
        end: Content to place in the end panel.
        divider: The divider. Useful for slotting in a custom icon that renders as a handle.
    """
    def __init__(
        self,
        *children: ChildrenType,
        position: int | float | None = None,
        position_in_pixels: int | float | None = None,
        orientation: Literal["horizontal", "vertical"] | None = None,
        disabled: bool | None = None,
        primary: Literal["start", "end"] | None = None,
        snap: str | bool | None = None,
        snap_threshold: int | float | None = None,
        **attributes: AttributeType,
    ) -> None:
        # Build attributes dict, filtering out None values
        attributes = attributes.copy()
        attributes.update({
            'position': position,
            'position_in_pixels': position_in_pixels,
            'orientation': orientation,
            'disabled': disabled,
            'primary': primary,
            'snap': snap,
            'snap_threshold': snap_threshold,
        })
        # Filter out None values and False booleans, convert numbers to strings
        attributes = {
            k: str(v) if isinstance(v, (int, float)) and not isinstance(v, bool) else v
            for k, v in attributes.items()
            if v is not None and v is not False
        }
        super().__init__(*children, **attributes)

    def _get_tag_name(self) -> str:
        return "wa-split-panel"


__all__ = [
    "split_panel",
]