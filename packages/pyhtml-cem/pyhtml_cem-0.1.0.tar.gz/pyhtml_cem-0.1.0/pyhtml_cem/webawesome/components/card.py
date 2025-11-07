"""
wa-card component.
"""

from typing import Literal
from pyhtml import Tag
from pyhtml.__types import ChildrenType, AttributeType


class card(Tag):
    """
    wa-card web component.

    Args:
        *children: Child elements and text content
        appearance: The card's visual appearance.
        with_header: Renders the card with a header. Only needed for SSR, otherwise is automatically added.
        with_media: Renders the card with an image. Only needed for SSR, otherwise is automatically added.
        with_footer: Renders the card with a footer. Only needed for SSR, otherwise is automatically added.
        orientation: Renders the card's orientation *
        **attributes: Additional HTML attributes

    Slots:
        : The card's main content.
        header: An optional header for the card.
        footer: An optional footer for the card.
        media: An optional media section to render at the start of the card.
        actions: An optional actions section to render at the end for the horizontal card.
        header-actions: An optional actions section to render in the header of the vertical card.
        footer-actions: An optional actions section to render in the footer of the vertical card.
    """
    def __init__(
        self,
        *children: ChildrenType,
        appearance: Literal["accent", "filled", "outlined", "plain"] | None = None,
        with_header: bool | None = None,
        with_media: bool | None = None,
        with_footer: bool | None = None,
        orientation: Literal["horizontal", "vertical"] | None = None,
        **attributes: AttributeType,
    ) -> None:
        # Build attributes dict, filtering out None values
        attributes = attributes.copy()
        attributes.update({
            'appearance': appearance,
            'with_header': with_header,
            'with_media': with_media,
            'with_footer': with_footer,
            'orientation': orientation,
        })
        # Filter out None values and False booleans, convert numbers to strings
        attributes = {
            k: str(v) if isinstance(v, (int, float)) and not isinstance(v, bool) else v
            for k, v in attributes.items()
            if v is not None and v is not False
        }
        super().__init__(*children, **attributes)

    def _get_tag_name(self) -> str:
        return "wa-card"


__all__ = [
    "card",
]