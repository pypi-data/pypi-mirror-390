"""
wa-rating component.
"""

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
        label: str | None = None,
        value: int | float | None = None,
        max: int | float | None = None,
        precision: int | float | None = None,
        readonly: bool | None = None,
        disabled: bool | None = None,
        getSymbol: str | bool | None = None,
        size: Literal["small", "medium", "large"] | None = None,
        **attributes: AttributeType,
    ) -> None:
        # Build attributes dict, filtering out None values
        attributes = attributes.copy()
        attributes.update({
            'label': label,
            'value': value,
            'max': max,
            'precision': precision,
            'readonly': readonly,
            'disabled': disabled,
            'getSymbol': getSymbol,
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
        return "wa-rating"


__all__ = [
    "rating",
]