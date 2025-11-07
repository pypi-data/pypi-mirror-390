"""Type stub for wa-callout component."""

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
        variant: Literal["brand", "neutral", "success", "warning", "danger"] | None = ...,
        appearance: Literal["accent", "filled", "outlined", "plain", "filled-outlined"] | None = ...,
        size: Literal["small", "medium", "large"] | None = ...,
        **attributes: AttributeType,
    ) -> None: ...

    def _get_tag_name(self) -> str: ...