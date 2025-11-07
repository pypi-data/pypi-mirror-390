"""
wa-zoomable-frame component.
"""

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
        src: str | None = None,
        srcdoc: str | None = None,
        allowfullscreen: bool | None = None,
        loading: Literal["eager", "lazy"] | None = None,
        referrerpolicy: str | None = None,
        sandbox: str | None = None,
        zoom: int | float | None = None,
        zoom_levels: str | None = None,
        without_controls: bool | None = None,
        without_interaction: bool | None = None,
        **attributes: AttributeType,
    ) -> None:
        # Build attributes dict, filtering out None values
        attributes = attributes.copy()
        attributes.update({
            'src': src,
            'srcdoc': srcdoc,
            'allowfullscreen': allowfullscreen,
            'loading': loading,
            'referrerpolicy': referrerpolicy,
            'sandbox': sandbox,
            'zoom': zoom,
            'zoom_levels': zoom_levels,
            'without_controls': without_controls,
            'without_interaction': without_interaction,
        })
        # Filter out None values and False booleans, convert numbers to strings
        attributes = {
            k: str(v) if isinstance(v, (int, float)) and not isinstance(v, bool) else v
            for k, v in attributes.items()
            if v is not None and v is not False
        }
        super().__init__(*children, **attributes)

    def _get_tag_name(self) -> str:
        return "wa-zoomable-frame"


__all__ = [
    "zoomable_frame",
]