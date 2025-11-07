"""
wa-details component.
"""

from typing import Literal
from pyhtml import Tag
from pyhtml.__types import ChildrenType, AttributeType


class details(Tag):
    """
    wa-details web component.

    Args:
        *children: Child elements and text content
        open: Indicates whether or not the details is open. You can toggle this attribute to show and hide the details, or you
            can use the `show()` and `hide()` methods and this attribute will reflect the details' open state.
        summary: The summary to show in the header. If you need to display HTML, use the `summary` slot instead.
        name: Groups related details elements. When one opens, others with the same name will close.
        disabled: Disables the details so it can't be toggled.
        appearance: The element's visual appearance.
        icon_placement: The location of the expand/collapse icon.
        **attributes: Additional HTML attributes

    Slots:
        : The details' main content.
        summary: The details' summary. Alternatively, you can use the `summary` attribute.
        expand-icon: Optional expand icon to use instead of the default. Works best with `<wa-icon>`.
        collapse-icon: Optional collapse icon to use instead of the default. Works best with `<wa-icon>`.
    """
    def __init__(
        self,
        *children: ChildrenType,
        open: bool | None = None,
        summary: str | None = None,
        name: str | None = None,
        disabled: bool | None = None,
        appearance: Literal["filled", "outlined", "filled-outlined", "plain"] | None = None,
        icon_placement: Literal["start", "end"] | None = None,
        **attributes: AttributeType,
    ) -> None:
        # Build attributes dict, filtering out None values
        attributes = attributes.copy()
        attributes.update({
            'open': open,
            'summary': summary,
            'name': name,
            'disabled': disabled,
            'appearance': appearance,
            'icon_placement': icon_placement,
        })
        # Filter out None values and False booleans, convert numbers to strings
        attributes = {
            k: str(v) if isinstance(v, (int, float)) and not isinstance(v, bool) else v
            for k, v in attributes.items()
            if v is not None and v is not False
        }
        super().__init__(*children, **attributes)

    def _get_tag_name(self) -> str:
        return "wa-details"


__all__ = [
    "details",
]