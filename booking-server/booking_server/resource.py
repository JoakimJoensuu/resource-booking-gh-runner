from __future__ import annotations

from typing import TYPE_CHECKING

from booking_common.models import BookingInfo, RequestedResource, ResourceInfo
from booking_server.exceptions import AlreadyExistingId
from pydantic import BaseModel, ConfigDict, Field

if TYPE_CHECKING:
    from booking_server.booking import Booking
    from booking_server.server import ServerState


class Resource(BaseModel):
    model_config = ConfigDict(extra="forbid")

    info: ResourceInfo
    used_by: None | Booking = None


class NewResource(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: str = Field(examples=["big_machine"])
    identifier: str = Field(examples=["floor_3"])


class DumpableResource(BaseModel):
    model_config = ConfigDict(extra="forbid")

    info: ResourceInfo
    used_by: BookingInfo | None


async def dumpable_resource(resource: Resource):
    used_by = resource.used_by.info if resource.used_by else None
    return DumpableResource(info=resource.info, used_by=used_by)


async def dumpable_resources(
    resources: list[Resource],
):
    return [await dumpable_resource(resource) for resource in resources]


async def dumpable_ids_to_resources(ids_to_resources: dict[str, Resource]):
    return {
        id: await dumpable_resource(booking)
        for id, booking in ids_to_resources.items()
    }


async def add_new_resource(
    new_resource: NewResource,
    server_state: ServerState,
):
    if new_resource.identifier in server_state.ids_to_resources:
        raise AlreadyExistingId(
            f"Resource with identifier {new_resource.identifier} already"
            " exists."
        )

    resource = Resource(info=ResourceInfo(**new_resource.model_dump()))

    server_state.resources.append(resource)
    server_state.ids_to_resources.update({resource.info.identifier: resource})

    return resource


def find_free_resource(
    requested: RequestedResource, resources: list[Resource]
):
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

        return resource
    return None
