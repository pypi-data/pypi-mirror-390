"""
wa-tree-item component.
"""

from typing import Literal
from pyhtml import Tag
from pyhtml.__types import ChildrenType, AttributeType


class tree_item(Tag):
    """
    wa-tree-item web component.

    Args:
        *children: Child elements and text content
        expanded: Expands the tree item.
        selected: Draws the tree item in a selected state.
        disabled: Disables the tree item.
        lazy: Enables lazy loading behavior.
        **attributes: Additional HTML attributes

    Slots:
        : The default slot.
        expand-icon: The icon to show when the tree item is expanded.
        collapse-icon: The icon to show when the tree item is collapsed.
    """
    def __init__(
        self,
        *children: ChildrenType,
        expanded: bool | None = None,
        selected: bool | None = None,
        disabled: bool | None = None,
        lazy: bool | None = None,
        **attributes: AttributeType,
    ) -> None:
        # Build attributes dict, filtering out None values
        attributes = attributes.copy()
        attributes.update({
            'expanded': expanded,
            'selected': selected,
            'disabled': disabled,
            'lazy': lazy,
        })
        # Filter out None values and False booleans, convert numbers to strings
        attributes = {
            k: str(v) if isinstance(v, (int, float)) and not isinstance(v, bool) else v
            for k, v in attributes.items()
            if v is not None and v is not False
        }
        super().__init__(*children, **attributes)

    def _get_tag_name(self) -> str:
        return "wa-tree-item"


__all__ = [
    "tree_item",
]