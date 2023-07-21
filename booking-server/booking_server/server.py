import asyncio
import json
from copy import deepcopy
from typing import Dict, List, TypedDict

import aioconsole
from aioconsole import aprint
from aiohttp.web import Application
from booking_server.booking import (
    Booking,
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


async def get_server_data(application: Application):
    server_data: ServerData = application["server_data"]
    return server_data


async def periodic_cleanup(server_data: ServerData):
    # TODO: Implement
    # TODO: Could be also ran from endpoint handlers when lists get too big
    while True:
        await aprint(
            "========================================================"
        )
        await aprint(
            "I could clean something, but here is current server data:"
        )

        dumpable = await dumpable_server_data(deepcopy(server_data))
        await aprint(json.dumps(dumpable, indent=2))

        await asyncio.sleep(1)
