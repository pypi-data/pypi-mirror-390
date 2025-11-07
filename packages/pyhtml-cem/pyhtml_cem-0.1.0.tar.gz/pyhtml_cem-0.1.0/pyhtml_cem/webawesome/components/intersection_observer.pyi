"""Type stub for wa-intersection-observer component."""

from typing import Literal
from pyhtml import Tag
from pyhtml.__types import ChildrenType, AttributeType


class intersection_observer(Tag):
    """
    wa-intersection-observer web component.

    Args:
        *children: Child elements and text content
        root: Element ID to define the viewport boundaries for tracked targets.
        root_margin: Offset space around the root boundary. Accepts values like CSS margin syntax.
        threshold: One or more space-separated values representing visibility percentages that trigger the observer callback.
        intersect_class: CSS class applied to elements during intersection. Automatically removed when elements leave
            the viewport, enabling pure CSS styling based on visibility state.
        once: If enabled, observation ceases after initial intersection.
        disabled: Deactivates the intersection observer functionality.
        **attributes: Additional HTML attributes

    Slots:
        : Elements to track. Only immediate children of the host are monitored.
    """
    def __init__(
        self,
        *children: ChildrenType,
        root: str | bool | None = ...,
        root_margin: str | None = ...,
        threshold: str | None = ...,
        intersect_class: str | None = ...,
        once: bool | None = ...,
        disabled: bool | None = ...,
        **attributes: AttributeType,
    ) -> None: ...

    def _get_tag_name(self) -> str: ...