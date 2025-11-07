"""Type stub for wa-format-date component."""

from typing import Literal
from pyhtml import Tag
from pyhtml.__types import ChildrenType, AttributeType


class format_date(Tag):
    """
    wa-format-date web component.

    Args:
        *children: Child elements and text content
        date: The date/time to format. If not set, the current date and time will be used. When passing a string, it's strongly
            recommended to use the ISO 8601 format to ensure timezones are handled correctly. To convert a date to this format
            in JavaScript, use [`date.toISOString()`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Date/toISOString).
        weekday: The format for displaying the weekday.
        era: The format for displaying the era.
        year: The format for displaying the year.
        month: The format for displaying the month.
        day: The format for displaying the day.
        hour: The format for displaying the hour.
        minute: The format for displaying the minute.
        second: The format for displaying the second.
        time_zone_name: The format for displaying the time.
        time_zone: The time zone to express the time in.
        hour_format: The format for displaying the hour.
        **attributes: Additional HTML attributes
    """
    def __init__(
        self,
        *children: ChildrenType,
        date: str | bool | None = ...,
        weekday: Literal["narrow", "short", "long"] | None = ...,
        era: Literal["narrow", "short", "long"] | None = ...,
        year: Literal["numeric", "2-digit"] | None = ...,
        month: Literal["numeric", "2-digit", "narrow", "short", "long"] | None = ...,
        day: Literal["numeric", "2-digit"] | None = ...,
        hour: Literal["numeric", "2-digit"] | None = ...,
        minute: Literal["numeric", "2-digit"] | None = ...,
        second: Literal["numeric", "2-digit"] | None = ...,
        time_zone_name: Literal["short", "long"] | None = ...,
        time_zone: str | None = ...,
        hour_format: Literal["auto", "12", "24"] | None = ...,
        **attributes: AttributeType,
    ) -> None: ...

    def _get_tag_name(self) -> str: ...