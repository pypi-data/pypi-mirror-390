"""
wa-textarea component.
"""

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
        title: str | None = None,
        name: str | bool | None = None,
        value: str | None = None,
        size: Literal["small", "medium", "large"] | None = None,
        appearance: Literal["filled", "outlined", "filled-outlined"] | None = None,
        label: str | None = None,
        hint: str | None = None,
        placeholder: str | None = None,
        rows: int | float | None = None,
        resize: Literal["none", "vertical", "horizontal", "both", "auto"] | None = None,
        disabled: bool | None = None,
        readonly: bool | None = None,
        form: str | bool | None = None,
        required: bool | None = None,
        minlength: int | float | None = None,
        maxlength: int | float | None = None,
        autocapitalize: Literal["off", "none", "on", "sentences", "words", "characters"] | None = None,
        autocorrect: str | None = None,
        autocomplete: str | None = None,
        autofocus: bool | None = None,
        enterkeyhint: Literal["enter", "done", "go", "next", "previous", "search", "send"] | None = None,
        spellcheck: bool | None = None,
        inputmode: Literal["none", "text", "decimal", "numeric", "tel", "search", "email", "url"] | None = None,
        with_label: bool | None = None,
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
            'appearance': appearance,
            'label': label,
            'hint': hint,
            'placeholder': placeholder,
            'rows': rows,
            'resize': resize,
            'disabled': disabled,
            'readonly': readonly,
            'form': form,
            'required': required,
            'minlength': minlength,
            'maxlength': maxlength,
            'autocapitalize': autocapitalize,
            'autocorrect': autocorrect,
            'autocomplete': autocomplete,
            'autofocus': autofocus,
            'enterkeyhint': enterkeyhint,
            'spellcheck': spellcheck,
            'inputmode': inputmode,
            'with_label': with_label,
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
        return "wa-textarea"


__all__ = [
    "textarea",
]