from booking_server.booking import Booking, BookingStatus, find_waiting_booking
from booking_server.resource import Resource, find_free_resource


def assign_to_each_others(resource: Resource, booking: Booking):
    booking.info.status = BookingStatus.ON
    booking.used_resource = resource
    resource.used_by = booking
    booking.event.set()
    booking.event.clear()


async def try_assigning_new_resource(
    booking: Booking, resources: list[Resource]
):
    # TODO: What if booking was deleted from server data before this is
    # ran and this still holds the reference to the object

    if booking.info.status != BookingStatus.WAITING:
        return

    requested = booking.info.resource

    resource = find_free_resource(requested, resources)

    if resource is None:
        return

    assign_to_each_others(resource, booking)

    # TODO: Send notification to client


async def try_assigning_to_booking(
    resource: Resource, bookings: list[Booking]
):
    # TODO: What if resource is deleted before this runs and this still
    # holds the reference to the object

    if resource.used_by is not None:
        return

    booking = find_waiting_booking(resource, bookings)

    if booking is None:
        return

    assign_to_each_others(resource, booking)

    # TODO: Send notification to client
