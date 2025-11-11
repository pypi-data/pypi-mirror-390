from __future__ import annotations

import logging


def _validate_status_list(status_list: dict[str, int | str]):
    try:
        logger = logging.getLogger("root")
        old_level = logger.getEffectiveLevel()
        for status in status_list.values():
            if not isinstance(status, (int, str)):
                return f"Invalid status: {status}. Must be int or str!"
            if isinstance(status, str):
                logger.setLevel(status)
            if isinstance(status, int):
                if status not in [0, 10, 20, 30, 40, 50]:
                    return f"Invalid logging level: {status}. Must be in [0, 10, 20, 30, 40, 50]!"
        logger.setLevel(old_level)
    except Exception as e:
        logger.setLevel(old_level)
        return str(e)
