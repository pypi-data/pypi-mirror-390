"""Type stub for wa-format-number component."""

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
        value: int | float | None = ...,
        type: Literal["currency", "decimal", "percent"] | None = ...,
        without_grouping: bool | None = ...,
        currency: str | None = ...,
        currency_display: Literal["symbol", "narrowSymbol", "code", "name"] | None = ...,
        minimum_integer_digits: int | float | None = ...,
        minimum_fraction_digits: int | float | None = ...,
        maximum_fraction_digits: int | float | None = ...,
        minimum_significant_digits: int | float | None = ...,
        maximum_significant_digits: int | float | None = ...,
        **attributes: AttributeType,
    ) -> None: ...

    def _get_tag_name(self) -> str: ...