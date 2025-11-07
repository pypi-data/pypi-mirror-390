"""Type stub for wa-animated-image component."""

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
        src: str | None = ...,
        alt: str | None = ...,
        play: bool | None = ...,
        **attributes: AttributeType,
    ) -> None: ...

    def _get_tag_name(self) -> str: ...