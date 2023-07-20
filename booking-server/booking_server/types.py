from __future__ import annotations

from typing import TYPE_CHECKING, Dict, List, TypedDict

if TYPE_CHECKING:
    from booking_server.booking import BookingStatus


class RequestedResource(TypedDict):
    type: str
    identifier: None | str


class BookingRequest(TypedDict):
    name: str
    resource: RequestedResource


class ResourceInfo(TypedDict):
    type: str
    identifier: str
    # TODO: Allow adding arbitrary commands to be ran when resource is reserved or freed

class BookingInfo(TypedDict):
    name: str
    id: int
    requested: RequestedResource
    booking_time: str
    status: BookingStatus


class Resource(TypedDict):
    info: ResourceInfo
    used_by: None | Booking


class Booking(TypedDict):
    info: BookingInfo
    used: None | Resource
    # Add optional booking time

class DumpableResource(TypedDict):
    info: ResourceInfo
    used_by: BookingInfo | None


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
