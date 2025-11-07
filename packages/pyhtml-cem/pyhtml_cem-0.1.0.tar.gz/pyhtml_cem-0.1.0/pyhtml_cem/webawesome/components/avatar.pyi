"""Type stub for wa-avatar component."""

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
        image: str | None = ...,
        label: str | None = ...,
        initials: str | None = ...,
        loading: Literal["eager", "lazy"] | None = ...,
        shape: Literal["circle", "square", "rounded"] | None = ...,
        **attributes: AttributeType,
    ) -> None: ...

    def _get_tag_name(self) -> str: ...