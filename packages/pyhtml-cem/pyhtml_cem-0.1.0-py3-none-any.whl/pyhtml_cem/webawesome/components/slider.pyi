"""Type stub for wa-slider component."""

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
        label: str | None = ...,
        hint: str | None = ...,
        name: str | None = ...,
        min_value: int | float | None = ...,
        max_value: int | float | None = ...,
        value: int | float | None = ...,
        range: bool | None = ...,
        disabled: bool | None = ...,
        readonly: bool | None = ...,
        orientation: Literal["horizontal", "vertical"] | None = ...,
        size: Literal["small", "medium", "large"] | None = ...,
        indicator_offset: int | float | None = ...,
        form: str | bool | None = ...,
        min: int | float | None = ...,
        max: int | float | None = ...,
        step: int | float | None = ...,
        required: bool | None = ...,
        autofocus: bool | None = ...,
        tooltip_distance: int | float | None = ...,
        tooltip_placement: Literal["top", "right", "bottom", "left"] | None = ...,
        with_markers: bool | None = ...,
        with_tooltip: bool | None = ...,
        **attributes: AttributeType,
    ) -> None: ...

    def _get_tag_name(self) -> str: ...