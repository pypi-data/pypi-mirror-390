"""Type stub for wa-radio component."""

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
        form: str | bool | None = ...,
        value: str | None = ...,
        appearance: Literal["default", "button"] | None = ...,
        size: Literal["small", "medium", "large"] | None = ...,
        disabled: bool | None = ...,
        **attributes: AttributeType,
    ) -> None: ...

    def _get_tag_name(self) -> str: ...