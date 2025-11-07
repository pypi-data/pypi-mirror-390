"""
wa-input component.
"""

from typing import Literal
from pyhtml import Tag
from pyhtml.__types import ChildrenType, AttributeType


class input(Tag):
    """
    wa-input web component.

    Args:
        *children: Child elements and text content
        title: Type: string
        type: The type of input. Works the same as a native `<input>` element, but only a subset of types are supported. Defaults
            to `text`.
        value: The default value of the form control. Primarily used for resetting the form control.
        size: The input's size.
        appearance: The input's visual appearance.
        pill: Draws a pill-style input with rounded edges.
        label: The input's label. If you need to display HTML, use the `label` slot instead.
        hint: The input's hint. If you need to display HTML, use the `hint` slot instead.
        with_clear: Adds a clear button when the input is not empty.
        placeholder: Placeholder text to show as a hint when the input is empty.
        readonly: Makes the input readonly.
        password_toggle: Adds a button to toggle the password's visibility. Only applies to password types.
        password_visible: Determines whether or not the password is currently visible. Only applies to password input types.
        without_spin_buttons: Hides the browser's built-in increment/decrement spin buttons for number inputs.
        form: By default, form controls are associated with the nearest containing `<form>` element. This attribute allows you
            to place the form control outside of a form and associate it with the form that has this `id`. The form must be in
            the same document or shadow root for this to work.
        required: Makes the input a required field.
        pattern: A regular expression pattern to validate input against.
        minlength: The minimum length of input that will be considered valid.
        maxlength: The maximum length of input that will be considered valid.
        min: The input's minimum value. Only applies to date and number input types.
        max: The input's maximum value. Only applies to date and number input types.
        step: Specifies the granularity that the value must adhere to, or the special value `any` which means no stepping is
            implied, allowing any numeric value. Only applies to date and number input types.
        autocapitalize: Controls whether and how text input is automatically capitalized as it is entered by the user.
        autocorrect: Indicates whether the browser's autocorrect feature is on or off.
        autocomplete: Specifies what permission the browser has to provide assistance in filling out form field values. Refer to
            [this page on MDN](https://developer.mozilla.org/en-US/docs/Web/HTML/Attributes/autocomplete) for available values.
        autofocus: Indicates that the input should receive focus on page load.
        enterkeyhint: Used to customize the label or icon of the Enter key on virtual keyboards.
        spellcheck: Enables spell checking on the input.
        inputmode: Tells the browser what type of data will be entered by the user, allowing it to display the appropriate virtual
            keyboard on supportive devices.
        with_label: Used for SSR. Will determine if the SSRed component will have the label slot rendered on initial paint.
        with_hint: Used for SSR. Will determine if the SSRed component will have the hint slot rendered on initial paint.
        **attributes: Additional HTML attributes

    Slots:
        label: The input's label. Alternatively, you can use the `label` attribute.
        start: An element, such as `<wa-icon>`, placed at the start of the input control.
        end: An element, such as `<wa-icon>`, placed at the end of the input control.
        clear-icon: An icon to use in lieu of the default clear icon.
        show-password-icon: An icon to use in lieu of the default show password icon.
        hide-password-icon: An icon to use in lieu of the default hide password icon.
        hint: Text that describes how to use the input. Alternatively, you can use the `hint` attribute.
    """
    def __init__(
        self,
        *children: ChildrenType,
        title: str | None = None,
        type: Literal["date", "datetime-local", "email", "number", "password", "search", "tel", "text", "time", "url"] | None = None,
        value: str | bool | None = None,
        size: Literal["small", "medium", "large"] | None = None,
        appearance: Literal["filled", "outlined", "filled-outlined"] | None = None,
        pill: bool | None = None,
        label: str | None = None,
        hint: str | None = None,
        with_clear: bool | None = None,
        placeholder: str | None = None,
        readonly: bool | None = None,
        password_toggle: bool | None = None,
        password_visible: bool | None = None,
        without_spin_buttons: bool | None = None,
        form: str | bool | None = None,
        required: bool | None = None,
        pattern: str | None = None,
        minlength: int | float | None = None,
        maxlength: int | float | None = None,
        min: str | bool | None = None,
        max: str | bool | None = None,
        step: Literal["any"] | None = None,
        autocapitalize: Literal["off", "none", "on", "sentences", "words", "characters"] | None = None,
        autocorrect: Literal["off", "on"] | None = None,
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
            'type': type,
            'value': value,
            'size': size,
            'appearance': appearance,
            'pill': pill,
            'label': label,
            'hint': hint,
            'with_clear': with_clear,
            'placeholder': placeholder,
            'readonly': readonly,
            'password_toggle': password_toggle,
            'password_visible': password_visible,
            'without_spin_buttons': without_spin_buttons,
            'form': form,
            'required': required,
            'pattern': pattern,
            'minlength': minlength,
            'maxlength': maxlength,
            'min': min,
            'max': max,
            'step': step,
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
        return "wa-input"


__all__ = [
    "input",
]