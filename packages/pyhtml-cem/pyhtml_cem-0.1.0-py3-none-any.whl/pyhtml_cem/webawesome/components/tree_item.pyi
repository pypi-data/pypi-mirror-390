"""Type stub for wa-tree-item component."""

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
        expanded: bool | None = ...,
        selected: bool | None = ...,
        disabled: bool | None = ...,
        lazy: bool | None = ...,
        **attributes: AttributeType,
    ) -> None: ...

    def _get_tag_name(self) -> str: ...