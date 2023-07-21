from __future__ import annotations

from enum import Enum


class BookingStatus(str, Enum):
    CANCELLED = "CANCELLED"
    FINISHED = "FINISHED"
    WAITING = "WAITING"
    ON = "ON"
