"""
wa-format-number component.
"""

from typing import Literal
from pyhtml import Tag
from pyhtml.__types import ChildrenType, AttributeType


class format_number(Tag):
    """
    wa-format-number web component.

    Args:
        *children: Child elements and text content
        value: The number to format.
        type: The formatting style to use.
        without_grouping: Turns off grouping separators.
        currency: The [ISO 4217](https://en.wikipedia.org/wiki/ISO_4217) currency code to use when formatting.
        currency_display: How to display the currency.
        minimum_integer_digits: The minimum number of integer digits to use. Possible values are 1-21.
        minimum_fraction_digits: The minimum number of fraction digits to use. Possible values are 0-100.
        maximum_fraction_digits: The maximum number of fraction digits to use. Possible values are 0-100.
        minimum_significant_digits: The minimum number of significant digits to use. Possible values are 1-21.
        maximum_significant_digits: The maximum number of significant digits to use,. Possible values are 1-21.
        **attributes: Additional HTML attributes
    """
    def __init__(
        self,
        *children: ChildrenType,
        value: int | float | None = None,
        type: Literal["currency", "decimal", "percent"] | None = None,
        without_grouping: bool | None = None,
        currency: str | None = None,
        currency_display: Literal["symbol", "narrowSymbol", "code", "name"] | None = None,
        minimum_integer_digits: int | float | None = None,
        minimum_fraction_digits: int | float | None = None,
        maximum_fraction_digits: int | float | None = None,
        minimum_significant_digits: int | float | None = None,
        maximum_significant_digits: int | float | None = None,
        **attributes: AttributeType,
    ) -> None:
        # Build attributes dict, filtering out None values
        attributes = attributes.copy()
        attributes.update({
            'value': value,
            'type': type,
            'without_grouping': without_grouping,
            'currency': currency,
            'currency_display': currency_display,
            'minimum_integer_digits': minimum_integer_digits,
            'minimum_fraction_digits': minimum_fraction_digits,
            'maximum_fraction_digits': maximum_fraction_digits,
            'minimum_significant_digits': minimum_significant_digits,
            'maximum_significant_digits': maximum_significant_digits,
        })
        # Filter out None values and False booleans, convert numbers to strings
        attributes = {
            k: str(v) if isinstance(v, (int, float)) and not isinstance(v, bool) else v
            for k, v in attributes.items()
            if v is not None and v is not False
        }
        super().__init__(*children, **attributes)

    def _get_tag_name(self) -> str:
        return "wa-format-number"


__all__ = [
    "format_number",
]