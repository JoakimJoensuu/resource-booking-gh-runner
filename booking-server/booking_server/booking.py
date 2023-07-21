from __future__ import annotations

from enum import Enum
from typing import Dict, List, TypedDict

from booking_server.resource import RequestedResource, Resource, ResourceInfo


class BookingStatus(str, Enum):
    CANCELLED = "CANCELLED"
    FINISHED = "FINISHED"
    WAITING = "WAITING"
    ON = "ON"


class BookingInfo(TypedDict):
    name: str
    id: int
    requested: RequestedResource
    booking_time: str
    status: BookingStatus


class Booking(TypedDict):
    info: BookingInfo
    used: None | Resource
    # Add optional booking time
    # Add priviledged client compared to workflow


class DumpableBooking(TypedDict):
    info: BookingInfo
    used: ResourceInfo | None


class BookingRequest(TypedDict):
    name: str
    resource: RequestedResource


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


async def dumpable_booking(
    booking: Booking,
) -> DumpableBooking:
    return {
        "info": booking["info"],
        "used": booking["used"]["info"] if booking["used"] else None,
    }


async def dumpable_bookings(
    bookings: List[Booking],
) -> List[DumpableBooking]:
    return [await dumpable_booking(booking) for booking in bookings]
