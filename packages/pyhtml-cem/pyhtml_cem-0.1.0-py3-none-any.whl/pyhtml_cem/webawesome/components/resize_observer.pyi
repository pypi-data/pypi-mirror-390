"""Type stub for wa-resize-observer component."""

from typing import Literal
from pyhtml import Tag
from pyhtml.__types import ChildrenType, AttributeType


class resize_observer(Tag):
    """
    wa-resize-observer web component.

    Args:
        *children: Child elements and text content
        disabled: Disables the observer.
        **attributes: Additional HTML attributes

    Slots:
        : One or more elements to watch for resizing.
    """
    def __init__(
        self,
        *children: ChildrenType,
        disabled: bool | None = ...,
        **attributes: AttributeType,
    ) -> None: ...

    def _get_tag_name(self) -> str: ...