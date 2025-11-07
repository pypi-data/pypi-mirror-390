"""Type stub for wa-tab-group component."""

from typing import Literal
from pyhtml import Tag
from pyhtml.__types import ChildrenType, AttributeType


class tab_group(Tag):
    """
    wa-tab-group web component.

    Args:
        *children: Child elements and text content
        active: Sets the active tab.
        placement: The placement of the tabs.
        activation: When set to auto, navigating tabs with the arrow keys will instantly show the corresponding tab panel. When set to
            manual, the tab will receive focus but will not show until the user presses spacebar or enter.
        without_scroll_controls: Disables the scroll arrows that appear when tabs overflow.
        **attributes: Additional HTML attributes

    Slots:
        : Used for grouping tab panels in the tab group. Must be `<wa-tab-panel>` elements.
        nav: Used for grouping tabs in the tab group. Must be `<wa-tab>` elements. Note that `<wa-tab>` will set this slot on itself automatically.
    """
    def __init__(
        self,
        *children: ChildrenType,
        active: str | None = ...,
        placement: Literal["top", "bottom", "start", "end"] | None = ...,
        activation: Literal["auto", "manual"] | None = ...,
        without_scroll_controls: bool | None = ...,
        **attributes: AttributeType,
    ) -> None: ...

    def _get_tag_name(self) -> str: ...