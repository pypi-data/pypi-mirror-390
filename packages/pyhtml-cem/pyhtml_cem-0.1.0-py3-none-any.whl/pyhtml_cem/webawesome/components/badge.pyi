"""Type stub for wa-badge component."""

from typing import Literal
from pyhtml import Tag
from pyhtml.__types import ChildrenType, AttributeType


class badge(Tag):
    """
    wa-badge web component.

    Args:
        *children: Child elements and text content
        variant: The badge's theme variant. Defaults to `brand` if not within another element with a variant.
        appearance: The badge's visual appearance.
        pill: Draws a pill-style badge with rounded edges.
        attention: Adds an animation to draw attention to the badge.
        **attributes: Additional HTML attributes

    Slots:
        : The badge's content.
    """
    def __init__(
        self,
        *children: ChildrenType,
        variant: Literal["brand", "neutral", "success", "warning", "danger"] | None = ...,
        appearance: Literal["accent", "filled", "outlined", "filled-outlined"] | None = ...,
        pill: bool | None = ...,
        attention: Literal["none", "pulse", "bounce"] | None = ...,
        **attributes: AttributeType,
    ) -> None: ...

    def _get_tag_name(self) -> str: ...