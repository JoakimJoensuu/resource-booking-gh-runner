from __future__ import annotations

import asyncio
from enum import Enum
from http import HTTPStatus
from typing import Callable, List

from aiohttp import web
from booking_server.broker import try_assigning_to_booking
from booking_server.types import Booking


class BookingStatus(str, Enum):
    CANCELLED = "CANCELLED"
    FINISHED = "FINISHED"
    WAITING = "WAITING"
    ON = "ON"


def cancel_booking(booking: Booking, _: List[Booking]):
    if booking["info"]["status"] == BookingStatus.ON:
        return web.Response(
            status=HTTPStatus.UNPROCESSABLE_ENTITY,
            text=(
                f"Booking with id {booking['info']['id']} had already resource"
                " assigned to it. Did you mean to"
                " /booking/{booking_id}/finish the booking?"
            ),
        )

    booking["info"]["status"] = BookingStatus.CANCELLED

    return web.Response()


def finish_booking(booking: Booking, bookings: List[Booking]):
    if booking["info"]["status"] == BookingStatus.WAITING:
        return web.Response(
            status=HTTPStatus.UNPROCESSABLE_ENTITY,
            text=(
                f"Booking with id {booking['info']['id']} was still waiting"
                " for resource to be assigned to it. Did you mean to"
                " /booking/{booking_id}/cancel the booking?"
            ),
        )

    freed_resource = booking["used"]
    if freed_resource is None:
        raise RuntimeError("Booking didn't have resource even when it should.")

    freed_resource["used_by"] = None
    booking["info"]["status"] = BookingStatus.FINISHED

    asyncio.create_task(try_assigning_to_booking(freed_resource, bookings))

    return web.Response()


class BookingUpdateAction(Enum):
    def __init__(
        self,
        action_name: str,
        updater: Callable[[Booking, List[Booking]], web.Response],
    ):
        self.action_name: str = action_name

        self.updater: Callable[[Booking, List[Booking]], web.Response] = (
            updater
        )

    CANCEL = ("cancel", cancel_booking)
    FINISH = ("finish", finish_booking)
