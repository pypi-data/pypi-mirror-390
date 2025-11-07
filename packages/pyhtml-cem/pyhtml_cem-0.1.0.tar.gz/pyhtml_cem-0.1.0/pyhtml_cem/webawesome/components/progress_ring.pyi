"""Type stub for wa-progress-ring component."""

from typing import Literal
from pyhtml import Tag
from pyhtml.__types import ChildrenType, AttributeType


class progress_ring(Tag):
    """
    wa-progress-ring web component.

    Args:
        *children: Child elements and text content
        value: The current progress as a percentage, 0 to 100.
        label: A custom label for assistive devices.
        **attributes: Additional HTML attributes

    Slots:
        : A label to show inside the ring.
    """
    def __init__(
        self,
        *children: ChildrenType,
        value: int | float | None = ...,
        label: str | None = ...,
        **attributes: AttributeType,
    ) -> None: ...

    def _get_tag_name(self) -> str: ...