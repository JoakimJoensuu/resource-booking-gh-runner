import asyncio
from copy import deepcopy
from http import HTTPStatus
from typing import List

from aiohttp import web
from aiohttp.web_request import Request
from aiohttp.web_routedef import RouteDef
from booking_server.booking import (
    BookingStatus,
    dumpable_booking,
    validate_booking_request,
)
from booking_server.broker import (
    try_assigning_new_resource,
    try_assigning_to_booking,
)
from booking_server.resource import validate_resource
from booking_server.server import add_new_booking, get_server_data


async def post_booking(request: Request):
    server_data = await get_server_data(request.app)
    booking_request = await validate_booking_request(await request.json())

    booking = await add_new_booking(booking_request, server_data)

    asyncio.create_task(
        try_assigning_new_resource(booking, server_data["resources"])
    )

    return web.json_response(await dumpable_booking(deepcopy(booking)))


async def unimplemented(_: Request):
    return web.Response(
        text="This endpoint is not yet implemented.",
        status=HTTPStatus.NOT_IMPLEMENTED,
    )


async def post_resource(request: Request):
    resource = await validate_resource(await request.json())

    server_data = await get_server_data(request.app)

    # TODO: Check for existing resources with same identifier use HTTP 409 Conflict

    server_data["resources"].append(resource)

    asyncio.create_task(
        try_assigning_to_booking(resource, server_data["bookings"])
    )

    return web.Response()


async def get_resource_all(request: Request):
    return web.json_response((await get_server_data(request.app))["resources"])


async def get_booking_id(request: Request):
    booking_id = int(request.match_info["booking_id"])
    server_data = await get_server_data(request.app)

    # TODO: Proper response for non existing booking
    return web.json_response(server_data["id_to_booking"][booking_id])


async def get_booking_all(request: Request):
    return web.json_response((await get_server_data(request.app))["bookings"])


async def post_booking_id_finish(request: Request):
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

    bookings = server_data["bookings"]
    asyncio.create_task(try_assigning_to_booking(freed_resource, bookings))

    return web.Response()


async def post_booking_id_cancel(request: Request):
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


# TODO: Add /booking/extend
routes: List[RouteDef] = [
    web.get("/booking/all", get_booking_all),
    web.get("/bookings", get_booking_all),
    web.post("/booking", post_booking),
    web.post("/booking/{booking_id}/finish", post_booking_id_finish),
    web.post("/booking/{booking_id}/cancel", post_booking_id_cancel),
    web.get("/booking/before/{booking_id}", unimplemented),
    web.get("/booking/{booking_id}", get_booking_id),
    web.post("/resource", post_resource),
    web.delete("/resource", unimplemented),
    web.get("/resource/all", get_resource_all),
    web.get("/resources", get_resource_all),
]
