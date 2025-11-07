"""Type stub for wa-option component."""

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
        value: str | None = ...,
        disabled: bool | None = ...,
        selected: bool | None = ...,
        label: str | None = ...,
        **attributes: AttributeType,
    ) -> None: ...

    def _get_tag_name(self) -> str: ...