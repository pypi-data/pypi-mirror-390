"""Type stub for wa-button component."""

from typing import Literal
from pyhtml import Tag
from pyhtml.__types import ChildrenType, AttributeType


class button(Tag):
    """
    wa-button web component.

    Args:
        *children: Child elements and text content
        title: Type: string
        variant: The button's theme variant. Defaults to `neutral` if not within another element with a variant.
        appearance: The button's visual appearance.
        size: The button's size.
        with_caret: Draws the button with a caret. Used to indicate that the button triggers a dropdown menu or similar behavior.
        disabled: Disables the button. Does not apply to link buttons.
        loading: Draws the button in a loading state.
        pill: Draws a pill-style button with rounded edges.
        type: The type of button. Note that the default value is `button` instead of `submit`, which is opposite of how native
            `<button>` elements behave. When the type is `submit`, the button will submit the surrounding form.
        name: The name of the button, submitted as a name/value pair with form data, but only when this button is the submitter.
            This attribute is ignored when `href` is present.
        value: The value of the button, submitted as a pair with the button's name as part of the form data, but only when this
            button is the submitter. This attribute is ignored when `href` is present.
        href: When set, the underlying button will be rendered as an `<a>` with this `href` instead of a `<button>`.
        target: Tells the browser where to open the link. Only used when `href` is present.
        rel: When using `href`, this attribute will map to the underlying link's `rel` attribute.
        download: Tells the browser to download the linked file as this filename. Only used when `href` is present.
        form: The "form owner" to associate the button with. If omitted, the closest containing form will be used instead. The
            value of this attribute must be an id of a form in the same document or shadow root as the button.
        formaction: Used to override the form owner's `action` attribute.
        formenctype: Used to override the form owner's `enctype` attribute.
        formmethod: Used to override the form owner's `method` attribute.
        formnovalidate: Used to override the form owner's `novalidate` attribute.
        formtarget: Used to override the form owner's `target` attribute.
        **attributes: Additional HTML attributes

    Slots:
        : The button's label.
        start: An element, such as `<wa-icon>`, placed before the label.
        end: An element, such as `<wa-icon>`, placed after the label.
    """
    def __init__(
        self,
        *children: ChildrenType,
        title: str | None = ...,
        variant: Literal["neutral", "brand", "success", "warning", "danger"] | None = ...,
        appearance: Literal["accent", "filled", "outlined", "filled-outlined", "plain"] | None = ...,
        size: Literal["small", "medium", "large"] | None = ...,
        with_caret: bool | None = ...,
        disabled: bool | None = ...,
        loading: bool | None = ...,
        pill: bool | None = ...,
        type: Literal["button", "submit", "reset"] | None = ...,
        name: str | None = ...,
        value: str | None = ...,
        href: str | None = ...,
        target: Literal["_blank", "_parent", "_self", "_top"] | None = ...,
        rel: str | bool | None = ...,
        download: str | bool | None = ...,
        form: str | bool | None = ...,
        formaction: str | None = ...,
        formenctype: Literal["application/x-www-form-urlencoded", "multipart/form-data", "text/plain"] | None = ...,
        formmethod: Literal["post", "get"] | None = ...,
        formnovalidate: bool | None = ...,
        formtarget: Literal["_self", "_blank", "_parent", "_top"] | None = ...,
        **attributes: AttributeType,
    ) -> None: ...

    def _get_tag_name(self) -> str: ...