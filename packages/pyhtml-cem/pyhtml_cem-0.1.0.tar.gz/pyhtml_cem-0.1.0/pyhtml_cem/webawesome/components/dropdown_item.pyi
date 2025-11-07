"""Type stub for wa-dropdown-item component."""

from typing import Literal
from pyhtml import Tag
from pyhtml.__types import ChildrenType, AttributeType


class dropdown_item(Tag):
    """
    wa-dropdown-item web component.

    Args:
        *children: Child elements and text content
        variant: The type of menu item to render.
        value: An optional value for the menu item. This is useful for determining which item was selected when listening to the
            dropdown's `wa-select` event.
        type: Set to `checkbox` to make the item a checkbox.
        checked: Set to true to check the dropdown item. Only valid when `type` is `checkbox`.
        disabled: Disables the dropdown item.
        submenuOpen: Whether the submenu is currently open.
        **attributes: Additional HTML attributes

    Slots:
        : The dropdown item's label.
        icon: An optional icon to display before the label.
        details: Additional content or details to display after the label.
        submenu: Submenu items, typically `<wa-dropdown-item>` elements, to create a nested menu.
    """
    def __init__(
        self,
        *children: ChildrenType,
        variant: Literal["danger", "default"] | None = ...,
        value: str | None = ...,
        type: Literal["normal", "checkbox"] | None = ...,
        checked: bool | None = ...,
        disabled: bool | None = ...,
        submenuOpen: bool | None = ...,
        **attributes: AttributeType,
    ) -> None: ...

    def _get_tag_name(self) -> str: ...