"""
wa-qr-code component.
"""

from typing import Literal
from pyhtml import Tag
from pyhtml.__types import ChildrenType, AttributeType


class qr_code(Tag):
    """
    wa-qr-code web component.

    Args:
        *children: Child elements and text content
        value: The QR code's value.
        label: The label for assistive devices to announce. If unspecified, the value will be used instead.
        size: The size of the QR code, in pixels.
        fill: The fill color. This can be any valid CSS color, but not a CSS custom property.
        background: The background color. This can be any valid CSS color or `transparent`. It cannot be a CSS custom property.
        radius: The edge radius of each module. Must be between 0 and 0.5.
        error_correction: The level of error correction to use. [Learn more](https://www.qrcode.com/en/about/error_correction.html)
        **attributes: Additional HTML attributes
    """
    def __init__(
        self,
        *children: ChildrenType,
        value: str | None = None,
        label: str | None = None,
        size: int | float | None = None,
        fill: str | None = None,
        background: str | None = None,
        radius: int | float | None = None,
        error_correction: Literal["L", "M", "Q", "H"] | None = None,
        **attributes: AttributeType,
    ) -> None:
        # Build attributes dict, filtering out None values
        attributes = attributes.copy()
        attributes.update({
            'value': value,
            'label': label,
            'size': size,
            'fill': fill,
            'background': background,
            'radius': radius,
            'error_correction': error_correction,
        })
        # Filter out None values and False booleans, convert numbers to strings
        attributes = {
            k: str(v) if isinstance(v, (int, float)) and not isinstance(v, bool) else v
            for k, v in attributes.items()
            if v is not None and v is not False
        }
        super().__init__(*children, **attributes)

    def _get_tag_name(self) -> str:
        return "wa-qr-code"


__all__ = [
    "qr_code",
]