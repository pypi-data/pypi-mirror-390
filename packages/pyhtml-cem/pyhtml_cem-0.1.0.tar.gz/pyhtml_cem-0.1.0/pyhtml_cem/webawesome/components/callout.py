"""
wa-callout component.
"""

from typing import Literal
from pyhtml import Tag
from pyhtml.__types import ChildrenType, AttributeType


class callout(Tag):
    """
    wa-callout web component.

    Args:
        *children: Child elements and text content
        variant: The callout's theme variant. Defaults to `brand` if not within another element with a variant.
        appearance: The callout's visual appearance.
        size: The callout's size.
        **attributes: Additional HTML attributes

    Slots:
        : The callout's main content.
        icon: An icon to show in the callout. Works best with `<wa-icon>`.
    """
    def __init__(
        self,
        *children: ChildrenType,
        variant: Literal["brand", "neutral", "success", "warning", "danger"] | None = None,
        appearance: Literal["accent", "filled", "outlined", "plain", "filled-outlined"] | None = None,
        size: Literal["small", "medium", "large"] | None = None,
        **attributes: AttributeType,
    ) -> None:
        # Build attributes dict, filtering out None values
        attributes = attributes.copy()
        attributes.update({
            'variant': variant,
            'appearance': appearance,
            'size': size,
        })
        # Filter out None values and False booleans, convert numbers to strings
        attributes = {
            k: str(v) if isinstance(v, (int, float)) and not isinstance(v, bool) else v
            for k, v in attributes.items()
            if v is not None and v is not False
        }
        super().__init__(*children, **attributes)

    def _get_tag_name(self) -> str:
        return "wa-callout"


__all__ = [
    "callout",
]