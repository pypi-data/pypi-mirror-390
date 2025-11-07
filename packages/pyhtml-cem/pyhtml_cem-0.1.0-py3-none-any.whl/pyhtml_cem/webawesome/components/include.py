"""
wa-include component.
"""

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
        src: str | None = None,
        mode: Literal["cors", "no-cors", "same-origin"] | None = None,
        allow_scripts: bool | None = None,
        **attributes: AttributeType,
    ) -> None:
        # Build attributes dict, filtering out None values
        attributes = attributes.copy()
        attributes.update({
            'src': src,
            'mode': mode,
            'allow_scripts': allow_scripts,
        })
        # Filter out None values and False booleans, convert numbers to strings
        attributes = {
            k: str(v) if isinstance(v, (int, float)) and not isinstance(v, bool) else v
            for k, v in attributes.items()
            if v is not None and v is not False
        }
        super().__init__(*children, **attributes)

    def _get_tag_name(self) -> str:
        return "wa-include"


__all__ = [
    "include",
]