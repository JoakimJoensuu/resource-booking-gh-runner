from __future__ import annotations

import asyncio
import json
from copy import deepcopy
from datetime import datetime, timezone
from enum import Enum
from http import HTTPStatus
from typing import Callable, Dict, List, TypedDict

from aiohttp import web
from aiohttp.web import Application
from aiohttp.web_request import Request


class RequestedResource(TypedDict):
    type: str
    identifier: None | str


class BookingRequest(TypedDict):
    name: str
    resource: RequestedResource


class BookingStatus(str, Enum):
    CANCELLED = "CANCELLED"
    FINISHED = "FINISHED"
    WAITING = "WAITING"
    ON = "ON"


class Resource(TypedDict):
    info: ResourceInfo
    used_by: None | Booking


class Booking(TypedDict):
    info: BookingInfo
    used: None | Resource


class DumpableResource(TypedDict):
    info: ResourceInfo
    used_by: BookingInfo | None


class ResourceInfo(TypedDict):
    type: str
    identifier: str


class BookingInfo(TypedDict):
    name: str
    id: int
    requested: RequestedResource
    booking_time: str
    status: BookingStatus


class DumpableBooking(TypedDict):
    info: BookingInfo
    used: ResourceInfo | None


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


async def get_server_data(application: Application):
    server_data: ServerData = application["server_data"]
    return server_data


async def validate_resource(resource: Dict) -> Resource:
    # TODO: Proper error reporting mechanism
    # TODO: Generic TypedDict validation function
    return {
        "info": {
            "identifier": resource["identifier"],
            "type": resource["type"],
        },
        "used_by": None,
    }


async def validate_booking_request(booking_request: Dict) -> BookingRequest:
    # TODO: Proper error reporting mechanism
    # TODO: Generic TypedDict validation function
    return {
        "name": booking_request["name"],
        "resource": {
            "type": booking_request["resource"]["type"],
            "identifier": booking_request["resource"].get("identifier"),
        },
    }


def find_free_resource(
    resources: List[Resource],
    requested: RequestedResource,
):
    for resource in resources:
        if resource["info"]["type"] != requested["type"]:
            continue

        if (
            resource["info"]["identifier"] != requested["identifier"]
            and requested["identifier"] is not None
        ):
            continue

        if resource["used_by"] is not None:
            continue

        return resource

    return None


async def new_booking(request: Request):
    server_data = await get_server_data(request.app)
    booking_id = server_data["booking_id_counter"]
    server_data["booking_id_counter"] += 1

    booking_request = await validate_booking_request(await request.json())

    free_resource = find_free_resource(
        server_data["resources"],
        booking_request["resource"],
    )

    booking: Booking = {
        "info": {
            "id": booking_id,
            "name": booking_request["name"],
            "requested": booking_request["resource"],
            "booking_time": datetime.now(timezone.utc).isoformat(
                timespec="seconds"
            ),
            "status": (
                BookingStatus.ON if free_resource else BookingStatus.WAITING
            ),
        },
        "used": free_resource if free_resource else None,
    }

    if free_resource is not None:
        free_resource["used_by"] = booking
        booking["used"] = free_resource
        # TODO: Send notification to client

    server_data["bookings"].append(booking)
    server_data["id_to_booking"][booking_id] = booking

    return web.json_response(dumpable_booking(booking))


async def unimplemented(_: Request):
    return web.Response(
        text="This endpoint is not yet implemented.",
        status=HTTPStatus.NOT_IMPLEMENTED,
    )


async def new_resource(request: Request):
    resource = await validate_resource(await request.json())

    # TODO: Check for existing resources with same identifier
    server_data = await get_server_data(request.app)

    server_data["resources"].append(resource)

    asyncio.create_task(
        find_booking_for_resource(resource, server_data["bookings"])
    )

    return web.Response()


async def get_resources(request: Request):
    return web.json_response((await get_server_data(request.app))["resources"])


async def get_booking(request: Request):
    id = int(request.match_info["booking_id"])
    server_data = await get_server_data(request.app)

    # TODO: Proper response for non existing booking
    return web.json_response(server_data["id_to_booking"][id])


async def get_bookings(request: Request):
    return web.json_response((await get_server_data(request.app))["bookings"])


def find_resource_by_booking(resources: List[Resource], booking: Booking):
    for resource in resources:
        candidate_booking = resource["used_by"]
        if candidate_booking is None:
            continue

        if candidate_booking["info"]["id"] != booking["info"]["id"]:
            continue

        return resource

    raise RuntimeError(
        f"Didn't find resource for booking (id={booking['info']['id']}) that"
        f" had status {booking['info']['status']}"
    )


def cancel_booking(booking: Booking, _: List[Resource], _2: List[Booking]):
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


async def find_booking_for_resource(
    resource: Resource, bookings: List[Booking]
):
    for booking in bookings:
        requested = booking["info"]["requested"]
        if booking["info"]["status"] != BookingStatus.WAITING:
            continue
        if requested["type"] != resource["info"]["type"]:
            continue
        if (
            requested["identifier"] != resource["info"]["identifier"]
            and requested["identifier"] is not None
        ):
            continue

        booking["info"]["status"] = BookingStatus.ON
        booking["used"] = resource
        resource["used_by"] = booking

        return


