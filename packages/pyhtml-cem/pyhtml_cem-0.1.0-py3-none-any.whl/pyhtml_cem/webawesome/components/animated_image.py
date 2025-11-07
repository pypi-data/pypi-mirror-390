"""
wa-animated-image component.
"""

from typing import Literal
from pyhtml import Tag
from pyhtml.__types import ChildrenType, AttributeType


class animated_image(Tag):
    """
    wa-animated-image web component.

    Args:
        *children: Child elements and text content
        src: The path to the image to load.
        alt: A description of the image used by assistive devices.
        play: Plays the animation. When this attribute is remove, the animation will pause.
        **attributes: Additional HTML attributes

    Slots:
        play-icon: Optional play icon to use instead of the default. Works best with `<wa-icon>`.
        pause-icon: Optional pause icon to use instead of the default. Works best with `<wa-icon>`.
    """
    def __init__(
        self,
        *children: ChildrenType,
        src: str | None = None,
        alt: str | None = None,
        play: bool | None = None,
        **attributes: AttributeType,
    ) -> None:
        # Build attributes dict, filtering out None values
        attributes = attributes.copy()
        attributes.update({
            'src': src,
            'alt': alt,
            'play': play,
        })
        # Filter out None values and False booleans, convert numbers to strings
        attributes = {
            k: str(v) if isinstance(v, (int, float)) and not isinstance(v, bool) else v
            for k, v in attributes.items()
            if v is not None and v is not False
        }
        super().__init__(*children, **attributes)

    def _get_tag_name(self) -> str:
        return "wa-animated-image"


__all__ = [
    "animated_image",
]