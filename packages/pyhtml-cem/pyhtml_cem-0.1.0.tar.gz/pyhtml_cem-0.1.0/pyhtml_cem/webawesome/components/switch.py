"""
wa-switch component.
"""

from typing import Literal
from pyhtml import Tag
from pyhtml.__types import ChildrenType, AttributeType


class switch(Tag):
    """
    wa-switch web component.

    Args:
        *children: Child elements and text content
        title: Type: string
        name: The name of the switch, submitted as a name/value pair with form data.
        value: The value of the switch, submitted as a name/value pair with form data.
        size: The switch's size.
        disabled: Disables the switch.
        checked: The default value of the form control. Primarily used for resetting the form control.
        form: By default, form controls are associated with the nearest containing `<form>` element. This attribute allows you
            to place the form control outside of a form and associate it with the form that has this `id`. The form must be in
            the same document or shadow root for this to work.
        required: Makes the switch a required field.
        hint: The switch's hint. If you need to display HTML, use the `hint` slot instead.
        with_hint: Used for SSR. If you slot in hint, make sure to add `with-hint` to your component to get it to properly render with SSR.
        **attributes: Additional HTML attributes

    Slots:
        : The switch's label.
        hint: Text that describes how to use the switch. Alternatively, you can use the `hint` attribute.
    """
    def __init__(
        self,
        *children: ChildrenType,
        title: str | None = None,
        name: str | bool | None = None,
        value: str | bool | None = None,
        size: Literal["small", "medium", "large"] | None = None,
        disabled: bool | None = None,
        checked: bool | None = None,
        form: str | bool | None = None,
        required: bool | None = None,
        hint: str | None = None,
        with_hint: bool | None = None,
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
            'checked': checked,
            'form': form,
            'required': required,
            'hint': hint,
            'with_hint': with_hint,
        })
        # Filter out None values and False booleans, convert numbers to strings
        attributes = {
            k: str(v) if isinstance(v, (int, float)) and not isinstance(v, bool) else v
            for k, v in attributes.items()
            if v is not None and v is not False
        }
        super().__init__(*children, **attributes)

    def _get_tag_name(self) -> str:
        return "wa-switch"


__all__ = [
    "switch",
]