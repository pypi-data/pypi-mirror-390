"""
wa-option component.
"""

from typing import Literal
from pyhtml import Tag
from pyhtml.__types import ChildrenType, AttributeType


class option(Tag):
    """
    wa-option web component.

    Args:
        *children: Child elements and text content
        value: The option's value. When selected, the containing form control will receive this value. The value must be unique
            from other options in the same group. Values may not contain spaces, as spaces are used as delimiters when listing
            multiple values.
        disabled: Draws the option in a disabled state, preventing selection.
        selected: Selects an option initially.
        label: The option’s plain text label.
            Usually automatically generated, but can be useful to provide manually for cases involving complex content.
        **attributes: Additional HTML attributes

    Slots:
        : The option's label.
        start: An element, such as `<wa-icon>`, placed before the label.
        end: An element, such as `<wa-icon>`, placed after the label.
    """
    def __init__(
        self,
        *children: ChildrenType,
        value: str | None = None,
        disabled: bool | None = None,
        selected: bool | None = None,
        label: str | None = None,
        **attributes: AttributeType,
    ) -> None:
        # Build attributes dict, filtering out None values
        attributes = attributes.copy()
        attributes.update({
            'value': value,
            'disabled': disabled,
            'selected': selected,
            'label': label,
        })
        # Filter out None values and False booleans, convert numbers to strings
        attributes = {
            k: str(v) if isinstance(v, (int, float)) and not isinstance(v, bool) else v
            for k, v in attributes.items()
            if v is not None and v is not False
        }
        super().__init__(*children, **attributes)

    def _get_tag_name(self) -> str:
        return "wa-option"


__all__ = [
    "option",
]