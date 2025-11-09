from collections.abc import Callable
from dataclasses import KW_ONLY, dataclass, field
from datetime import datetime
from functools import cached_property
from typing import Any, Self, override

from nextrpg.config.config import config
from nextrpg.config.save_config import SaveConfig
from nextrpg.core.dataclass_with_default import private_init_below
from nextrpg.core.module_and_attribute import ModuleAndAttribute
from nextrpg.core.save import HasSaveData, LoadSavable
from nextrpg.scene.scene import Scene


class SceneWithCreationFunction[Context](HasSaveData, Scene):
    creation_function: ModuleAndAttribute[Callable[[Context], Self]]


@dataclass(frozen=True)
class GameSaveMeta(LoadSavable):
    config: SaveConfig = field(default_factory=lambda: config().save)
    _: KW_ONLY = private_init_below()
    save_time: datetime = field(default_factory=datetime.now)

    @override
    @classmethod
    def save_key(cls) -> str:
        return GameSave.save_key()

    @cached_property
    def save_time_str(self) -> str:
        return self.save_time.strftime(self.config.time_format)

    @override
    @cached_property
    def save_data(self) -> dict[str, Any]:
        return {"save_time": self.save_time_str}

    @classmethod
    def load_from_save(cls, data: dict[str, Any]) -> Self:
        save_time_format = config().save.time_format
        save_time = datetime.strptime(
            data["meta"]["save_time"], save_time_format
        )
        return cls(save_time=save_time)


@dataclass(frozen=True)
class GameSave[Context](LoadSavable):
    context_creation: ModuleAndAttribute[Callable[[], Context]]
    scene: SceneWithCreationFunction[Context]
    _: KW_ONLY = private_init_below()
    meta: GameSaveMeta = field(default_factory=GameSaveMeta)

    @override
    @cached_property
    def save_data(self) -> dict[str, Any]:
        scene_creation = self.scene.creation_function
        return {
            "scene": self.scene.save_data,
            "context_creation": self.context_creation.save_data,
            "scene_creation": scene_creation.save_data,
        } | {"meta": self.meta.save_data}

    @override
    @classmethod
    def load_from_save(cls, data: dict[str, Any]) -> Self:
        scene_creation = ModuleAndAttribute.load_from_save(
            data["scene_creation"]
        )
        context_creation = ModuleAndAttribute.load_from_save(
            data["context_creation"]
        )

        context = context_creation.imported()
        scene = scene_creation.imported(context)
        saved_scene = scene.update_from_save(data["scene"])
        meta = GameSaveMeta.load_from_save(data)
        return cls(
            context_creation=context_creation, scene=saved_scene, meta=meta
        )
