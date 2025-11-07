"""
wa-slider component.
"""

from typing import Literal
from pyhtml import Tag
from pyhtml.__types import ChildrenType, AttributeType


class slider(Tag):
    """
    <wa-slider>

    Args:
        *children: Child elements and text content
        label: The slider's label. If you need to provide HTML in the label, use the `label` slot instead.
        hint: The slider hint. If you need to display HTML, use the hint slot instead.
        name: The name of the slider. This will be submitted with the form as a name/value pair.
        min_value: The minimum value of a range selection. Used only when range attribute is set.
        max_value: The maximum value of a range selection. Used only when range attribute is set.
        value: The default value of the form control. Primarily used for resetting the form control.
        range: Converts the slider to a range slider with two thumbs.
        disabled: Disables the slider.
        readonly: Makes the slider a read-only field.
        orientation: The orientation of the slider.
        size: The slider's size.
        indicator_offset: The starting value from which to draw the slider's fill, which is based on its current value.
        form: The form to associate this control with. If omitted, the closest containing `<form>` will be used. The value of
            this attribute must be an ID of a form in the same document or shadow root.
        min: The minimum value allowed.
        max: The maximum value allowed.
        step: The granularity the value must adhere to when incrementing and decrementing.
        required: Makes the slider a required field.
        autofocus: Tells the browser to focus the slider when the page loads or a dialog is shown.
        tooltip_distance: The distance of the tooltip from the slider's thumb.
        tooltip_placement: The placement of the tooltip in reference to the slider's thumb.
        with_markers: Draws markers at each step along the slider.
        with_tooltip: Draws a tooltip above the thumb when the control has focus or is dragged.
        **attributes: Additional HTML attributes

    Slots:
        label: The slider label. Alternatively, you can use the `label` attribute.
        hint: Text that describes how to use the input. Alternatively, you can use the `hint` attribute. instead.
        reference: One or more reference labels to show visually below the slider.
    """
    def __init__(
        self,
        *children: ChildrenType,
        label: str | None = None,
        hint: str | None = None,
        name: str | None = None,
        min_value: int | float | None = None,
        max_value: int | float | None = None,
        value: int | float | None = None,
        range: bool | None = None,
        disabled: bool | None = None,
        readonly: bool | None = None,
        orientation: Literal["horizontal", "vertical"] | None = None,
        size: Literal["small", "medium", "large"] | None = None,
        indicator_offset: int | float | None = None,
        form: str | bool | None = None,
        min: int | float | None = None,
        max: int | float | None = None,
        step: int | float | None = None,
        required: bool | None = None,
        autofocus: bool | None = None,
        tooltip_distance: int | float | None = None,
        tooltip_placement: Literal["top", "right", "bottom", "left"] | None = None,
        with_markers: bool | None = None,
        with_tooltip: bool | None = None,
        **attributes: AttributeType,
    ) -> None:
        # Build attributes dict, filtering out None values
        attributes = attributes.copy()
        attributes.update({
            'label': label,
            'hint': hint,
            'name': name,
            'min_value': min_value,
            'max_value': max_value,
            'value': value,
            'range': range,
            'disabled': disabled,
            'readonly': readonly,
            'orientation': orientation,
            'size': size,
            'indicator_offset': indicator_offset,
            'form': form,
            'min': min,
            'max': max,
            'step': step,
            'required': required,
            'autofocus': autofocus,
            'tooltip_distance': tooltip_distance,
            'tooltip_placement': tooltip_placement,
            'with_markers': with_markers,
            'with_tooltip': with_tooltip,
        })
        # Filter out None values and False booleans, convert numbers to strings
        attributes = {
            k: str(v) if isinstance(v, (int, float)) and not isinstance(v, bool) else v
            for k, v in attributes.items()
            if v is not None and v is not False
        }
        super().__init__(*children, **attributes)

    def _get_tag_name(self) -> str:
        return "wa-slider"


__all__ = [
    "slider",
]