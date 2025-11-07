"""
wa-radio component.
"""

from typing import Literal
from pyhtml import Tag
from pyhtml.__types import ChildrenType, AttributeType


class radio(Tag):
    """
    wa-radio web component.

    Args:
        *children: Child elements and text content
        form: The string pointing to a form's id.
        value: The radio's value. When selected, the radio group will receive this value.
        appearance: The radio's visual appearance.
        size: The radio's size. When used inside a radio group, the size will be determined by the radio group's size so this
            attribute can typically be omitted.
        disabled: Disables the radio.
        **attributes: Additional HTML attributes

    Slots:
        : The radio's label.
    """
    def __init__(
        self,
        *children: ChildrenType,
        form: str | bool | None = None,
        value: str | None = None,
        appearance: Literal["default", "button"] | None = None,
        size: Literal["small", "medium", "large"] | None = None,
        disabled: bool | None = None,
        **attributes: AttributeType,
    ) -> None:
        # Build attributes dict, filtering out None values
        attributes = attributes.copy()
        attributes.update({
            'form': form,
            'value': value,
            'appearance': appearance,
            'size': size,
            'disabled': disabled,
        })
        # Filter out None values and False booleans, convert numbers to strings
        attributes = {
            k: str(v) if isinstance(v, (int, float)) and not isinstance(v, bool) else v
            for k, v in attributes.items()
            if v is not None and v is not False
        }
        super().__init__(*children, **attributes)

    def _get_tag_name(self) -> str:
        return "wa-radio"


__all__ = [
    "radio",
]