"""
Webawesome components for PyHTML.

Auto-generated from Custom Elements Manifest - 57 components.

This module uses lazy loading: components are only imported when first accessed.
"""

__all__ = [
    "animated_image",
    "animation",
    "avatar",
    "badge",
    "breadcrumb",
    "breadcrumb_item",
    "button",
    "button_group",
    "callout",
    "card",
    "carousel",
    "carousel_item",
    "checkbox",
    "color_picker",
    "comparison",
    "copy_button",
    "details",
    "dialog",
    "divider",
    "drawer",
    "dropdown",
    "dropdown_item",
    "format_bytes",
    "format_date",
    "format_number",
    "icon",
    "include",
    "input",
    "intersection_observer",
    "mutation_observer",
    "option",
    "popover",
    "popup",
    "progress_bar",
    "progress_ring",
    "qr_code",
    "radio",
    "radio_group",
    "rating",
    "relative_time",
    "resize_observer",
    "scroller",
    "select",
    "skeleton",
    "slider",
    "spinner",
    "split_panel",
    "switch",
    "tab",
    "tab_group",
    "tab_panel",
    "tag",
    "textarea",
    "tooltip",
    "tree",
    "tree_item",
    "zoomable_frame",
]


_component_cache = {}


def __getattr__(name: str):
    """Lazy load components on demand."""
    if name in __all__:
        if name not in _component_cache:
            from . import components
            _component_cache[name] = getattr(components, name)
        return _component_cache[name]
    raise AttributeError(f"module {__name__} has no attribute {name}")