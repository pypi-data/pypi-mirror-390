from collections.abc import Callable
from dataclasses import dataclass, field
from functools import cached_property
from typing import override

from nextrpg.config.config import config
from nextrpg.core.time import Millisecond
from nextrpg.drawing.animation_on_screen_like import AnimationOnScreenLike
from nextrpg.drawing.drawing_on_screen import DrawingOnScreen
from nextrpg.gui.screen_area import screen_area
from nextrpg.scene.scene import Scene


@dataclass(frozen=True)
class StaticScene(Scene):
    drawing_on_screen: (
        AnimationOnScreenLike | Callable[[], AnimationOnScreenLike]
    ) = field(
        default_factory=lambda: screen_area().fill(config().window.background)
    )

    @override
    @cached_property
    def drawing_on_screens(self) -> tuple[DrawingOnScreen, ...]:
        if callable(self.drawing_on_screen):
            return self.drawing_on_screen().drawing_on_screens
        return self.drawing_on_screen.drawing_on_screens

    @override
    def tick(self, time_delta: Millisecond) -> Scene:
        return self
