"""Type stub for wa-tag component."""

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
        variant: Literal["brand", "neutral", "success", "warning", "danger"] | None = ...,
        appearance: Literal["accent", "filled", "outlined", "filled-outlined"] | None = ...,
        size: Literal["small", "medium", "large"] | None = ...,
        pill: bool | None = ...,
        with_remove: bool | None = ...,
        **attributes: AttributeType,
    ) -> None: ...

    def _get_tag_name(self) -> str: ...