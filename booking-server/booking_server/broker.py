from booking_server.booking import Booking, BookingStatus
from booking_server.resource import Resource


async def try_assigning_new_resource(
    booking: Booking, resources: list[Resource]
):
    # TODO: What if booking was deleted from server data before this is ran
    if booking.info.status != BookingStatus.WAITING:
        return

    requested = booking.info.requested

    # TODO: Move searching logic to resource.py
    for resource in resources:
        if resource.info.type != requested.type:
            continue

        if (
            resource.info.identifier != requested.identifier
            and requested.identifier is not None
        ):
            continue

        if resource.used_by is not None:
            continue

        resource.used_by = booking
        booking.used_resource = resource
        booking.info.status = BookingStatus.ON

        # TODO: Send notification to client

        return

    return


async def try_assigning_to_booking(
    resource: Resource, bookings: list[Booking]
):
    # TODO: What if resource is deleted before this runs?

    # TODO: Move searching logic to booking.py
    for booking in bookings:
        requested = booking.info.requested
        if booking.info.status != BookingStatus.WAITING:
            continue
        if requested.type != resource.info.type:
            continue
        if (
            requested.identifier != resource.info.identifier
            and requested.identifier is not None
        ):
            continue

        booking.info.status = BookingStatus.ON
        booking.used_resource = resource
        resource.used_by = booking

        # TODO: Send notification to client

        return
