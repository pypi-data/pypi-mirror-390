import json
import sys
from collections.abc import Callable
from concurrent.futures import Future, ThreadPoolExecutor
from dataclasses import KW_ONLY, dataclass, field
from enum import Enum
from functools import cache, cached_property
from pathlib import Path
from shutil import rmtree
from typing import TYPE_CHECKING, Self, override

from nextrpg import __version__
from nextrpg.config.save_config import SaveConfig
from nextrpg.core.dataclass_with_default import (
    dataclass_with_default,
    default,
    private_init_below,
)

if TYPE_CHECKING:
    from nextrpg.core.log import Log


@dataclass(frozen=True)
class AliasAndBytes:
    alias: str
    bytes: bytes


type Primitive = str | int | float | bool | None
type Json = Primitive | tuple["Json", ...] | list["Json"] | dict[str, "Json"]
type SaveData = Primitive | AliasAndBytes | tuple["SaveData", ...] | list[
    "SaveData"
] | dict[str, "SaveData"]


class HasSaveData[_S: SaveData]:
    @property
    def save_data(self) -> _S: ...


class LoadFromSave[_S: SaveData](HasSaveData[_S]):
    @classmethod
    def load_from_save(cls, data: _S) -> Self: ...


class UpdateFromSave[_S: SaveData](HasSaveData[_S]):
    def update_from_save(self, data: _S) -> Self | None: ...


class LoadFromSaveEnum(LoadFromSave, Enum):
    @override
    @cached_property
    def save_data(self) -> str:
        return self.name

    @override
    @classmethod
    def load_from_save(cls, data: str) -> Self:
        return cls[data]


class UpdateSavable[_S: SaveData](UpdateFromSave[_S]):
    def save_key(self) -> str:
        return type(self).__qualname__


class LoadSavable[_S: SaveData](LoadFromSave[_S]):
    @classmethod
    def save_key(cls) -> str:
        return cls.__qualname__


@cache
def _config() -> SaveConfig:
    from nextrpg.config.config import config

    return config().save


@cache
def _log() -> Log:
    from nextrpg.core.log import Log

    return Log()


@dataclass_with_default(frozen=True)
class SaveIo:
    slot: str = default(lambda self: self.config.shared_slot)
    config: SaveConfig = field(default_factory=_config)
    _: KW_ONLY = private_init_below()
    _log: Log = field(default_factory=_log)
    _thread: ThreadPoolExecutor = ThreadPoolExecutor(max_workers=1)

    def save(self, savable: UpdateSavable | LoadSavable) -> Future:
        key = savable.save_key()
        self._log.debug(t"Saving {key} at {self.slot}")
        future = self._thread.submit(self._save, savable)
        future.add_done_callback(lambda fut: self._on_save_complete(key, fut))
        return future

    def remove(self) -> None:
        rmtree(self.config.directory / self.slot, ignore_errors=True)

    def update[_U: UpdateSavable](self, update_from_save: _U) -> _U:
        key = update_from_save.save_key()
        return (
            self._load(key, update_from_save.update_from_save)
            or update_from_save
        )

    def load[_L: LoadSavable](self, load_from_save: type[_L]) -> _L | None:
        key = load_from_save.save_key()
        return self._load(key, load_from_save.load_from_save)

    @cached_property
    def web(self) -> bool:
        # TODO: Implement web save/load using IndexedDB.
        return sys.platform == "emscripten"

    def _on_save_complete(self, key, future: Future) -> None:
        if exp := future.exception():
            self._log.error(t"Failed to save {key} at {self.slot}. {exp}")
            return
        self._log.debug(t"Saved {key} at {self.slot}")

    def _save(self, savable: UpdateSavable | LoadSavable) -> None:
        key = savable.save_key()
        data = self._serialize(key, savable.save_data)
        blob = self._read_text()
        blob[key] = data
        json_blob = json.dumps(blob)
        self._text_path.parent.mkdir(parents=True, exist_ok=True)
        self._text_path.write_text(json_blob)
        self._read_text.cache_clear()

    def _load[_U: UpdateSavable, _L: LoadSavable](
        self, key: str, loader: Callable[[SaveData], _L | _U | None]
    ) -> _U | _L | None:
        self._log.debug(t"Loading {key} at {self.slot}")
        if json_like := self._read_text().get(key):
            data = self._deserialize(key, json_like)
            return loader(data)
        return None

    def _write_bytes(self, key: str, alias_and_bytes: AliasAndBytes) -> None:
        file = self._key_and_alias(key, alias_and_bytes.alias)
        path = self._bytes_path(file)
        path.write_bytes(alias_and_bytes.bytes)

    def _deserialize(self, key: str, data: Json) -> SaveData:
        if isinstance(data, list):
            return [self._deserialize(key, datum) for datum in data]
        if isinstance(data, dict):
            return {
                key: self._deserialize(key, value)
                for key, value in data.items()
            }
        if (
            isinstance(data, str)
            and (
                path := self._bytes_path(self._key_and_alias(key, data))
            ).exists()
        ):
            alias = data.split(self.config.key_delimiter, maxsplit=1)[1]
            read_bytes = path.read_bytes()
            return AliasAndBytes(alias, read_bytes)
        return data

    @cache
    def _read_text(self) -> dict[str, Json]:
        if (file := self._text_path).exists():
            text = file.read_text()
            return json.loads(text)
        return {"version": __version__}

    def _serialize(self, key: str, data: SaveData) -> Json:
        if isinstance(data, AliasAndBytes):
            self._write_bytes(key, data)
            return self._key_and_alias(key, data)
        if isinstance(data, tuple | list):
            return [self._serialize(key, datum) for datum in data]
        if isinstance(data, dict):
            return {
                key: self._serialize(key, value) for key, value in data.items()
            }
        return data

    def _bytes_path(self, file: str) -> Path:
        return self.config.directory / self.slot / file

    @cached_property
    def _text_path(self) -> Path:
        return self.config.directory / self.slot / self.config.text_file

    def _key_and_alias(self, key: str, alias: str) -> str:
        return self.config.key_delimiter.join((key, alias))
