"""Type stub for wa-spinner component."""

from typing import Literal
from pyhtml import Tag
from pyhtml.__types import ChildrenType, AttributeType


class spinner(Tag):
    """
    wa-spinner web component.
    """
    def __init__(
        self,
        *children: ChildrenType,
        **attributes: AttributeType,
    ) -> None: ...

    def _get_tag_name(self) -> str: ...