"""
wa-icon component.
"""

from typing import Literal
from pyhtml import Tag
from pyhtml.__types import ChildrenType, AttributeType


class icon(Tag):
    """
    wa-icon web component.

    Args:
        *children: Child elements and text content
        name: The name of the icon to draw. Available names depend on the icon library being used.
        family: The family of icons to choose from. For Font Awesome Free, valid options include `classic` and `brands`. For
            Font Awesome Pro subscribers, valid options include, `classic`, `sharp`, `duotone`, `sharp-duotone`, and `brands`.
            A valid kit code must be present to show pro icons via CDN. You can set `<html data-fa-kit-code="...">` to provide
            one.
        variant: The name of the icon's variant. For Font Awesome, valid options include `thin`, `light`, `regular`, and `solid` for
            the `classic` and `sharp` families. Some variants require a Font Awesome Pro subscription. Custom icon libraries
            may or may not use this property.
        auto_width: Sets the width of the icon to match the cropped SVG viewBox. This operates like the Font `fa-width-auto` class.
        swap_opacity: Swaps the opacity of duotone icons.
        src: An external URL of an SVG file. Be sure you trust the content you are including, as it will be executed as code and
            can result in XSS attacks.
        label: An alternate description to use for assistive devices. If omitted, the icon will be considered presentational and
            ignored by assistive devices.
        library: The name of a registered custom icon library.
        **attributes: Additional HTML attributes
    """
    def __init__(
        self,
        *children: ChildrenType,
        name: str | bool | None = None,
        family: str | None = None,
        variant: str | None = None,
        auto_width: bool | None = None,
        swap_opacity: bool | None = None,
        src: str | bool | None = None,
        label: str | None = None,
        library: str | None = None,
        **attributes: AttributeType,
    ) -> None:
        # Build attributes dict, filtering out None values
        attributes = attributes.copy()
        attributes.update({
            'name': name,
            'family': family,
            'variant': variant,
            'auto_width': auto_width,
            'swap_opacity': swap_opacity,
            'src': src,
            'label': label,
            'library': library,
        })
        # Filter out None values and False booleans, convert numbers to strings
        attributes = {
            k: str(v) if isinstance(v, (int, float)) and not isinstance(v, bool) else v
            for k, v in attributes.items()
            if v is not None and v is not False
        }
        super().__init__(*children, **attributes)

    def _get_tag_name(self) -> str:
        return "wa-icon"


__all__ = [
    "icon",
]