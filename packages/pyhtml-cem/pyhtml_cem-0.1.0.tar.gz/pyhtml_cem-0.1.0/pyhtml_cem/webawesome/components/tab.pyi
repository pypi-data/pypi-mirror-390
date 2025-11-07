"""Type stub for wa-tab component."""

from typing import Literal
from pyhtml import Tag
from pyhtml.__types import ChildrenType, AttributeType


class tab(Tag):
    """
    wa-tab web component.

    Args:
        *children: Child elements and text content
        panel: The name of the tab panel this tab is associated with. The panel must be located in the same tab group.
        disabled: Disables the tab and prevents selection.
        **attributes: Additional HTML attributes

    Slots:
        : The tab's label.
    """
    def __init__(
        self,
        *children: ChildrenType,
        panel: str | None = ...,
        disabled: bool | None = ...,
        **attributes: AttributeType,
    ) -> None: ...

    def _get_tag_name(self) -> str: ...