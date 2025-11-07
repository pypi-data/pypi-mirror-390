"""Type stub for wa-mutation-observer component."""

from typing import Literal
from pyhtml import Tag
from pyhtml.__types import ChildrenType, AttributeType


class mutation_observer(Tag):
    """
    wa-mutation-observer web component.

    Args:
        *children: Child elements and text content
        attr: Watches for changes to attributes. To watch only specific attributes, separate them by a space, e.g.
            `attr="class id title"`. To watch all attributes, use `*`.
        attr_old_value: Indicates whether or not the attribute's previous value should be recorded when monitoring changes.
        char_data: Watches for changes to the character data contained within the node.
        char_data_old_value: Indicates whether or not the previous value of the node's text should be recorded.
        child_list: Watches for the addition or removal of new child nodes.
        disabled: Disables the observer.
        **attributes: Additional HTML attributes

    Slots:
        : The content to watch for mutations.
    """
    def __init__(
        self,
        *children: ChildrenType,
        attr: str | None = ...,
        attr_old_value: bool | None = ...,
        char_data: bool | None = ...,
        char_data_old_value: bool | None = ...,
        child_list: bool | None = ...,
        disabled: bool | None = ...,
        **attributes: AttributeType,
    ) -> None: ...

    def _get_tag_name(self) -> str: ...