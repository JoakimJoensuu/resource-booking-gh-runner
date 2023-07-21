import asyncio
import json
from asyncio.events import AbstractEventLoop
from copy import deepcopy
from datetime import datetime, timezone
from typing import Any, Coroutine, Dict, List, NoReturn, TypedDict

from aioconsole import aprint
from aiohttp import web
from aiohttp.web import Application
from aiohttp.web_routedef import RouteDef
from booking_server.booking import (
    Booking,
    BookingRequest,
    BookingStatus,
    DumpableBooking,
    dumpable_booking,
    dumpable_bookings,
)
from booking_server.resource import (
    DumpableResource,
    Resource,
    dumpable_resources,
)


class DumpableServerData(TypedDict):
    booking_id_counter: int
    bookings: List[DumpableBooking]
    resources: List[DumpableResource]
    id_to_booking: Dict[int, DumpableBooking]


class ServerData(TypedDict):
    booking_id_counter: int
    bookings: List[Booking]
    resources: List[Resource]
    id_to_booking: Dict[int, Booking]


async def dumpable_server_data(
    server_data: ServerData,
) -> DumpableServerData:
    bookings = server_data["bookings"]
    resources = server_data["resources"]

    return {
        "bookings": await dumpable_bookings(bookings),
        "booking_id_counter": server_data["booking_id_counter"],
        "id_to_booking": {
            id: await dumpable_booking(booking)
            for id, booking in enumerate(bookings)
        },
        "resources": await dumpable_resources(resources),
    }


async def add_new_booking(
    booking_request: BookingRequest, server_data: ServerData
):
    booking_id = server_data["booking_id_counter"]
    server_data["booking_id_counter"] += 1

    booking: Booking = {
        "info": {
            "id": booking_id,
            "name": booking_request["name"],
            "requested": booking_request["resource"],
            "booking_time": datetime.now(timezone.utc).isoformat(
                timespec="seconds"
            ),
            "status": BookingStatus.WAITING,
        },
        "used": None,
    }

    server_data["bookings"].append(booking)
    server_data["id_to_booking"][booking_id] = booking

    return booking


async def get_server_data(application: Application) -> ServerData:
    return application["server_data"]


async def periodic_cleanup(server_data: ServerData):
    # TODO: Implement
    # TODO: Could be also ran from endpoint handlers when lists get too big
    while True:
        await asyncio.sleep(1)
        await aprint(
            "========================================================"
        )
        await aprint(
            "I could clean something, but here is current server data:"
        )

        dumpable = await dumpable_server_data(deepcopy(server_data))
        await aprint(json.dumps(dumpable, indent=2))


def start_cleaner(
    loop: AbstractEventLoop,
    cleaning_routine: Coroutine[Any, Any, NoReturn],
):
    loop.create_task(cleaning_routine)


def start_server(
    routes: List[RouteDef],
    initial_server_data: ServerData,
    loop: AbstractEventLoop,
):
    app = web.Application()
    app.add_routes(routes)
    app["server_data"] = initial_server_data
    web.run_app(app, loop=loop)
