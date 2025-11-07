"""
wa-progress-bar component.
"""

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
        value: int | float | None = None,
        indeterminate: bool | None = None,
        label: str | None = None,
        **attributes: AttributeType,
    ) -> None:
        # Build attributes dict, filtering out None values
        attributes = attributes.copy()
        attributes.update({
            'value': value,
            'indeterminate': indeterminate,
            'label': label,
        })
        # Filter out None values and False booleans, convert numbers to strings
        attributes = {
            k: str(v) if isinstance(v, (int, float)) and not isinstance(v, bool) else v
            for k, v in attributes.items()
            if v is not None and v is not False
        }
        super().__init__(*children, **attributes)

    def _get_tag_name(self) -> str:
        return "wa-progress-bar"


__all__ = [
    "progress_bar",
]