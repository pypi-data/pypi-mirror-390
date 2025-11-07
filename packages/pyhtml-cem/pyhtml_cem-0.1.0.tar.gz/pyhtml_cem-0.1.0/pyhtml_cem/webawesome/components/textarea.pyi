"""Type stub for wa-textarea component."""

from typing import Literal
from pyhtml import Tag
from pyhtml.__types import ChildrenType, AttributeType


class textarea(Tag):
    """
    wa-textarea web component.

    Args:
        *children: Child elements and text content
        title: Type: string
        name: The name of the textarea, submitted as a name/value pair with form data.
        value: The default value of the form control. Primarily used for resetting the form control.
        size: The textarea's size.
        appearance: The textarea's visual appearance.
        label: The textarea's label. If you need to display HTML, use the `label` slot instead.
        hint: The textarea's hint. If you need to display HTML, use the `hint` slot instead.
        placeholder: Placeholder text to show as a hint when the input is empty.
        rows: The number of rows to display by default.
        resize: Controls how the textarea can be resized.
        disabled: Disables the textarea.
        readonly: Makes the textarea readonly.
        form: By default, form controls are associated with the nearest containing `<form>` element. This attribute allows you
            to place the form control outside of a form and associate it with the form that has this `id`. The form must be in
            the same document or shadow root for this to work.
        required: Makes the textarea a required field.
        minlength: The minimum length of input that will be considered valid.
        maxlength: The maximum length of input that will be considered valid.
        autocapitalize: Controls whether and how text input is automatically capitalized as it is entered by the user.
        autocorrect: Indicates whether the browser's autocorrect feature is on or off.
        autocomplete: Specifies what permission the browser has to provide assistance in filling out form field values. Refer to
            [this page on MDN](https://developer.mozilla.org/en-US/docs/Web/HTML/Attributes/autocomplete) for available values.
        autofocus: Indicates that the input should receive focus on page load.
        enterkeyhint: Used to customize the label or icon of the Enter key on virtual keyboards.
        spellcheck: Enables spell checking on the textarea.
        inputmode: Tells the browser what type of data will be entered by the user, allowing it to display the appropriate virtual
            keyboard on supportive devices.
        with_label: Used for SSR. If you're slotting in a `label` element, make sure to set this to `true`.
        with_hint: Used for SSR. If you're slotting in a `hint` element, make sure to set this to `true`.
        **attributes: Additional HTML attributes

    Slots:
        label: The textarea's label. Alternatively, you can use the `label` attribute.
        hint: Text that describes how to use the input. Alternatively, you can use the `hint` attribute.
    """
    def __init__(
        self,
        *children: ChildrenType,
        title: str | None = ...,
        name: str | bool | None = ...,
        value: str | None = ...,
        size: Literal["small", "medium", "large"] | None = ...,
        appearance: Literal["filled", "outlined", "filled-outlined"] | None = ...,
        label: str | None = ...,
        hint: str | None = ...,
        placeholder: str | None = ...,
        rows: int | float | None = ...,
        resize: Literal["none", "vertical", "horizontal", "both", "auto"] | None = ...,
        disabled: bool | None = ...,
        readonly: bool | None = ...,
        form: str | bool | None = ...,
        required: bool | None = ...,
        minlength: int | float | None = ...,
        maxlength: int | float | None = ...,
        autocapitalize: Literal["off", "none", "on", "sentences", "words", "characters"] | None = ...,
        autocorrect: str | None = ...,
        autocomplete: str | None = ...,
        autofocus: bool | None = ...,
        enterkeyhint: Literal["enter", "done", "go", "next", "previous", "search", "send"] | None = ...,
        spellcheck: bool | None = ...,
        inputmode: Literal["none", "text", "decimal", "numeric", "tel", "search", "email", "url"] | None = ...,
        with_label: bool | None = ...,
        with_hint: bool | None = ...,
        **attributes: AttributeType,
    ) -> None: ...

    def _get_tag_name(self) -> str: ...