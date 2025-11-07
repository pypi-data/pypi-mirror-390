"""
wa-popup component.
"""

from typing import Literal
from pyhtml import Tag
from pyhtml.__types import ChildrenType, AttributeType


class popup(Tag):
    """
    wa-popup web component.

    Args:
        *children: Child elements and text content
        anchor: The element the popup will be anchored to. If the anchor lives outside of the popup, you can provide the anchor
            element `id`, a DOM element reference, or a `VirtualElement`. If the anchor lives inside the popup, use the
            `anchor` slot instead.
        active: Activates the positioning logic and shows the popup. When this attribute is removed, the positioning logic is torn
            down and the popup will be hidden.
        placement: The preferred placement of the popup. Note that the actual placement will vary as configured to keep the
            panel inside of the viewport.
        boundary: The bounding box to use for flipping, shifting, and auto-sizing.
        distance: The distance in pixels from which to offset the panel away from its anchor.
        skidding: The distance in pixels from which to offset the panel along its anchor.
        arrow: Attaches an arrow to the popup. The arrow's size and color can be customized using the `--arrow-size` and
            `--arrow-color` custom properties. For additional customizations, you can also target the arrow using
            `::part(arrow)` in your stylesheet.
        arrow_placement: The placement of the arrow. The default is `anchor`, which will align the arrow as close to the center of the
            anchor as possible, considering available space and `arrow-padding`. A value of `start`, `end`, or `center` will
            align the arrow to the start, end, or center of the popover instead.
        arrow_padding: The amount of padding between the arrow and the edges of the popup. If the popup has a border-radius, for example,
            this will prevent it from overflowing the corners.
        flip: When set, placement of the popup will flip to the opposite site to keep it in view. You can use
            `flipFallbackPlacements` to further configure how the fallback placement is determined.
        flip_fallback_placements: If the preferred placement doesn't fit, popup will be tested in these fallback placements until one fits. Must be a
            string of any number of placements separated by a space, e.g. "top bottom left". If no placement fits, the flip
            fallback strategy will be used instead.
        flip_fallback_strategy: When neither the preferred placement nor the fallback placements fit, this value will be used to determine whether
            the popup should be positioned using the best available fit based on available space or as it was initially
            preferred.
        flipBoundary: The flip boundary describes clipping element(s) that overflow will be checked relative to when flipping. By
            default, the boundary includes overflow ancestors that will cause the element to be clipped. If needed, you can
            change the boundary by passing a reference to one or more elements to this property.
        flip_padding: The amount of padding, in pixels, to exceed before the flip behavior will occur.
        shift: Moves the popup along the axis to keep it in view when clipped.
        shiftBoundary: The shift boundary describes clipping element(s) that overflow will be checked relative to when shifting. By
            default, the boundary includes overflow ancestors that will cause the element to be clipped. If needed, you can
            change the boundary by passing a reference to one or more elements to this property.
        shift_padding: The amount of padding, in pixels, to exceed before the shift behavior will occur.
        auto_size: When set, this will cause the popup to automatically resize itself to prevent it from overflowing.
        sync: Syncs the popup's width or height to that of the anchor element.
        autoSizeBoundary: The auto-size boundary describes clipping element(s) that overflow will be checked relative to when resizing. By
            default, the boundary includes overflow ancestors that will cause the element to be clipped. If needed, you can
            change the boundary by passing a reference to one or more elements to this property.
        auto_size_padding: The amount of padding, in pixels, to exceed before the auto-size behavior will occur.
        hover_bridge: When a gap exists between the anchor and the popup element, this option will add a "hover bridge" that fills the
            gap using an invisible element. This makes listening for events such as `mouseenter` and `mouseleave` more sane
            because the pointer never technically leaves the element. The hover bridge will only be drawn when the popover is
            active.
        **attributes: Additional HTML attributes

    Slots:
        : The popup's content.
        anchor: The element the popup will be anchored to. If the anchor lives outside of the popup, you can use the `anchor` attribute or property instead.
    """
    def __init__(
        self,
        *children: ChildrenType,
        anchor: str | bool | None = None,
        active: bool | None = None,
        placement: Literal["top", "top-start", "top-end", "bottom", "bottom-start", "bottom-end", "right", "right-start", "right-end", "left", "left-start", "left-end"] | None = None,
        boundary: Literal["viewport", "scroll"] | None = None,
        distance: int | float | None = None,
        skidding: int | float | None = None,
        arrow: bool | None = None,
        arrow_placement: Literal["start", "end", "center", "anchor"] | None = None,
        arrow_padding: int | float | None = None,
        flip: bool | None = None,
        flip_fallback_placements: str | None = None,
        flip_fallback_strategy: Literal["best-fit", "initial"] | None = None,
        flipBoundary: str | bool | None = None,
        flip_padding: int | float | None = None,
        shift: bool | None = None,
        shiftBoundary: str | bool | None = None,
        shift_padding: int | float | None = None,
        auto_size: Literal["horizontal", "vertical", "both"] | None = None,
        sync: Literal["width", "height", "both"] | None = None,
        autoSizeBoundary: str | bool | None = None,
        auto_size_padding: int | float | None = None,
        hover_bridge: bool | None = None,
        **attributes: AttributeType,
    ) -> None:
        # Build attributes dict, filtering out None values
        attributes = attributes.copy()
        attributes.update({
            'anchor': anchor,
            'active': active,
            'placement': placement,
            'boundary': boundary,
            'distance': distance,
            'skidding': skidding,
            'arrow': arrow,
            'arrow_placement': arrow_placement,
            'arrow_padding': arrow_padding,
            'flip': flip,
            'flip_fallback_placements': flip_fallback_placements,
            'flip_fallback_strategy': flip_fallback_strategy,
            'flipBoundary': flipBoundary,
            'flip_padding': flip_padding,
            'shift': shift,
            'shiftBoundary': shiftBoundary,
            'shift_padding': shift_padding,
            'auto_size': auto_size,
            'sync': sync,
            'autoSizeBoundary': autoSizeBoundary,
            'auto_size_padding': auto_size_padding,
            'hover_bridge': hover_bridge,
        })
        # Filter out None values and False booleans, convert numbers to strings
        attributes = {
            k: str(v) if isinstance(v, (int, float)) and not isinstance(v, bool) else v
            for k, v in attributes.items()
            if v is not None and v is not False
        }
        super().__init__(*children, **attributes)

    def _get_tag_name(self) -> str:
        return "wa-popup"


__all__ = [
    "popup",
]