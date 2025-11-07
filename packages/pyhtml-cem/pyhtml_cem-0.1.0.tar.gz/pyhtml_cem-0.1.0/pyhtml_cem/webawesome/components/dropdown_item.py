"""
wa-dropdown-item component.
"""

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
        variant: Literal["danger", "default"] | None = None,
        value: str | None = None,
        type: Literal["normal", "checkbox"] | None = None,
        checked: bool | None = None,
        disabled: bool | None = None,
        submenuOpen: bool | None = None,
        **attributes: AttributeType,
    ) -> None:
        # Build attributes dict, filtering out None values
        attributes = attributes.copy()
        attributes.update({
            'variant': variant,
            'value': value,
            'type': type,
            'checked': checked,
            'disabled': disabled,
            'submenuOpen': submenuOpen,
        })
        # Filter out None values and False booleans, convert numbers to strings
        attributes = {
            k: str(v) if isinstance(v, (int, float)) and not isinstance(v, bool) else v
            for k, v in attributes.items()
            if v is not None and v is not False
        }
        super().__init__(*children, **attributes)

    def _get_tag_name(self) -> str:
        return "wa-dropdown-item"


__all__ = [
    "dropdown_item",
]