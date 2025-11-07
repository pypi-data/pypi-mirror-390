"""
wa-avatar component.
"""

from typing import Literal
from pyhtml import Tag
from pyhtml.__types import ChildrenType, AttributeType


class avatar(Tag):
    """
    wa-avatar web component.

    Args:
        *children: Child elements and text content
        image: The image source to use for the avatar.
        label: A label to use to describe the avatar to assistive devices.
        initials: Initials to use as a fallback when no image is available (1-2 characters max recommended).
        loading: Indicates how the browser should load the image.
        shape: The shape of the avatar.
        **attributes: Additional HTML attributes

    Slots:
        icon: The default icon to use when no image or initials are present. Works best with `<wa-icon>`.
    """
    def __init__(
        self,
        *children: ChildrenType,
        image: str | None = None,
        label: str | None = None,
        initials: str | None = None,
        loading: Literal["eager", "lazy"] | None = None,
        shape: Literal["circle", "square", "rounded"] | None = None,
        **attributes: AttributeType,
    ) -> None:
        # Build attributes dict, filtering out None values
        attributes = attributes.copy()
        attributes.update({
            'image': image,
            'label': label,
            'initials': initials,
            'loading': loading,
            'shape': shape,
        })
        # Filter out None values and False booleans, convert numbers to strings
        attributes = {
            k: str(v) if isinstance(v, (int, float)) and not isinstance(v, bool) else v
            for k, v in attributes.items()
            if v is not None and v is not False
        }
        super().__init__(*children, **attributes)

    def _get_tag_name(self) -> str:
        return "wa-avatar"


__all__ = [
    "avatar",
]