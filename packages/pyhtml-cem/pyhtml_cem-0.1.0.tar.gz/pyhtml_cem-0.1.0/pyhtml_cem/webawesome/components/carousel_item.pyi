"""Type stub for wa-carousel-item component."""

from typing import Literal
from pyhtml import Tag
from pyhtml.__types import ChildrenType, AttributeType


class carousel_item(Tag):
    """
    wa-carousel-item web component.

    Slots:
        : The carousel item's content..
    """
    def __init__(
        self,
        *children: ChildrenType,
        **attributes: AttributeType,
    ) -> None: ...

    def _get_tag_name(self) -> str: ...