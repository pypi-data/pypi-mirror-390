"""Type stub for wa-relative-time component."""

from typing import Literal
from pyhtml import Tag
from pyhtml.__types import ChildrenType, AttributeType


class relative_time(Tag):
    """
    wa-relative-time web component.

    Args:
        *children: Child elements and text content
        date: The date from which to calculate time from. If not set, the current date and time will be used. When passing a
            string, it's strongly recommended to use the ISO 8601 format to ensure timezones are handled correctly. To convert
            a date to this format in JavaScript, use [`date.toISOString()`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Date/toISOString).
        format: The formatting style to use.
        numeric: When `auto`, values such as "yesterday" and "tomorrow" will be shown when possible. When `always`, values such as
            "1 day ago" and "in 1 day" will be shown.
        sync: Keep the displayed value up to date as time passes.
        **attributes: Additional HTML attributes
    """
    def __init__(
        self,
        *children: ChildrenType,
        date: str | bool | None = ...,
        format: Literal["long", "short", "narrow"] | None = ...,
        numeric: Literal["always", "auto"] | None = ...,
        sync: bool | None = ...,
        **attributes: AttributeType,
    ) -> None: ...

    def _get_tag_name(self) -> str: ...