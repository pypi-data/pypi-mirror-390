from dataclasses import dataclass

from nextrpg.core.time import Millisecond


@dataclass(frozen=True)
class AnimationConfig:
    transition_scene_total_duration: Millisecond = 800
    default_timed_animation_duration: Millisecond = 400
