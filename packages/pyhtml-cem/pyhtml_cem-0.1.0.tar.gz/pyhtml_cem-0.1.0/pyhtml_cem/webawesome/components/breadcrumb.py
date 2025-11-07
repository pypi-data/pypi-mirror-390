"""
wa-breadcrumb component.
"""

from typing import Literal
from pyhtml import Tag
from pyhtml.__types import ChildrenType, AttributeType


class breadcrumb(Tag):
    """
    wa-breadcrumb web component.

    Args:
        *children: Child elements and text content
        label: The label to use for the breadcrumb control. This will not be shown on the screen, but it will be announced by
            screen readers and other assistive devices to provide more context for users.
        **attributes: Additional HTML attributes

    Slots:
        : One or more breadcrumb items to display.
        separator: The separator to use between breadcrumb items. Works best with `<wa-icon>`.
    """
    def __init__(
        self,
        *children: ChildrenType,
        label: str | None = None,
        **attributes: AttributeType,
    ) -> None:
        # Build attributes dict, filtering out None values
        attributes = attributes.copy()
        attributes.update({
            'label': label,
        })
        # Filter out None values and False booleans, convert numbers to strings
        attributes = {
            k: str(v) if isinstance(v, (int, float)) and not isinstance(v, bool) else v
            for k, v in attributes.items()
            if v is not None and v is not False
        }
        super().__init__(*children, **attributes)

    def _get_tag_name(self) -> str:
        return "wa-breadcrumb"


__all__ = [
    "breadcrumb",
]