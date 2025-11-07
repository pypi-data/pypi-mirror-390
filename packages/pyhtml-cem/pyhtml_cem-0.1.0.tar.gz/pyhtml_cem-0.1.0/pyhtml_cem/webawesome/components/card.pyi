"""Type stub for wa-card component."""

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
        appearance: Literal["accent", "filled", "outlined", "plain"] | None = ...,
        with_header: bool | None = ...,
        with_media: bool | None = ...,
        with_footer: bool | None = ...,
        orientation: Literal["horizontal", "vertical"] | None = ...,
        **attributes: AttributeType,
    ) -> None: ...

    def _get_tag_name(self) -> str: ...