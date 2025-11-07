"""Type stub for wa-breadcrumb-item component."""

from typing import Literal
from pyhtml import Tag
from pyhtml.__types import ChildrenType, AttributeType


class breadcrumb_item(Tag):
    """
    wa-breadcrumb-item web component.

    Args:
        *children: Child elements and text content
        href: Optional URL to direct the user to when the breadcrumb item is activated. When set, a link will be rendered
            internally. When unset, a button will be rendered instead.
        target: Tells the browser where to open the link. Only used when `href` is set.
        rel: The `rel` attribute to use on the link. Only used when `href` is set.
        **attributes: Additional HTML attributes

    Slots:
        : The breadcrumb item's label.
        start: An element, such as `<wa-icon>`, placed before the label.
        end: An element, such as `<wa-icon>`, placed after the label.
        separator: The separator to use for the breadcrumb item. This will only change the separator for this item. If you want to change it for all items in the group, set the separator on `<wa-breadcrumb>` instead.
    """
    def __init__(
        self,
        *children: ChildrenType,
        href: str | bool | None = ...,
        target: Literal["_blank", "_parent", "_self", "_top"] | None = ...,
        rel: str | None = ...,
        **attributes: AttributeType,
    ) -> None: ...

    def _get_tag_name(self) -> str: ...