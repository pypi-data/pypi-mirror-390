"""Type stub for wa-tree component."""

from typing import Literal
from pyhtml import Tag
from pyhtml.__types import ChildrenType, AttributeType


class tree(Tag):
    """
    wa-tree web component.

    Args:
        *children: Child elements and text content
        selection: The selection behavior of the tree. Single selection allows only one node to be selected at a time. Multiple
            displays checkboxes and allows more than one node to be selected. Leaf allows only leaf nodes to be selected.
        **attributes: Additional HTML attributes

    Slots:
        : The default slot.
        expand-icon: The icon to show when the tree item is expanded. Works best with `<wa-icon>`.
        collapse-icon: The icon to show when the tree item is collapsed. Works best with `<wa-icon>`.
    """
    def __init__(
        self,
        *children: ChildrenType,
        selection: Literal["single", "multiple", "leaf"] | None = ...,
        **attributes: AttributeType,
    ) -> None: ...

    def _get_tag_name(self) -> str: ...