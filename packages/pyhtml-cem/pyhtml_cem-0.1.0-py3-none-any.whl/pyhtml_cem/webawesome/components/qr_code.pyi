"""Type stub for wa-qr-code component."""

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
        value: str | None = ...,
        label: str | None = ...,
        size: int | float | None = ...,
        fill: str | None = ...,
        background: str | None = ...,
        radius: int | float | None = ...,
        error_correction: Literal["L", "M", "Q", "H"] | None = ...,
        **attributes: AttributeType,
    ) -> None: ...

    def _get_tag_name(self) -> str: ...