"""Type stub for wa-format-bytes component."""

from typing import Literal
from pyhtml import Tag
from pyhtml.__types import ChildrenType, AttributeType


class format_bytes(Tag):
    """
    wa-format-bytes web component.

    Args:
        *children: Child elements and text content
        value: The number to format in bytes.
        unit: The type of unit to display.
        display: Determines how to display the result, e.g. "100 bytes", "100 b", or "100b".
        **attributes: Additional HTML attributes
    """
    def __init__(
        self,
        *children: ChildrenType,
        value: int | float | None = ...,
        unit: Literal["byte", "bit"] | None = ...,
        display: Literal["long", "short", "narrow"] | None = ...,
        **attributes: AttributeType,
    ) -> None: ...

    def _get_tag_name(self) -> str: ...