from typing import List

from booking_server.booking import BookingStatus
from booking_server.types import Booking, Resource


async def try_assigning_to_booking(
    resource: Resource, bookings: List[Booking]
):
    # TODO: What if resource is deleted before this runs?

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

        # TODO: Send notification to client

        return


async def try_assigning_new_resource(
    booking: Booking, resources: List[Resource]
):
    if booking["info"]["status"] != BookingStatus.WAITING:
        return

    requested = booking["info"]["requested"]

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

        resource["used_by"] = booking
        booking["used"] = resource
        booking["info"]["status"] = BookingStatus.ON

        # TODO: Send notification to client

        return

    return
