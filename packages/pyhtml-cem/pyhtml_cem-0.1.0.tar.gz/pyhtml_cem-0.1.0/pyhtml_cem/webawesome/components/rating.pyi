"""Type stub for wa-rating component."""

from typing import Literal
from pyhtml import Tag
from pyhtml.__types import ChildrenType, AttributeType


class rating(Tag):
    """
    wa-rating web component.

    Args:
        *children: Child elements and text content
        label: A label that describes the rating to assistive devices.
        value: The current rating.
        max: The highest rating to show.
        precision: The precision at which the rating will increase and decrease. For example, to allow half-star ratings, set this
            attribute to `0.5`.
        readonly: Makes the rating readonly.
        disabled: Disables the rating.
        getSymbol: A function that customizes the symbol to be rendered. The first and only argument is the rating's current value.
            The function should return a string containing trusted HTML of the symbol to render at the specified value. Works
            well with `<wa-icon>` elements.
        size: The component's size.
        **attributes: Additional HTML attributes
    """
    def __init__(
        self,
        *children: ChildrenType,
        label: str | None = ...,
        value: int | float | None = ...,
        max: int | float | None = ...,
        precision: int | float | None = ...,
        readonly: bool | None = ...,
        disabled: bool | None = ...,
        getSymbol: str | bool | None = ...,
        size: Literal["small", "medium", "large"] | None = ...,
        **attributes: AttributeType,
    ) -> None: ...

    def _get_tag_name(self) -> str: ...