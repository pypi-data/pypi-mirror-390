"""
wa-color-picker component.
"""

from typing import Literal
from pyhtml import Tag
from pyhtml.__types import ChildrenType, AttributeType


class color_picker(Tag):
    """
    wa-color-picker web component.

    Args:
        *children: Child elements and text content
        value: The default value of the form control. Primarily used for resetting the form control.
        with_label: Type: boolean
        with_hint: Type: boolean
        label: The color picker's label. This will not be displayed, but it will be announced by assistive devices. If you need to
            display HTML, you can use the `label` slot` instead.
        hint: The color picker's hint. If you need to display HTML, use the `hint` slot instead.
        format: The format to use. If opacity is enabled, these will translate to HEXA, RGBA, HSLA, and HSVA respectively. The color
            picker will accept user input in any format (including CSS color names) and convert it to the desired format.
        size: Determines the size of the color picker's trigger
        without_format_toggle: Removes the button that lets users toggle between format.
        name: The name of the form control, submitted as a name/value pair with form data.
        disabled: Disables the color picker.
        open: Indicates whether or not the popup is open. You can toggle this attribute to show and hide the popup, or you
            can use the `show()` and `hide()` methods and this attribute will reflect the popup's open state.
        opacity: Shows the opacity slider. Enabling this will cause the formatted value to be HEXA, RGBA, or HSLA.
        uppercase: By default, values are lowercase. With this attribute, values will be uppercase instead.
        swatches: One or more predefined color swatches to display as presets in the color picker. Can include any format the color
            picker can parse, including HEX(A), RGB(A), HSL(A), HSV(A), and CSS color names. Each color must be separated by a
            semicolon (`;`). Alternatively, you can pass an array of color values to this property using JavaScript.
        form: By default, form controls are associated with the nearest containing `<form>` element. This attribute allows you
            to place the form control outside of a form and associate it with the form that has this `id`. The form must be in
            the same document or shadow root for this to work.
        required: Makes the color picker a required field.
        **attributes: Additional HTML attributes

    Slots:
        label: The color picker's form label. Alternatively, you can use the `label` attribute.
        hint: The color picker's form hint. Alternatively, you can use the `hint` attribute.
    """
    def __init__(
        self,
        *children: ChildrenType,
        value: str | bool | None = None,
        with_label: bool | None = None,
        with_hint: bool | None = None,
        label: str | None = None,
        hint: str | None = None,
        format: Literal["hex", "rgb", "hsl", "hsv"] | None = None,
        size: Literal["small", "medium", "large"] | None = None,
        without_format_toggle: bool | None = None,
        name: str | bool | None = None,
        disabled: bool | None = None,
        open: bool | None = None,
        opacity: bool | None = None,
        uppercase: bool | None = None,
        swatches: str | bool | None = None,
        form: str | bool | None = None,
        required: bool | None = None,
        **attributes: AttributeType,
    ) -> None:
        # Build attributes dict, filtering out None values
        attributes = attributes.copy()
        attributes.update({
            'value': value,
            'with_label': with_label,
            'with_hint': with_hint,
            'label': label,
            'hint': hint,
            'format': format,
            'size': size,
            'without_format_toggle': without_format_toggle,
            'name': name,
            'disabled': disabled,
            'open': open,
            'opacity': opacity,
            'uppercase': uppercase,
            'swatches': swatches,
            'form': form,
            'required': required,
        })
        # Filter out None values and False booleans, convert numbers to strings
        attributes = {
            k: str(v) if isinstance(v, (int, float)) and not isinstance(v, bool) else v
            for k, v in attributes.items()
            if v is not None and v is not False
        }
        super().__init__(*children, **attributes)

    def _get_tag_name(self) -> str:
        return "wa-color-picker"


__all__ = [
    "color_picker",
]