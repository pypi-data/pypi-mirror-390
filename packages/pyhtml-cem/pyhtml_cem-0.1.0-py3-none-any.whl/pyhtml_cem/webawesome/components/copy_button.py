"""
wa-copy-button component.
"""

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
        value: str | None = None,
        from_: str | None = None,
        disabled: bool | None = None,
        copy_label: str | None = None,
        success_label: str | None = None,
        error_label: str | None = None,
        feedback_duration: int | float | None = None,
        tooltip_placement: Literal["top", "right", "bottom", "left"] | None = None,
        **attributes: AttributeType,
    ) -> None:
        # Build attributes dict, filtering out None values
        attributes = attributes.copy()
        attributes.update({
            'value': value,
            'from_': from_,
            'disabled': disabled,
            'copy_label': copy_label,
            'success_label': success_label,
            'error_label': error_label,
            'feedback_duration': feedback_duration,
            'tooltip_placement': tooltip_placement,
        })
        # Filter out None values and False booleans, convert numbers to strings
        attributes = {
            k: str(v) if isinstance(v, (int, float)) and not isinstance(v, bool) else v
            for k, v in attributes.items()
            if v is not None and v is not False
        }
        super().__init__(*children, **attributes)

    def _get_tag_name(self) -> str:
        return "wa-copy-button"


__all__ = [
    "copy_button",
]