def finish_booking(
    booking: Booking, resources: List[Resource], bookings: List[Booking]
):
    if booking["info"]["status"] == BookingStatus.WAITING:
        return web.Response(
            status=HTTPStatus.UNPROCESSABLE_ENTITY,
            text=(
                f"Booking with id {booking['info']['id']} was still waiting"
                " for resource to be assigned to it. Did you mean to"
                " /booking/{booking_id}/cancel the booking?"
            ),
        )

    booked_resource = booking["used"]
    if booked_resource is None:
        raise Exception("Booking didn't have resource even when it should.")

    booked_resource["used_by"] = None
    booking["info"]["status"] = BookingStatus.FINISHED

    asyncio.create_task(find_booking_for_resource(booked_resource, bookings))

    return web.Response()


class BookingUpdateAction(Enum):
    def __init__(
        self,
        action_name: str,
        updater: Callable[
            [Booking, List[Resource], List[Booking]], web.Response
        ],
    ):
        self.action_name: str = action_name

        self.updater: Callable[
            [Booking, List[Resource], List[Booking]], web.Response
        ] = updater

    CANCEL = ("cancel", cancel_booking)
    FINISH = ("finish", finish_booking)


async def booking_update(request: Request):
    requested_action = request.match_info["action"]

    if requested_action not in set(
        action.action_name for action in BookingUpdateAction
    ):
        return web.Response(
            status=HTTPStatus.NOT_FOUND,
            text=(
                f"Action {requested_action} not supported. Use one of the"
                " following:"
                f" {', '.join([status.action_name for status in BookingUpdateAction])}"
            ),
        )

    id = int(request.match_info["booking_id"])
    server_data = await get_server_data(request.app)

    try:
        booking = server_data["id_to_booking"][id]
    except KeyError:
        return web.Response(
            text=f"Booking id {id} doesn't exist.",
            status=HTTPStatus.NOT_FOUND,
        )

    if booking["info"]["status"] == BookingStatus.CANCELLED:
        return web.Response(
            status=HTTPStatus.UNPROCESSABLE_ENTITY,
            text=f"Booking with id {booking['id']} was already cancelled.",
        )

    if booking["info"]["status"] == BookingStatus.FINISHED:
        return web.Response(
            status=HTTPStatus.UNPROCESSABLE_ENTITY,
            text=f"Booking with id {booking['id']} was already finished.",
        )

    resources = server_data["resources"]
    bookings = server_data["bookings"]

    action = BookingUpdateAction[requested_action.upper()]
    return action.updater(booking, resources, bookings)


app = web.Application()
app.add_routes(
    [
        web.get("/booking/all", get_bookings),
        web.get("/bookings", get_bookings),
        web.post("/booking", new_booking),
        web.post("/booking/{booking_id}/{action}", booking_update),
        web.get("/booking/before/{booking_id}", unimplemented),
        web.get("/booking/{booking_id}", get_booking),
        web.post("/resource", new_resource),
        web.delete("/resource", unimplemented),
        web.get("/resource/all", get_resources),
        web.get("/resources", get_resources),
    ]
)


def dumpable_booking(
    booking: Booking,
) -> DumpableBooking:
    return {
        "info": booking["info"],
        "used": booking["used"]["info"] if booking["used"] else None,
    }


def dumpable_bookings(
    bookings: List[Booking],
) -> List[DumpableBooking]:
    return [dumpable_booking(booking) for booking in bookings]


def dumpable_resource(resource: Resource) -> DumpableResource:
    return {
        "info": resource["info"],
        "used_by": (
            resource["used_by"]["info"] if resource["used_by"] else None
        ),
    }


def dumpable_resources(resources: List[Resource]) -> List[DumpableResource]:
    return [dumpable_resource(resource) for resource in resources]


def dumpable_server_data(
    server_data: ServerData,
) -> DumpableServerData:
    bookings = server_data["bookings"]
    resources = server_data["resources"]

    return {
        "bookings": dumpable_bookings(bookings),
        "booking_id_counter": server_data["booking_id_counter"],
        "id_to_booking": {
            id: dumpable_booking(booking)
            for id, booking in enumerate(bookings)
        },
        "resources": dumpable_resources(resources),
    }


async def periodic_cleanup(server_data: ServerData):
    # TODO: Implement
    # TODO: Could be also ran from endpoint handlers when lists get too big
    while True:
        print("I could clean something, but here is current server data")

        import copy

        dumpable = dumpable_server_data(copy.deepcopy(server_data))
        print(json.dumps(dumpable, indent=2))

        await asyncio.sleep(5)


initial_server_data: ServerData = {
    "booking_id_counter": 0,
    "bookings": [],
    "resources": [],
    "id_to_booking": {},
}
app["server_data"] = initial_server_data

loop = asyncio.get_event_loop()
loop.create_task(periodic_cleanup(initial_server_data))


def main():
    web.run_app(app, loop=loop)


if __name__ == "__main__":
    main()
