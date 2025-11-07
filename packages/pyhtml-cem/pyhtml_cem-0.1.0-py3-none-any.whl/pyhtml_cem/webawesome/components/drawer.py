"""
wa-drawer component.
"""

from typing import Literal
from pyhtml import Tag
from pyhtml.__types import ChildrenType, AttributeType


class drawer(Tag):
    """
    wa-drawer web component.

    Args:
        *children: Child elements and text content
        open: Indicates whether or not the drawer is open. Toggle this attribute to show and hide the drawer.
        label: The drawer's label as displayed in the header. You should always include a relevant label, as it is required for
            proper accessibility. If you need to display HTML, use the `label` slot instead.
        placement: The direction from which the drawer will open.
        without_header: Disables the header. This will also remove the default close button.
        light_dismiss: When enabled, the drawer will be closed when the user clicks outside of it.
        **attributes: Additional HTML attributes

    Slots:
        : The drawer's main content.
        label: The drawer's label. Alternatively, you can use the `label` attribute.
        header-actions: Optional actions to add to the header. Works best with `<wa-button>`.
        footer: The drawer's footer, usually one or more buttons representing various options.
    """
    def __init__(
        self,
        *children: ChildrenType,
        open: bool | None = None,
        label: str | None = None,
        placement: Literal["top", "end", "bottom", "start"] | None = None,
        without_header: bool | None = None,
        light_dismiss: bool | None = None,
        **attributes: AttributeType,
    ) -> None:
        # Build attributes dict, filtering out None values
        attributes = attributes.copy()
        attributes.update({
            'open': open,
            'label': label,
            'placement': placement,
            'without_header': without_header,
            'light_dismiss': light_dismiss,
        })
        # Filter out None values and False booleans, convert numbers to strings
        attributes = {
            k: str(v) if isinstance(v, (int, float)) and not isinstance(v, bool) else v
            for k, v in attributes.items()
            if v is not None and v is not False
        }
        super().__init__(*children, **attributes)

    def _get_tag_name(self) -> str:
        return "wa-drawer"


__all__ = [
    "drawer",
]