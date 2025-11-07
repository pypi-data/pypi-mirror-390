"""Type stub for wa-breadcrumb component."""

from typing import Literal
from pyhtml import Tag
from pyhtml.__types import ChildrenType, AttributeType


class breadcrumb(Tag):
    """
    wa-breadcrumb web component.

    Args:
        *children: Child elements and text content
        label: The label to use for the breadcrumb control. This will not be shown on the screen, but it will be announced by
            screen readers and other assistive devices to provide more context for users.
        **attributes: Additional HTML attributes

    Slots:
        : One or more breadcrumb items to display.
        separator: The separator to use between breadcrumb items. Works best with `<wa-icon>`.
    """
    def __init__(
        self,
        *children: ChildrenType,
        label: str | None = ...,
        **attributes: AttributeType,
    ) -> None: ...

    def _get_tag_name(self) -> str: ...