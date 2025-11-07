"""Type stub for wa-comparison component."""

from typing import Literal
from pyhtml import Tag
from pyhtml.__types import ChildrenType, AttributeType


class comparison(Tag):
    """
    wa-comparison web component.

    Args:
        *children: Child elements and text content
        position: The position of the divider as a percentage.
        **attributes: Additional HTML attributes

    Slots:
        before: The before content, often an `<img>` or `<svg>` element.
        after: The after content, often an `<img>` or `<svg>` element.
        handle: The icon used inside the handle.
    """
    def __init__(
        self,
        *children: ChildrenType,
        position: int | float | None = ...,
        **attributes: AttributeType,
    ) -> None: ...

    def _get_tag_name(self) -> str: ...