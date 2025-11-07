"""Type stub for wa-divider component."""

from typing import Literal
from pyhtml import Tag
from pyhtml.__types import ChildrenType, AttributeType


class divider(Tag):
    """
    wa-divider web component.

    Args:
        *children: Child elements and text content
        orientation: Sets the divider's orientation.
        **attributes: Additional HTML attributes
    """
    def __init__(
        self,
        *children: ChildrenType,
        orientation: Literal["horizontal", "vertical"] | None = ...,
        **attributes: AttributeType,
    ) -> None: ...

    def _get_tag_name(self) -> str: ...