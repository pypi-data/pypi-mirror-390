"""Type stub for wa-include component."""

from typing import Literal
from pyhtml import Tag
from pyhtml.__types import ChildrenType, AttributeType


class include(Tag):
    """
    wa-include web component.

    Args:
        *children: Child elements and text content
        src: The location of the HTML file to include. Be sure you trust the content you are including as it will be executed as
            code and can result in XSS attacks.
        mode: The fetch mode to use.
        allow_scripts: Allows included scripts to be executed. Be sure you trust the content you are including as it will be executed as
            code and can result in XSS attacks.
        **attributes: Additional HTML attributes
    """
    def __init__(
        self,
        *children: ChildrenType,
        src: str | None = ...,
        mode: Literal["cors", "no-cors", "same-origin"] | None = ...,
        allow_scripts: bool | None = ...,
        **attributes: AttributeType,
    ) -> None: ...

    def _get_tag_name(self) -> str: ...