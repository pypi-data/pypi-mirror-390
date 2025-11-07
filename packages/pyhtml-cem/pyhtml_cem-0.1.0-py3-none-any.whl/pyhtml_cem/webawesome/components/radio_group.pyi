"""Type stub for wa-radio-group component."""

from typing import Literal
from pyhtml import Tag
from pyhtml.__types import ChildrenType, AttributeType


class radio_group(Tag):
    """
    wa-radio-group web component.

    Args:
        *children: Child elements and text content
        label: The radio group's label. Required for proper accessibility. If you need to display HTML, use the `label` slot
            instead.
        hint: The radio groups's hint. If you need to display HTML, use the `hint` slot instead.
        name: The name of the radio group, submitted as a name/value pair with form data.
        disabled: Disables the radio group and all child radios.
        orientation: The orientation in which to show radio items.
        value: The default value of the form control. Primarily used for resetting the form control.
        size: The radio group's size. This size will be applied to all child radios and radio buttons, except when explicitly overridden.
        required: Ensures a child radio is checked before allowing the containing form to submit.
        with_label: Used for SSR. if true, will show slotted label on initial render.
        with_hint: Used for SSR. if true, will show slotted hint on initial render.
        **attributes: Additional HTML attributes

    Slots:
        : The default slot where `<wa-radio>` elements are placed.
        label: The radio group's label. Required for proper accessibility. Alternatively, you can use the `label` attribute.
        hint: Text that describes how to use the radio group. Alternatively, you can use the `hint` attribute.
    """
    def __init__(
        self,
        *children: ChildrenType,
        label: str | None = ...,
        hint: str | None = ...,
        name: str | bool | None = ...,
        disabled: bool | None = ...,
        orientation: Literal["horizontal", "vertical"] | None = ...,
        value: str | bool | None = ...,
        size: Literal["small", "medium", "large"] | None = ...,
        required: bool | None = ...,
        with_label: bool | None = ...,
        with_hint: bool | None = ...,
        **attributes: AttributeType,
    ) -> None: ...

    def _get_tag_name(self) -> str: ...