"""
wa-tab component.
"""

from typing import Literal
from pyhtml import Tag
from pyhtml.__types import ChildrenType, AttributeType


class tab(Tag):
    """
    wa-tab web component.

    Args:
        *children: Child elements and text content
        panel: The name of the tab panel this tab is associated with. The panel must be located in the same tab group.
        disabled: Disables the tab and prevents selection.
        **attributes: Additional HTML attributes

    Slots:
        : The tab's label.
    """
    def __init__(
        self,
        *children: ChildrenType,
        panel: str | None = None,
        disabled: bool | None = None,
        **attributes: AttributeType,
    ) -> None:
        # Build attributes dict, filtering out None values
        attributes = attributes.copy()
        attributes.update({
            'panel': panel,
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
        return "wa-tab"


__all__ = [
    "tab",
]