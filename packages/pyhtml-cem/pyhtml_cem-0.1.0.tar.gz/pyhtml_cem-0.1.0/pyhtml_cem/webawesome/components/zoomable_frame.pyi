"""Type stub for wa-zoomable-frame component."""

from typing import Literal
from pyhtml import Tag
from pyhtml.__types import ChildrenType, AttributeType


class zoomable_frame(Tag):
    """
    wa-zoomable-frame web component.

    Args:
        *children: Child elements and text content
        src: The URL of the content to display.
        srcdoc: Inline HTML to display.
        allowfullscreen: Allows fullscreen mode.
        loading: Controls iframe loading behavior.
        referrerpolicy: Controls referrer information.
        sandbox: Security restrictions for the iframe.
        zoom: The current zoom of the frame, e.g. 0 = 0% and 1 = 100%.
        zoom_levels: The zoom levels to step through when using zoom controls. This does not restrict programmatic changes to the zoom.
        without_controls: Removes the zoom controls.
        without_interaction: Disables interaction when present.
        **attributes: Additional HTML attributes

    Slots:
        zoom-in-icon: The slot that contains the zoom in icon.
        zoom-out-icon: The slot that contains the zoom out icon.
    """
    def __init__(
        self,
        *children: ChildrenType,
        src: str | None = ...,
        srcdoc: str | None = ...,
        allowfullscreen: bool | None = ...,
        loading: Literal["eager", "lazy"] | None = ...,
        referrerpolicy: str | None = ...,
        sandbox: str | None = ...,
        zoom: int | float | None = ...,
        zoom_levels: str | None = ...,
        without_controls: bool | None = ...,
        without_interaction: bool | None = ...,
        **attributes: AttributeType,
    ) -> None: ...

    def _get_tag_name(self) -> str: ...