"""
wa-checkbox component.
"""

from typing import Literal
from pyhtml import Tag
from pyhtml.__types import ChildrenType, AttributeType


class checkbox(Tag):
    """
    wa-checkbox web component.

    Args:
        *children: Child elements and text content
        title: Type: string
        name: The name of the checkbox, submitted as a name/value pair with form data.
        value: The value of the checkbox, submitted as a name/value pair with form data.
        size: The checkbox's size.
        disabled: Disables the checkbox.
        indeterminate: Draws the checkbox in an indeterminate state. This is usually applied to checkboxes that represents a "select
            all/none" behavior when associated checkboxes have a mix of checked and unchecked states.
        checked: The default value of the form control. Primarily used for resetting the form control.
        form: By default, form controls are associated with the nearest containing `<form>` element. This attribute allows you
            to place the form control outside of a form and associate it with the form that has this `id`. The form must be in
            the same document or shadow root for this to work.
        required: Makes the checkbox a required field.
        hint: The checkbox's hint. If you need to display HTML, use the `hint` slot instead.
        **attributes: Additional HTML attributes

    Slots:
        : The checkbox's label.
        hint: Text that describes how to use the checkbox. Alternatively, you can use the `hint` attribute.
    """
    def __init__(
        self,
        *children: ChildrenType,
        title: str | None = None,
        name: str | None = None,
        value: str | bool | None = None,
        size: Literal["small", "medium", "large"] | None = None,
        disabled: bool | None = None,
        indeterminate: bool | None = None,
        checked: bool | None = None,
        form: str | bool | None = None,
        required: bool | None = None,
        hint: str | None = None,
        **attributes: AttributeType,
    ) -> None:
        # Build attributes dict, filtering out None values
        attributes = attributes.copy()
        attributes.update({
            'title': title,
            'name': name,
            'value': value,
            'size': size,
            'disabled': disabled,
            'indeterminate': indeterminate,
            'checked': checked,
            'form': form,
            'required': required,
            'hint': hint,
        })
        # Filter out None values and False booleans, convert numbers to strings
        attributes = {
            k: str(v) if isinstance(v, (int, float)) and not isinstance(v, bool) else v
            for k, v in attributes.items()
            if v is not None and v is not False
        }
        super().__init__(*children, **attributes)

    def _get_tag_name(self) -> str:
        return "wa-checkbox"


__all__ = [
    "checkbox",
]