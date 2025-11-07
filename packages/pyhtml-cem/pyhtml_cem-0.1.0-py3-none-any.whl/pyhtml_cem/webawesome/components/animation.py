"""
wa-animation component.
"""

from typing import Literal
from pyhtml import Tag
from pyhtml.__types import ChildrenType, AttributeType


class animation(Tag):
    """
    wa-animation web component.

    Args:
        *children: Child elements and text content
        name: The name of the built-in animation to use. For custom animations, use the `keyframes` prop.
        play: Plays the animation. When omitted, the animation will be paused. This attribute will be automatically removed when
            the animation finishes or gets canceled.
        delay: The number of milliseconds to delay the start of the animation.
        direction: Determines the direction of playback as well as the behavior when reaching the end of an iteration.
            [Learn more](https://developer.mozilla.org/en-US/docs/Web/CSS/animation-direction)
        duration: The number of milliseconds each iteration of the animation takes to complete.
        easing: The easing function to use for the animation. This can be a Web Awesome easing function or a custom easing function
            such as `cubic-bezier(0, 1, .76, 1.14)`.
        end_delay: The number of milliseconds to delay after the active period of an animation sequence.
        fill: Sets how the animation applies styles to its target before and after its execution.
        iterations: The number of iterations to run before the animation completes. Defaults to `Infinity`, which loops.
        iteration_start: The offset at which to start the animation, usually between 0 (start) and 1 (end).
        playback_rate: Sets the animation's playback rate. The default is `1`, which plays the animation at a normal speed. Setting this
            to `2`, for example, will double the animation's speed. A negative value can be used to reverse the animation. This
            value can be changed without causing the animation to restart.
        **attributes: Additional HTML attributes

    Slots:
        : The element to animate. Avoid slotting in more than one element, as subsequent ones will be ignored. To animate multiple elements, either wrap them in a single container or use multiple `<wa-animation>` elements.
    """
    def __init__(
        self,
        *children: ChildrenType,
        name: str | None = None,
        play: bool | None = None,
        delay: int | float | None = None,
        direction: str | bool | None = None,
        duration: int | float | None = None,
        easing: str | None = None,
        end_delay: int | float | None = None,
        fill: str | bool | None = None,
        iterations: int | float | None = None,
        iteration_start: int | float | None = None,
        playback_rate: int | float | None = None,
        **attributes: AttributeType,
    ) -> None:
        # Build attributes dict, filtering out None values
        attributes = attributes.copy()
        attributes.update({
            'name': name,
            'play': play,
            'delay': delay,
            'direction': direction,
            'duration': duration,
            'easing': easing,
            'end_delay': end_delay,
            'fill': fill,
            'iterations': iterations,
            'iteration_start': iteration_start,
            'playback_rate': playback_rate,
        })
        # Filter out None values and False booleans, convert numbers to strings
        attributes = {
            k: str(v) if isinstance(v, (int, float)) and not isinstance(v, bool) else v
            for k, v in attributes.items()
            if v is not None and v is not False
        }
        super().__init__(*children, **attributes)

    def _get_tag_name(self) -> str:
        return "wa-animation"


__all__ = [
    "animation",
]