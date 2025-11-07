"""Type stub for wa-carousel component."""

from typing import Literal
from pyhtml import Tag
from pyhtml.__types import ChildrenType, AttributeType


class carousel(Tag):
    """
    wa-carousel web component.

    Args:
        *children: Child elements and text content
        loop: When set, allows the user to navigate the carousel in the same direction indefinitely.
        slides: Type: number
        currentSlide: Type: number
        navigation: When set, show the carousel's navigation.
        pagination: When set, show the carousel's pagination indicators.
        autoplay: When set, the slides will scroll automatically when the user is not interacting with them.
        autoplay_interval: Specifies the amount of time, in milliseconds, between each automatic scroll.
        slides_per_page: Specifies how many slides should be shown at a given time.
        slides_per_move: Specifies the number of slides the carousel will advance when scrolling, useful when specifying a `slides-per-page`
            greater than one. It can't be higher than `slides-per-page`.
        orientation: Specifies the orientation in which the carousel will lay out.
        mouse_dragging: When set, it is possible to scroll through the slides by dragging them with the mouse.
        **attributes: Additional HTML attributes

    Slots:
        : The carousel's main content, one or more `<wa-carousel-item>` elements.
        next-icon: Optional next icon to use instead of the default. Works best with `<wa-icon>`.
        previous-icon: Optional previous icon to use instead of the default. Works best with `<wa-icon>`.
    """
    def __init__(
        self,
        *children: ChildrenType,
        loop: bool | None = ...,
        slides: int | float | None = ...,
        currentSlide: int | float | None = ...,
        navigation: bool | None = ...,
        pagination: bool | None = ...,
        autoplay: bool | None = ...,
        autoplay_interval: int | float | None = ...,
        slides_per_page: int | float | None = ...,
        slides_per_move: int | float | None = ...,
        orientation: Literal["horizontal", "vertical"] | None = ...,
        mouse_dragging: bool | None = ...,
        **attributes: AttributeType,
    ) -> None: ...

    def _get_tag_name(self) -> str: ...