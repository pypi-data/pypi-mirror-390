"""Type stub for wa-button-group component."""

from typing import Literal
from pyhtml import Tag
from pyhtml.__types import ChildrenType, AttributeType


class button_group(Tag):
    """
    wa-button-group web component.

    Args:
        *children: Child elements and text content
        label: A label to use for the button group. This won't be displayed on the screen, but it will be announced by assistive
            devices when interacting with the control and is strongly recommended.
        orientation: The button group's orientation.
        variant: The button group's theme variant. Defaults to `neutral` if not within another element with a variant.
        **attributes: Additional HTML attributes

    Slots:
        : One or more `<wa-button>` elements to display in the button group.
    """
    def __init__(
        self,
        *children: ChildrenType,
        label: str | None = ...,
        orientation: Literal["horizontal", "vertical"] | None = ...,
        variant: Literal["neutral", "brand", "success", "warning", "danger"] | None = ...,
        **attributes: AttributeType,
    ) -> None: ...

    def _get_tag_name(self) -> str: ...