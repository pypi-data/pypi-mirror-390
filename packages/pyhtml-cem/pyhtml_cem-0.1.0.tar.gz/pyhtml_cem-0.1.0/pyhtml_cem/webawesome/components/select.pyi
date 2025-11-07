"""Type stub for wa-select component."""

from typing import Literal
from pyhtml import Tag
from pyhtml.__types import ChildrenType, AttributeType


class select(Tag):
    """
    wa-select web component.

    Args:
        *children: Child elements and text content
        name: The name of the select, submitted as a name/value pair with form data.
        value: The select's value. This will be a string for single select or an array for multi-select.
        size: The select's size.
        placeholder: Placeholder text to show as a hint when the select is empty.
        multiple: Allows more than one option to be selected.
        max_options_visible: The maximum number of selected options to show when `multiple` is true. After the maximum, "+n" will be shown to
            indicate the number of additional items that are selected. Set to 0 to remove the limit.
        disabled: Disables the select control.
        with_clear: Adds a clear button when the select is not empty.
        open: Indicates whether or not the select is open. You can toggle this attribute to show and hide the menu, or you can
            use the `show()` and `hide()` methods and this attribute will reflect the select's open state.
        appearance: The select's visual appearance.
        pill: Draws a pill-style select with rounded edges.
        label: The select's label. If you need to display HTML, use the `label` slot instead.
        placement: The preferred placement of the select's menu. Note that the actual placement may vary as needed to keep the listbox
            inside of the viewport.
        hint: The select's hint. If you need to display HTML, use the `hint` slot instead.
        with_label: Used for SSR purposes when a label is slotted in. Will show the label on first render.
        with_hint: Used for SSR purposes when hint is slotted in. Will show the hint on first render.
        form: By default, form controls are associated with the nearest containing `<form>` element. This attribute allows you
            to place the form control outside of a form and associate it with the form that has this `id`. The form must be in
            the same document or shadow root for this to work.
        required: The select's required attribute.
        **attributes: Additional HTML attributes

    Slots:
        : The listbox options. Must be `<wa-option>` elements. You can use `<wa-divider>` to group items visually.
        label: The input's label. Alternatively, you can use the `label` attribute.
        start: An element, such as `<wa-icon>`, placed at the start of the combobox.
        end: An element, such as `<wa-icon>`, placed at the end of the combobox.
        clear-icon: An icon to use in lieu of the default clear icon.
        expand-icon: The icon to show when the control is expanded and collapsed. Rotates on open and close.
        hint: Text that describes how to use the input. Alternatively, you can use the `hint` attribute.
    """
    def __init__(
        self,
        *children: ChildrenType,
        name: str | None = ...,
        value: str | bool | None = ...,
        size: Literal["small", "medium", "large"] | None = ...,
        placeholder: str | None = ...,
        multiple: bool | None = ...,
        max_options_visible: int | float | None = ...,
        disabled: bool | None = ...,
        with_clear: bool | None = ...,
        open: bool | None = ...,
        appearance: Literal["filled", "outlined", "filled-outlined"] | None = ...,
        pill: bool | None = ...,
        label: str | None = ...,
        placement: Literal["top", "bottom"] | None = ...,
        hint: str | None = ...,
        with_label: bool | None = ...,
        with_hint: bool | None = ...,
        form: str | bool | None = ...,
        required: bool | None = ...,
        **attributes: AttributeType,
    ) -> None: ...

    def _get_tag_name(self) -> str: ...