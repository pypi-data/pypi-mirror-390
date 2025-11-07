"""Type stub for wa-dialog component."""

from typing import Literal
from pyhtml import Tag
from pyhtml.__types import ChildrenType, AttributeType


class dialog(Tag):
    """
    wa-dialog web component.

    Args:
        *children: Child elements and text content
        open: Indicates whether or not the dialog is open. Toggle this attribute to show and hide the dialog.
        label: The dialog's label as displayed in the header. You should always include a relevant label, as it is required for
            proper accessibility. If you need to display HTML, use the `label` slot instead.
        without_header: Disables the header. This will also remove the default close button.
        light_dismiss: When enabled, the dialog will be closed when the user clicks outside of it.
        **attributes: Additional HTML attributes

    Slots:
        : The dialog's main content.
        label: The dialog's label. Alternatively, you can use the `label` attribute.
        header-actions: Optional actions to add to the header. Works best with `<wa-button>`.
        footer: The dialog's footer, usually one or more buttons representing various options.
    """
    def __init__(
        self,
        *children: ChildrenType,
        open: bool | None = ...,
        label: str | None = ...,
        without_header: bool | None = ...,
        light_dismiss: bool | None = ...,
        **attributes: AttributeType,
    ) -> None: ...

    def _get_tag_name(self) -> str: ...