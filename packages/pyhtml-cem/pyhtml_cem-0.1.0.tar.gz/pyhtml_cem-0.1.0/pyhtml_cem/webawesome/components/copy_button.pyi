"""Type stub for wa-copy-button component."""

from typing import Literal
from pyhtml import Tag
from pyhtml.__types import ChildrenType, AttributeType


class copy_button(Tag):
    """
    wa-copy-button web component.

    Args:
        *children: Child elements and text content
        value: The text value to copy.
        from_: An id that references an element in the same document from which data will be copied. If both this and `value` are
            present, this value will take precedence. By default, the target element's `textContent` will be copied. To copy an
            attribute, append the attribute name wrapped in square brackets, e.g. `from="el[value]"`. To copy a property,
            append a dot and the property name, e.g. `from="el.value"`.
        disabled: Disables the copy button.
        copy_label: A custom label to show in the tooltip.
        success_label: A custom label to show in the tooltip after copying.
        error_label: A custom label to show in the tooltip when a copy error occurs.
        feedback_duration: The length of time to show feedback before restoring the default trigger.
        tooltip_placement: The preferred placement of the tooltip.
        **attributes: Additional HTML attributes

    Slots:
        copy-icon: The icon to show in the default copy state. Works best with `<wa-icon>`.
        success-icon: The icon to show when the content is copied. Works best with `<wa-icon>`.
        error-icon: The icon to show when a copy error occurs. Works best with `<wa-icon>`.
    """
    def __init__(
        self,
        *children: ChildrenType,
        value: str | None = ...,
        from_: str | None = ...,
        disabled: bool | None = ...,
        copy_label: str | None = ...,
        success_label: str | None = ...,
        error_label: str | None = ...,
        feedback_duration: int | float | None = ...,
        tooltip_placement: Literal["top", "right", "bottom", "left"] | None = ...,
        **attributes: AttributeType,
    ) -> None: ...

    def _get_tag_name(self) -> str: ...