import asyncio
from datetime import datetime, timezone
from http import HTTPStatus

from aiohttp import web
from aiohttp.web_request import Request
from booking_server.booking import BookingStatus, BookingUpdateAction
from booking_server.broker import (
    try_assigning_new_resource,
    try_assigning_to_booking,
)
from booking_server.server import get_server_data
from booking_server.types import (
    Booking,
    dumpable_booking,
    validate_booking_request,
    validate_resource,
)


async def new_booking(request: Request):
    server_data = await get_server_data(request.app)
    booking_id = server_data["booking_id_counter"]
    server_data["booking_id_counter"] += 1

    booking_request = await validate_booking_request(await request.json())

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

    asyncio.create_task(
        try_assigning_new_resource(booking, server_data["resources"])
    )

    return web.json_response(dumpable_booking(booking))


async def unimplemented(_: Request):
    return web.Response(
        text="This endpoint is not yet implemented.",
        status=HTTPStatus.NOT_IMPLEMENTED,
    )


async def new_resource(request: Request):
    resource = await validate_resource(await request.json())

    server_data = await get_server_data(request.app)

    # TODO: Check for existing resources with same identifier
    server_data["resources"].append(resource)

    asyncio.create_task(
        try_assigning_to_booking(resource, server_data["bookings"])
    )

    return web.Response()


async def get_resources(request: Request):
    return web.json_response((await get_server_data(request.app))["resources"])


async def get_booking(request: Request):
    booking_id = int(request.match_info["booking_id"])
    server_data = await get_server_data(request.app)

    # TODO: Proper response for non existing booking
    return web.json_response(server_data["id_to_booking"][booking_id])


async def get_bookings(request: Request):
    return web.json_response((await get_server_data(request.app))["bookings"])


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

    booking_id = int(request.match_info["booking_id"])
    server_data = await get_server_data(request.app)

    try:
        booking = server_data["id_to_booking"][booking_id]
    except KeyError:
        return web.Response(
            text=f"Booking id {booking_id} doesn't exist.",
            status=HTTPStatus.NOT_FOUND,
        )

    if booking["info"]["status"] == BookingStatus.CANCELLED:
        return web.Response(
            status=HTTPStatus.UNPROCESSABLE_ENTITY,
            text=(
                f"Booking with id {booking['info']['id']} was already"
                " cancelled."
            ),
        )

    if booking["info"]["status"] == BookingStatus.FINISHED:
        return web.Response(
            status=HTTPStatus.UNPROCESSABLE_ENTITY,
            text=(
                f"Booking with id {booking['info']['id']} was already"
                " finished."
            ),
        )

    bookings = server_data["bookings"]

    action = BookingUpdateAction[requested_action.upper()]
    # TODO: Move web.Response construction here
    return action.updater(booking, bookings)
    # TODO: Move usage of function for assigning resource to othee booking here
