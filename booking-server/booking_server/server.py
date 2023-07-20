from __future__ import annotations

import asyncio
import json
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


class BookingStatus(str, Enum):
    CANCELLED = "CANCELLED"
    FINISHED = "FINISHED"
    WAITING = "WAITING"
    ON = "ON"


class Resource(TypedDict):
    type: str
    identifier: str
    used_by: None | Booking


class Booking(TypedDict):
    name: str
    id: int
    requested: RequestedResource
    booking_time: str
    status: BookingStatus


class ServerData(TypedDict):
    booking_id_counter: int
    bookings: List[Booking]
    resources: List[Resource]
    id_to_booking: Dict[int, Booking]


class BookingRequest(TypedDict):
    name: str
    resource: RequestedResource


async def get_server_data(application: Application):
    server_data: ServerData = application["server_data"]
    return server_data


async def validate_resource(resource: Dict) -> Resource:
    # TODO: Proper error reporting mechanism
    # TODO: Generic TypedDict validation function
    return {
        "identifier": resource["identifier"],
        "type": resource["type"],
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
        if resource["type"] != requested["type"]:
            continue

        if (
            resource["identifier"] != requested["identifier"]
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
        "id": booking_id,
        "name": booking_request["name"],
        "requested": booking_request["resource"],
        "booking_time": datetime.now(timezone.utc).isoformat(
            timespec="seconds"
        ),
        "status": BookingStatus.ON if free_resource else BookingStatus.WAITING,
    }

    if free_resource is not None:
        free_resource["used_by"] = booking
        # TODO: Send notification to client

    server_data["bookings"].append(booking)
    server_data["id_to_booking"][booking_id] = booking

    return web.json_response(booking)


async def unimplemented(_: Request):
    return web.Response(
        text="This endpoint is not yet implemented.",
        status=HTTPStatus.NOT_IMPLEMENTED,
    )


async def new_resource(request: Request):
    resource = await validate_resource(await request.json())

    # TODO: Check for existing resources with same identifier
    (await get_server_data(request.app))["resources"].append(resource)

    # TODO: Check if that resource can be assigned to some booking

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

        if candidate_booking["id"] != booking["id"]:
            continue

        return resource

    raise RuntimeError(
        f"Didn't find resource for booking (id={booking['id']}) that had"
        f" status {booking['status']}"
    )


def cancel_booking(booking: Booking, _: List[Resource], _2: List[Booking]):
    if booking["status"] == BookingStatus.ON:
        return web.Response(
            status=HTTPStatus.UNPROCESSABLE_ENTITY,
            text=(
                f"Booking with id {booking['id']} had already resource"
                " assigned to it. Did you mean to"
                " /booking/{booking_id}/finish the booking?"
            ),
        )

    booking["status"] = BookingStatus.CANCELLED

    return web.Response()


def find_booking_for_resource(resource: Resource, bookings: List[Booking]):
    for booking in bookings:
        requested = booking["requested"]
        if booking["status"] != BookingStatus.WAITING:
            continue
        if requested["type"] != resource["type"]:
            continue
        if (
            resource["identifier"] != requested["identifier"]
            and requested["identifier"] is not None
        ):
            continue

        return booking

    return None


def finish_booking(
    booking: Booking, resources: List[Resource], bookings: List[Booking]
):
    if booking["status"] == BookingStatus.WAITING:
        return web.Response(
            status=HTTPStatus.UNPROCESSABLE_ENTITY,
            text=(
                f"Booking with id {booking['id']} was still waiting for"
                " resource to be assigned to it. Did you mean to"
                " /booking/{booking_id}/cancel the booking?"
            ),
        )

    booked_resource: Resource = find_resource_by_booking(resources, booking)
    booked_resource["used_by"] = None
    booking["status"] = BookingStatus.FINISHED

    candidate_booking = find_booking_for_resource(booked_resource, bookings)

    if candidate_booking is not None:
        candidate_booking["status"] = BookingStatus.ON
        booked_resource["used_by"] = candidate_booking

    return web.Response()


class BookingUpdateAction(Enum):
    def __init__(self, action_name, updater):
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

    # TODO: Error response for non existing booking_id
    booking = server_data["id_to_booking"][id]

    if booking["status"] == BookingStatus.CANCELLED:
        return web.Response(
            status=HTTPStatus.UNPROCESSABLE_ENTITY,
            text=f"Booking with id {booking['id']} was already cancelled.",
        )

    if booking["status"] == BookingStatus.FINISHED:
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


async def periodic_cleanup(server_data: ServerData):
    # TODO: Implement
    # TODO: Could be also ran from endpoint handlers when lists get too big
    while True:
        print("I could clean something, but here is current server data")
        print(json.dumps(server_data, indent=2))

        await asyncio.sleep(2)


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
