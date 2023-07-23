from __future__ import annotations

from http import HTTPStatus

from booking_server.booking import (
    Booking,
    BookingStatus,
    DumpableBooking,
    NewBooking,
    add_new_booking,
    dumpable_booking,
    dumpable_bookings,
)
from booking_server.broker import (
    try_assigning_new_resource,
    try_assigning_to_booking,
)
from booking_server.exceptions import AlreadyExistingId
from booking_server.resource import (
    DumpableResource,
    NewResource,
    add_new_resource,
    dumpable_resources,
)
from booking_server.server import AppRequest, fire_and_forget
from fastapi import APIRouter
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse, Response

router = APIRouter()


@router.post("/resource", status_code=HTTPStatus.CREATED)
async def post_resource(new_resource: NewResource, request: AppRequest):
    server_state = request.app.server_state

    try:
        resource = await add_new_resource(new_resource, server_state)
    except AlreadyExistingId as exception:
        return Response(
            status_code=HTTPStatus.CONFLICT, content=exception.message
        )

    fire_and_forget(
        request.app, try_assigning_to_booking(resource, server_state.bookings)
    )

    return Response(status_code=HTTPStatus.CREATED)


@router.post(
    "/booking", response_model=Booking, status_code=HTTPStatus.CREATED
)
async def post_booking(new_booking: NewBooking, request: AppRequest):
    server_state = request.app.server_state

    booking = await add_new_booking(new_booking, server_state)

    fire_and_forget(
        request.app,
        try_assigning_new_resource(booking, server_state.resources),
    )

    return JSONResponse(
        jsonable_encoder(await dumpable_booking(booking)), HTTPStatus.CREATED
    )


@router.get(
    "/booking/{booking_id}",
    response_model=DumpableBooking,
    status_code=HTTPStatus.OK,
)
async def get_booking_by_id(booking_id: int, request: AppRequest):
    try:
        booking = request.app.server_state.ids_to_bookings[booking_id]
    except KeyError:
        return Response(
            f"Booking id {booking_id} doesn't exists.",
            status_code=HTTPStatus.NOT_FOUND,
        )

    return JSONResponse(
        content=jsonable_encoder(await dumpable_booking(booking))
    )


@router.get(
    "/resource/all",
    response_model=list[DumpableResource],
    status_code=HTTPStatus.OK,
)
async def get_all_resources(
    request: AppRequest,
):
    resources = request.app.server_state.resources

    return JSONResponse(
        content=jsonable_encoder(await dumpable_resources(resources))
    )


@router.get(
    "/booking/all",
    response_model=list[Booking],
    status_code=HTTPStatus.OK,
)
async def get_all_bookings(
    request: AppRequest,
):
    bookings = request.app.server_state.bookings

    return JSONResponse(
        content=jsonable_encoder(await dumpable_bookings(bookings))
    )


@router.post("/booking/{booking_id}/finish", status_code=HTTPStatus.OK)
async def post_finish_booking(booking_id: int, request: AppRequest):
    server_state = request.app.server_state

    try:
        booking = server_state.ids_to_bookings[booking_id]
    except KeyError:
        return Response(
            content=f"Booking id {booking_id} doesn't exist.",
            status_code=HTTPStatus.NOT_FOUND,
        )

    if booking.info.status == BookingStatus.CANCELLED:
        return Response(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
            content=(
                f"Booking with id {booking.info.id} was already cancelled."
            ),
        )

    if booking.info.status == BookingStatus.FINISHED:
        return Response(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
            content=f"Booking with id {booking.info.id} was already finished.",
        )

    if booking.info.status == BookingStatus.WAITING:
        return Response(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
            content=(
                f"Booking with id {booking.info.id} was still waiting"
                " for resource to be assigned to it. Did you mean to"
                " /booking/{booking_id}/cancel the booking?"
            ),
        )

    freed_resource = booking.used_resource
    if freed_resource is None:
        raise RuntimeError(
            "Booking didn't have resource even when it should have."
        )

    freed_resource.used_by = None
    booking.info.status = BookingStatus.FINISHED

    bookings = server_state.bookings
    fire_and_forget(
        request.app, try_assigning_to_booking(freed_resource, bookings)
    )

    return Response(content=f"Booking id {booking_id} finished.")


@router.post(
    "/booking/{booking_id}/cancel",
    status_code=HTTPStatus.OK,
)
async def post_cancel_booking(booking_id: int, request: AppRequest):
    server_state = request.app.server_state

    try:
        booking = server_state.ids_to_bookings[booking_id]
    except KeyError:
        return Response(
            content=f"Booking id {booking_id} doesn't exist.",
            status_code=HTTPStatus.NOT_FOUND,
        )

    if booking.info.status == BookingStatus.CANCELLED:
        return Response(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
            content=(
                f"Booking with id {booking.info.id} was already cancelled."
            ),
        )

    if booking.info.status == BookingStatus.FINISHED:
        return Response(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
            content=f"Booking with id {booking.info.id} was already finished.",
        )

    if booking.info.status == BookingStatus.ON:
        return Response(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
            content=(
                f"Booking with id {booking.info.id} had already resource"
                " assigned to it. Did you mean to"
                " /booking/{booking_id}/finish the booking?"
            ),
        )

    booking.info.status = BookingStatus.CANCELLED

    return Response(content=f"Booking id {booking_id} cancelled.")


# TODO: Add /booking/extend
