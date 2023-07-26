from __future__ import annotations

from asyncio import Event
from datetime import datetime, timezone
from enum import Enum
from typing import TYPE_CHECKING

from booking_server.resource import DumpableResource, Resource, ResourceInfo
from pydantic import BaseModel, ConfigDict, Field

if TYPE_CHECKING:
    from booking_server.server import ServerState


class BookingStatus(str, Enum):
    CANCELLED = "CANCELLED"
    FINISHED = "FINISHED"
    WAITING = "WAITING"
    ON = "ON"


class RequestedResource(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: str = Field(examples=["big_machine"])
    identifier: None | str = Field(examples=["floor_3"], default=None)

    model_config = ConfigDict(extra="forbid")


class JobInfo(BaseModel):
    model_config = ConfigDict(extra="forbid")

    job_id: int = Field(examples=[15367862127])
    repo_owner: str = Field(examples=["JoakimJoensuu"])
    repo_name: str = Field(examples=["resource-booking-gh-runner"])


class NewBooking(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(examples=["Some One"])
    resource: RequestedResource
    github: JobInfo | None = None


class BookingInfo(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    id: int
    resource: RequestedResource
    booking_time: datetime
    status: BookingStatus
    github: JobInfo | None = None


class Booking(BaseModel):
    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)

    info: BookingInfo
    used_resource: None | Resource = None
    event: Event = Event()
    # Add optional booking time
    # Add priviledged client compared to workflow
    # Add callback address to trigger workflows later


class DumpableBooking(BaseModel):
    model_config = ConfigDict(extra="forbid")

    info: BookingInfo
    used_resource: ResourceInfo | None


DumpableResource.model_rebuild()
ResourceInfo.model_rebuild()
Resource.model_rebuild()


async def dumpable_booking(
    booking: Booking,
):
    used_resource = (
        booking.used_resource.info if booking.used_resource else None
    )
    return DumpableBooking(info=booking.info, used_resource=used_resource)


async def dumpable_bookings(
    bookings: list[Booking],
):
    return [await dumpable_booking(booking) for booking in bookings]


async def dumpable_ids_to_bookings(ids_to_bookings: dict[int, Booking]):
    return {
        id: await dumpable_booking(booking)
        for id, booking in ids_to_bookings.items()
    }


async def add_new_booking(new_booking: NewBooking, server_state: ServerState):
    booking_id = server_state.booking_id_counter
    server_state.booking_id_counter += 1

    booking = Booking(
        info=BookingInfo(
            status=BookingStatus.WAITING,
            id=booking_id,
            **new_booking.model_dump(),
            booking_time=datetime.now(timezone.utc),
        )
    )

    server_state.bookings.append(booking)
    server_state.ids_to_bookings.update({booking_id: booking})

    return booking


def find_waiting_booking(resource: Resource, bookings: list[Booking]):
    for booking in bookings:
        if booking.info.status != BookingStatus.WAITING:
            continue

        requested_resource = booking.info.resource
        if requested_resource.type != resource.info.type:
            continue
        if (
            requested_resource.identifier != resource.info.identifier
            and requested_resource.identifier is not None
        ):
            continue

        return booking
    return None
