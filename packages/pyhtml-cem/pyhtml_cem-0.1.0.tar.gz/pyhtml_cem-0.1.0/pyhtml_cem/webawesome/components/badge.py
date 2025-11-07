"""
wa-badge component.
"""

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
        variant: Literal["brand", "neutral", "success", "warning", "danger"] | None = None,
        appearance: Literal["accent", "filled", "outlined", "filled-outlined"] | None = None,
        pill: bool | None = None,
        attention: Literal["none", "pulse", "bounce"] | None = None,
        **attributes: AttributeType,
    ) -> None:
        # Build attributes dict, filtering out None values
        attributes = attributes.copy()
        attributes.update({
            'variant': variant,
            'appearance': appearance,
            'pill': pill,
            'attention': attention,
        })
        # Filter out None values and False booleans, convert numbers to strings
        attributes = {
            k: str(v) if isinstance(v, (int, float)) and not isinstance(v, bool) else v
            for k, v in attributes.items()
            if v is not None and v is not False
        }
        super().__init__(*children, **attributes)

    def _get_tag_name(self) -> str:
        return "wa-badge"


__all__ = [
    "badge",
]