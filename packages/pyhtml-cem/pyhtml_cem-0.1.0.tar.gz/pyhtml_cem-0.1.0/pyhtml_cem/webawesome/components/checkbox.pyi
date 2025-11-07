"""Type stub for wa-checkbox component."""

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
        title: str | None = ...,
        name: str | None = ...,
        value: str | bool | None = ...,
        size: Literal["small", "medium", "large"] | None = ...,
        disabled: bool | None = ...,
        indeterminate: bool | None = ...,
        checked: bool | None = ...,
        form: str | bool | None = ...,
        required: bool | None = ...,
        hint: str | None = ...,
        **attributes: AttributeType,
    ) -> None: ...

    def _get_tag_name(self) -> str: ...