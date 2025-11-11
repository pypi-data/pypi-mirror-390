from __future__ import annotations

import os
from copy import deepcopy
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, TypedDict

from uyeia.serializers import _validate_status_list

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))


class DefaultStatusEnum(str, Enum):
    HEALTHY = "HEALTHY"
    RESCUE = "RESCUE"
    PENDING = "PENDING"
    LIMITED = "LIMITED"
    WARNING = "WARNING"


class CommonStatus(TypedDict):
    status: str
    message: str
    solution: str | None


class Status(CommonStatus):
    escalation: int


@dataclass
class Config:
    status: dict[str, int | str] = field(
        default_factory=lambda: {
            "HEALTHY": 20,
            "PENDING": 20,
            "LIMITED": 30,
            "WARNING": 40,
            "RESCUE": 50,
        }
    )
    escalation_status: str = DefaultStatusEnum.RESCUE.value
    default_healthy: Optional[str] = DefaultStatusEnum.HEALTHY.value
    default_solution: Optional[str] = "Contact your IT admin."
    disable_escalation: bool = False
    max_escalation: int = 5
    disable_logging: bool = False
    error_config_location: str = field(
        default=os.path.join(ROOT_DIR, "uyeia.errors.json")
    )
    error_cache_location: str = os.path.join(ROOT_DIR, "errors_cache.db")

    def __post_init__(self):
        self.escalation_status = self.escalation_status.upper()
        if self.default_healthy:
            self.default_healthy = self.default_healthy.upper()

        old_dict = deepcopy(self.status)
        self.status.clear()
        for status in old_dict:
            self.status[status.upper()] = old_dict[status]

    def validate(self):
        if status_list := _validate_status_list(self.status):
            return status_list
