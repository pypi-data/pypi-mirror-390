"""
wa-tag component.
"""

from typing import Literal
from pyhtml import Tag
from pyhtml.__types import ChildrenType, AttributeType


class tag(Tag):
    """
    wa-tag web component.

    Args:
        *children: Child elements and text content
        variant: The tag's theme variant. Defaults to `neutral` if not within another element with a variant.
        appearance: The tag's visual appearance.
        size: The tag's size.
        pill: Draws a pill-style tag with rounded edges.
        with_remove: Makes the tag removable and shows a remove button.
        **attributes: Additional HTML attributes

    Slots:
        : The tag's content.
    """
    def __init__(
        self,
        *children: ChildrenType,
        variant: Literal["brand", "neutral", "success", "warning", "danger"] | None = None,
        appearance: Literal["accent", "filled", "outlined", "filled-outlined"] | None = None,
        size: Literal["small", "medium", "large"] | None = None,
        pill: bool | None = None,
        with_remove: bool | None = None,
        **attributes: AttributeType,
    ) -> None:
        # Build attributes dict, filtering out None values
        attributes = attributes.copy()
        attributes.update({
            'variant': variant,
            'appearance': appearance,
            'size': size,
            'pill': pill,
            'with_remove': with_remove,
        })
        # Filter out None values and False booleans, convert numbers to strings
        attributes = {
            k: str(v) if isinstance(v, (int, float)) and not isinstance(v, bool) else v
            for k, v in attributes.items()
            if v is not None and v is not False
        }
        super().__init__(*children, **attributes)

    def _get_tag_name(self) -> str:
        return "wa-tag"


__all__ = [
    "tag",
]