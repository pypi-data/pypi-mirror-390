"""Type stub for wa-progress-bar component."""

from typing import Literal
from pyhtml import Tag
from pyhtml.__types import ChildrenType, AttributeType


class progress_bar(Tag):
    """
    wa-progress-bar web component.

    Args:
        *children: Child elements and text content
        value: The current progress as a percentage, 0 to 100.
        indeterminate: When true, percentage is ignored, the label is hidden, and the progress bar is drawn in an indeterminate state.
        label: A custom label for assistive devices.
        **attributes: Additional HTML attributes

    Slots:
        : A label to show inside the progress indicator.
    """
    def __init__(
        self,
        *children: ChildrenType,
        value: int | float | None = ...,
        indeterminate: bool | None = ...,
        label: str | None = ...,
        **attributes: AttributeType,
    ) -> None: ...

    def _get_tag_name(self) -> str: ...