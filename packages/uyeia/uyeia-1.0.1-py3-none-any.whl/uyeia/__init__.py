from __future__ import annotations

import atexit
import io
import json
import logging
import os
import re
import threading
from datetime import datetime, timezone
from typing import Literal

from uyeia.cache import UyeiaCache
from uyeia.exceptions import UYEIAConfigError
from uyeia.type import CommonStatus, Config, Status

__all__ = ["Watcher", "set_global_config", "get_errors", "Vault"]

_lock = threading.RLock()
_uyeia_config: Config = Config()
__uyeia_init__ = False
__default_logger__ = logging.getLogger("__UYEIA__")
__error_mapper__: dict[str, CommonStatus] = {}


def set_global_config(config: Config):
    global _uyeia_config, __root__

    if error := config.validate():
        raise UYEIAConfigError(f"Invalid UYEIA config: {error}")

    with _lock:
        _uyeia_config = config
        __root__._init_cache()
        _init_uyeia_env()


def _load_error_definitions():
    path = _uyeia_config.error_config_location
    if os.path.isfile(path) and os.access(path, os.R_OK):
        try:
            with io.open(path, "r") as db_file:
                data = json.load(db_file)
                return data
        except json.decoder.JSONDecodeError as e:
            raise UYEIAConfigError("Invalid errors config:", e)

    with io.open(path, "w") as db_file:
        json.dump({}, db_file)
    return {}


def _init_uyeia_env():
    global __uyeia_init__, __error_mapper__, __root__

    with _lock:
        __error_mapper__ = _load_error_definitions()
        __uyeia_init__ = True


class Watcher:
    def __init__(self, name: str | None = None, logger: logging.Logger | None = None):
        self._cache: Status | None = None

        if logger:
            self.logger = logger
            self.name = self.logger.name
        elif name:
            self.logger = logging.getLogger(name)
            self.name = name
        else:
            raise ValueError("Name or logger is required for Watcher instance")

        global __root__
        if not __uyeia_init__:
            _init_uyeia_env()

        self.manager = __root__.register(self)

    def __log(self, status: str, message: str, config: Config):
        level = config.status.get(status)
        if isinstance(level, str):
            level = logging.getLevelName(level)

        if level:
            self.logger.log(level, message)
        else:
            raise ValueError(f"Invalid status: {status}. Not in UYEIA config!")

    def __is_empty_or_high(self, status: CommonStatus) -> bool:
        levels = list(_uyeia_config.status.keys())
        return not self._cache or levels.index(status["status"]) > levels.index(
            self._cache["status"]
        )

    def get_actual_status(self):
        return self._cache

    def __replace_vars(self, message, args):
        var = re.search(r"{{(.*?)}}", message)
        if not var:
            return message
        var_name = var.groups()[0]
        value = args.get(var_name, "")
        return self.__replace_vars(
            message[: var.start()] + str(value) + message[var.end() :], args
        )

    def register(self, error_code: str, custom_message=None, vars: dict[str, str] = {}):
        error = __error_mapper__.get(error_code)
        if not error:
            raise ValueError(
                f"Invalid error code: {error_code}. Not in UYEIA errors config!"
            )

        with _lock:
            if self.__is_empty_or_high(error):
                if self._cache and self._cache["status"] != error["status"].upper():
                    self.manager.delete_entry_cache(self.name, self._cache)

                message = custom_message or error["message"]
                if vars:
                    message = self.__replace_vars(message, vars)

                if not _uyeia_config.disable_logging:
                    self.__log(error["status"], message, _uyeia_config)
                self._cache = {
                    "status": error["status"].upper(),
                    "message": self.__add_timestamp(message),
                    "solution": error.get("solution", _uyeia_config.default_solution),
                    "escalation": 0,
                }
                self.manager.write_entry_cache(self.name, self._cache)

    def release(self):
        if not self._cache:
            return

        with _lock:
            self.manager.delete_entry_cache(self.name, self._cache)
            self._cache = None

    def __del__(self):
        if getattr(self, "manager", None):
            self.manager.unregister(self.name)

    def __add_timestamp(self, error_log: str) -> str:
        return (
            f"{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} - {error_log}"
        )


class Manager:
    def __init__(self) -> None:
        self.watcherDict: dict[str, Watcher] = {}

    def _init_cache(self):
        global _uyeia_config
        self.__cache = UyeiaCache(_uyeia_config.error_cache_location)

    def getWatcher(self, name: str | None = None, logger: logging.Logger | None = None):
        if name and logger:
            raise ValueError(
                "Name or logger is required for Watcher instance! Not both."
            )

        rv = None
        name = name or getattr(logger, "name", None)
        if not name:
            raise ValueError("Name or logger is required for Watcher instance")

        with _lock:
            if name in self.watcherDict:
                rv = self.watcherDict[name]
            else:
                rv = Watcher(name, logger)
        return rv

    def __find_data_watcher(self, watcher_name: str):
        with _lock:
            return self.__cache.get("watcher", watcher_name)

    def delete_entry_cache(self, name: str, old_status: Status):
        with _lock:
            self.__cache.remove(name, old_status)

    def write_entry_cache(self, name: str, status: Status):
        with _lock:
            self.__cache.set(name, status)

    def get_cache(self):
        return self.__cache

    def set_cache(self, new_cache):
        with _lock:
            self.__cache = new_cache
            for watcher in self.watcherDict.values():
                watcher._cache = self.__find_data_watcher(watcher.name)

    def clear_cache(self):
        with _lock:
            for watcher in self.watcherDict.values():
                watcher.release()

    def close_cache(self):
        with _lock:
            if getattr(self, "_Manager__cache", None):
                self.__cache.close()

    def register(self, watcher: Watcher):
        with _lock:
            self.watcherDict[watcher.name] = watcher
            watcher._cache = self.__find_data_watcher(watcher.name)
            return self

    def unregister(self, name: str):
        with _lock:
            self.watcherDict.pop(name, None)


__root__ = Manager()


class Vault:
    def __init__(self):
        self.__vault = __root__.get_cache()

    def set(self, key: str, value: str):
        if not self.__vault:
            return
        self.__vault.set_vault(key, value)

    def get(self, key: str) -> str | None:
        if not self.__vault:
            return None
        return self.__vault.retrieve_vault(key)

    def remove(self, key: str):
        if not self.__vault:
            return
        self.__vault.remove_vault(key)


def get_errors(mode: Literal["all", "hot", "cold"] = "all"):
    cache = __root__.get_cache()
    if not cache:
        return None

    if mode == "all":
        return cache.get_all()

    if mode not in {"hot", "cold"}:
        raise ValueError(f"Invalid mode: {mode}. Must be 'all', 'hot' or 'cold'!")

    for status in (
        _uyeia_config.status.keys()
        if mode == "cold"
        else reversed(_uyeia_config.status.keys())
    ):
        if cache.exists("status", status):
            return cache.get("status", status)

    return None


def escalate():
    if _uyeia_config.disable_escalation:
        __default_logger__.warning("Escalate function is disabled in config.")
        return

    cache = __root__.get_cache()
    with _lock:
        high_status = _uyeia_config.escalation_status or next(
            reversed(_uyeia_config.status)
        )
        first_status = next(iter(_uyeia_config.status))

        cache.escalate([high_status, first_status])
        cache.update_after_escalate(_uyeia_config.max_escalation, high_status)


atexit.register(__root__.close_cache)
