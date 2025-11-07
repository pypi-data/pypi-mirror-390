"""Type stub for wa-tab-panel component."""

from typing import Literal
from pyhtml import Tag
from pyhtml.__types import ChildrenType, AttributeType


class tab_panel(Tag):
    """
    wa-tab-panel web component.

    Args:
        *children: Child elements and text content
        name: The tab panel's name.
        active: When true, the tab panel will be shown.
        **attributes: Additional HTML attributes

    Slots:
        : The tab panel's content.
    """
    def __init__(
        self,
        *children: ChildrenType,
        name: str | None = ...,
        active: bool | None = ...,
        **attributes: AttributeType,
    ) -> None: ...

    def _get_tag_name(self) -> str: ...